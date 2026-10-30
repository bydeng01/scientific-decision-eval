"""Five-model extension contracts, with all networking disabled."""
import copy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from common import BASE, ROOT, loads, read, sha
from dataset import bundle, load_inputs
from providers import INSTRUCTIONS, ResponseError, parse_response, request_body, usage_record
import run


class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read(BASE/'config.json')
        cls.groups = load_inputs()
        cls.models = cls.config['models']
        cls.packet, _ = bundle(next(g for g in cls.groups if g['group_id'] == 'B002'))
        cls.network = patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden'))
        cls.network.start()

    @classmethod
    def tearDownClass(cls):
        cls.network.stop()

    def response(self, model):
        return loads(run.fake_transport(model, self.packet, 0)['raw_body'])

    def test_exact_extension_roster_and_matrix(self):
        self.assertEqual([m['id'] for m in self.models],
                         ['qwen_flash','qwen_max','deepseek_flash','deepseek_pro','opus5'])
        matrix = run.matrix(self.groups, self.config)
        self.assertEqual((matrix['requests'], matrix['semantic_answers']), (250,500))
        self.assertEqual(len({j['job_id'] for j in matrix['jobs']}), 250)
        self.assertEqual(len({j['model_id'] for j in matrix['jobs'][:5]}), 5)
        self.assertIsNone(self.config['budget']['cap_usd'])
        self.assertEqual(self.config['max_retries'], 0)

    def test_fixed_routes_and_explicit_parameters(self):
        catalog = read(BASE/'provider_catalog.json')
        for model in self.models:
            body = request_body(model, self.packet)
            self.assertNotIn('temperature', body)
            self.assertNotIn('tools', body)
            if model['provider'] == 'openrouter_chat':
                self.assertEqual(body['provider'], {'only':[model['provider_slug']],
                                                   'allow_fallbacks':False,'require_parameters':True})
                self.assertEqual(body['reasoning']['effort'], model['reasoning_effort'])
                self.assertTrue(body['response_format']['json_schema']['strict'])
                entry = next(r for r in catalog['rows'] if r['requested_model'] == model['model'])
                endpoint = next(e for e in entry['response']['data']['endpoints'] if e['tag'] == model['provider_slug'])
                self.assertGreaterEqual(endpoint['max_completion_tokens'], body['max_tokens'])
                self.assertIn('structured_outputs', endpoint['supported_parameters'])
            else:
                self.assertEqual(body['thinking'], {'type':'adaptive'})
                self.assertEqual(body['output_config']['effort'], 'medium')

    def test_same_packets_and_question_mapping_as_original_run(self):
        old = read(ROOT/'results/s2-execution-live-v1/plan.json')
        old_packets = {j['group_id']:(j['packet'],j['question_map']) for j in old['jobs']}
        for job in run.matrix(self.groups, self.config)['jobs']:
            self.assertEqual((job['packet'],job['question_map']), old_packets[job['group_id']])
        for model in self.models:
            body = request_body(model,self.packet)
            message = body['messages'][-1]['content']
            self.assertEqual(loads(message),self.packet)
            self.assertEqual(body.get('system', body['messages'][0]['content']), INSTRUCTIONS)

    def test_new_requests_exclude_evaluation_metadata(self):
        original = Path.read_text
        def guarded(path,*args,**kwargs):
            if path.name in {'evaluation.json','review_decisions.json','source_revisions.json','references.json'}:
                raise AssertionError('Reference read during request assembly')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',guarded):
            groups = load_inputs()
            for g in groups:
                g['reference_option']='REFERENCE_TEST_MARKER'
                if g['problem']:
                    g['problem']['expected_code_output']='DERIVED_TEST_MARKER'
            matrix = run.matrix(groups,self.config)
        self.assertNotIn('REFERENCE_TEST_MARKER',json.dumps(matrix))
        self.assertNotIn('DERIVED_TEST_MARKER',json.dumps(matrix))

    def test_valid_responses_and_service_identity(self):
        for model in self.models:
            response=self.response(model)
            self.assertFalse(parse_response(model,self.packet,response)['errors'])
            response['model']='unapproved'
            with self.assertRaisesRegex(ResponseError,'model_version'):parse_response(model,self.packet,response)
            if model['provider']=='openrouter_chat':
                response=self.response(model);response['provider']='unapproved'
                with self.assertRaisesRegex(ResponseError,'provider_mismatch'):parse_response(model,self.packet,response)

    def test_partial_invalid_refused_and_truncated_chat(self):
        m=self.models[0];obj=self.response(m);message=obj['choices'][0]['message']
        message['content']='{"q1":"shared_then_separate"}'
        parsed=parse_response(m,self.packet,obj)
        self.assertEqual(parsed['errors'],{'q2':'missing_answer'})
        self.assertEqual(parsed['answers'],{'q1':'shared_then_separate'})
        message['content']='{"q1":null,"q2":"not-a-choice"}'
        self.assertEqual(set(parse_response(m,self.packet,obj)['errors'].values()),{'invalid_option'})
        message['content']='{"q1":"shared_then_separate","q1":"other"}'
        with self.assertRaises(ValueError):parse_response(m,self.packet,obj)
        obj=self.response(m);obj['choices'][0]['finish_reason']='length'
        with self.assertRaisesRegex(ResponseError,'incomplete'):parse_response(m,self.packet,obj)
        obj=self.response(m);obj['choices'][0]['message']['refusal']='fixture'
        with self.assertRaisesRegex(ResponseError,'refusal'):parse_response(m,self.packet,obj)
        obj=self.response(m);obj['choices'][0]['message']['tool_calls']=[{}]
        with self.assertRaisesRegex(ResponseError,'unexpected_tool'):parse_response(m,self.packet,obj)

    def test_usage_field_corrections_and_unknown_charges(self):
        old=read(BASE/'regression_config.json')['models'][1]
        u=usage_record(old,{'usage':{'input_tokens':1000,'output_tokens':100,
             'input_tokens_details':{'cached_tokens':200,'cache_write_tokens':100},
             'output_tokens_details':{'reasoning_tokens':40}}})
        self.assertEqual(u['cache_creation_tokens'],100)
        self.assertAlmostEqual(u['usage_cost_estimate_usd'],(700*.2+200*.02+100*.25+100*1.2)/1e6)
        self.assertIsNone(u['reported_cost_usd'])
        u=usage_record(self.models[-1],{'usage':{'input_tokens':1000,'output_tokens':100,
            'cache_creation_input_tokens':0,'cache_read_input_tokens':0,
            'output_tokens_details':{'thinking_tokens':40}}})
        self.assertEqual(u['reasoning_tokens'],40)
        self.assertAlmostEqual(u['usage_cost_estimate_usd'],.0075)
        u=usage_record(self.models[0],{'usage':{'prompt_tokens':1000,'completion_tokens':100,
            'prompt_tokens_details':{'cached_tokens':200,'cache_write_tokens':100},
            'completion_tokens_details':{'reasoning_tokens':40},'cost':.0002}})
        self.assertEqual((u['input_tokens'],u['output_tokens'],u['reasoning_tokens']),(1000,100,40))
        self.assertEqual(u['reported_cost_usd'],.0002)
        u=usage_record(self.models[0],{'usage':{'prompt_tokens':1000,'completion_tokens':100}})
        self.assertIsNone(u['cache_creation_tokens'])
        self.assertIsNone(u['reported_cost_usd'])
        self.assertIsNone(u['usage_cost_estimate_usd'])

    def test_full_extension_dry_run_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run'
            run.prepare(out,mode='dry-run')
            first=run.execute(out)
            self.assertEqual(first['new_attempts'],250)
            hashes={str(p):sha(p) for p in (out/'attempts').rglob('*.json')}
            second=run.execute(out)
            self.assertEqual(second['new_attempts'],0)
            self.assertEqual(hashes,{str(p):sha(p) for p in (out/'attempts').rglob('*.json')})
            self.assertIsNone(read(Path(second['report']))['model_scores'])
            self.assertEqual(len(run.validate_attempts(out)),250)


if __name__=='__main__':
    unittest.main(verbosity=2)
