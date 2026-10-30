"""Offline behavioral checks. All network connections are prohibited."""
import copy
from functools import partial
import itertools
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from common import BASE, OLD, ROOT, digest, loads, read, sha, write_new
from dataset import bundle, inventory, load_inputs
from derive import derive, zero_answers
from providers import ResponseError, parse_response, request_body, usage_record
import run
from scoring import expected_projection, load_references, oracle, projection, score_lane


class ExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = load_inputs()
        cls.g = {g['group_id']: g for g in cls.groups}
        cls.config = read(BASE/'regression_config.json')
        cls.preparation = patch.object(run, 'prepare', partial(run.prepare, config_path=BASE/'regression_config.json'))
        cls.preparation.start()
        cls.refs = load_references(cls.groups)
        cls.network = patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden in offline tests'))
        cls.network.start()

    @classmethod
    def tearDownClass(cls):
        cls.preparation.stop()
        cls.network.stop()

    def answers(self, gid):
        return {q['question_id']: self.refs['answers'][q['question_id']] for q in self.g[gid]['questions']}

    def prep(self, path, mode='dry-run'):
        return run.prepare(path, mode=mode)

    def test_full_inventory_and_subset(self):
        i = inventory(self.groups)
        self.assertEqual((i['groups'], i['choices'], i['scientific_choices'], i['engineering_choices']), (20,41,40,1))
        self.assertEqual((i['scientific_claims'], i['source_records'], i['source_families']), (25,21,18))
        self.assertEqual((i['recent_independent_review_groups'], i['recent_independent_review_choices']), (10,18))
        self.assertEqual(i['route_choices'], {'code':21,'model':20})
        self.assertEqual(i['route_groups'], {'code':10,'model':10})
        self.assertEqual(len({r['question_id'] for r in i['rows']}),41)

    def test_reference_files_are_not_read_by_input_assembly(self):
        original = Path.read_text
        def guarded(path, *args, **kwargs):
            if path.name in {'evaluation.json','review_decisions.json','source_revisions.json','references.json'}:
                raise AssertionError('Reference read during assembly')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',guarded):
            groups = load_inputs()
            matrix = run.matrix(groups,self.config)
            run.run_code(groups)
        self.assertEqual(matrix['requests'],300)

    def test_evaluation_metadata_is_excluded_from_requests(self):
        groups=copy.deepcopy(self.groups)
        for g in groups:
            g['reference_option']='ANSWER_KEY_TEST_MARKER'
            g['review_rationale']='REVIEW_TEST_MARKER'
            g['approved_by_author']=True
            g['author_reviewed_question_ids']=['REVIEW_TEST_MARKER']
            if g['problem']:
                g['problem']['expected_code_output']='DERIVED_TEST_MARKER'
        for g in groups:
            packet,_=bundle(g)
            for m in self.config['models']:
                text=json.dumps(request_body(m,packet))
                self.assertFalse(any(c in text for c in ['ANSWER_KEY_TEST_MARKER','REVIEW_TEST_MARKER','DERIVED_TEST_MARKER']))
                self.assertFalse(any(k in text for k in ['reference_option','expected_code_output','review_status']))

    def test_every_provider_receives_same_evidence_and_options(self):
        packet,_=bundle(self.g['E010'])
        for model in self.config['models']:
            body=request_body(model,packet)
            if model['provider']=='openrouter':
                decoded={k:body[k] for k in ('state','questions')}
                self.assertFalse(body['provider']['allow_fallbacks'])
            elif model['provider']=='openai':
                decoded=loads(body['input'])
                self.assertNotIn('temperature',body)
            else:
                decoded=loads(body['messages'][0]['content'])
            self.assertEqual(decoded,packet)
        self.assertIn('monthly generator-exclusion cells',json.dumps(packet))
        b,_=bundle(self.g['B004'])
        self.assertIn('multiple mutant alleles',json.dumps(b))
        self.assertIn('exact total remains unresolved',json.dumps(b))

    def test_deterministic_schedule_and_no_zero_call_jobs(self):
        a=run.matrix(self.groups,self.config)
        self.assertEqual(a,run.matrix(self.groups,self.config))
        self.assertEqual((a['requests'],a['semantic_answers'],a['max_attempts']),(300,600,300))
        self.assertEqual(len({j['job_id'] for j in a['jobs']}),300)
        self.assertTrue(all(self.g[j['group_id']]['route']=='model' for j in a['jobs']))
        for j in a['jobs']:
            self.assertEqual(j['request_sha256'],digest(j['request']))

    def test_zero_call_answers_and_claims(self):
        rows=run.run_code(self.groups)
        lane={(0,r['group_id']):r for r in rows}
        score=score_lane(self.groups,self.refs,lane,1)
        self.assertEqual(score['zero_call_scientific_choices']['correct'],20)
        self.assertEqual(score['scientific_claims']['exact']['correct'],15)
        self.assertEqual(score['engineering_choices']['correct'],1)
        self.assertEqual(score['scientific_workflow_choices']['denominator'],40)

    def test_zero_rules_reject_added_negation_or_conflict(self):
        for gid in ('E001','E002','E003','E008'):
            g=copy.deepcopy(self.g[gid]);g['problem']['evidence'][0]['text']+=' This account is contradicted.'
            with self.assertRaises(ValueError):zero_answers(g)
        g=copy.deepcopy(self.g['D01']);g['questions'][0]['state']['evidence_text']+=' No prisms share a batch.'
        with self.assertRaises(ValueError):zero_answers(g)

    def test_oracle_matches_all_twenty_groups(self):
        result=oracle(self.groups,self.refs)
        self.assertEqual(result['groups_correct'],20)
        self.assertFalse(result['model_performance'])

    def test_unknown_values_survive_serialization(self):
        paths={'B001':('counts','distinct_F0_ancestors'),'B002':('counts','exact_mutation_origins'),
               'B004':('counts','validated_new_germline_lines'),
               'E002':('output','actual_eligible_application_count'),
               'E004':('output','exact_parent_lot_count'),
               'E009':('output','exact_effective_replication_count')}
        for gid,(a,b) in paths.items():
            value=loads(json.dumps(derive(self.g[gid],self.answers(gid))))
            self.assertIsNone(value[a][b],gid)
        self.assertIsNone(derive(self.g['D03'],self.answers('D03'))['cases']['D03']['count'])

    def test_fallback_precedence_and_partial_identification(self):
        for gid in ('E005','B001','B002','B003','B004'):
            answers=self.answers(gid);q1,q2=list(answers)
            answers[q1]='not_stated';answers[q2]='other'
            self.assertEqual(derive(self.g[gid],answers)['status'],'candidate_completion_required')
            answers[q2]='conflicting'
            self.assertEqual(derive(self.g[gid],answers)['status'],'evidence_conflict')
            answers[q2]='not_stated'
            self.assertEqual(derive(self.g[gid],answers)['status'],'insufficient_evidence')
            self.assertIsNone(derive(self.g[gid],answers)['final_label'])
        self.assertEqual(derive(self.g['E004'],self.answers('E004'))['final_label'],'inconsistent')
        self.assertEqual(derive(self.g['B004'],self.answers('B004'))['final_label'],'inconsistent')

    def test_missing_answers_are_errors_not_not_stated(self):
        for g in self.groups:
            a=self.answers(g['group_id']);a.pop(next(iter(a)))
            with self.assertRaisesRegex(ValueError,'missing_or_extra'):derive(g,a)
            a=self.answers(g['group_id']);a[next(iter(a))]=None
            with self.assertRaisesRegex(ValueError,'invalid_option'):derive(g,a)

    def test_all_option_combinations_are_defined(self):
        for g in self.groups:
            qs=g['questions']
            for options in itertools.product(*(q['question']['criteria'] for q in qs)):
                a=dict(zip([q['question_id'] for q in qs],options))
                self.assertIsInstance(derive(g,a),dict)

    def test_nonoracle_answers_drive_derivation(self):
        a=self.answers('B003');a['B003-Q02']='all_individuals_resolved'
        self.assertEqual(derive(self.g['B003'],a)['counts']['separately_observed_contributor_profiles'],32)
        a=self.answers('E006');a['E006-Q02']='individual_execution'
        self.assertEqual(derive(self.g['E006'],a)['output']['values_entering_pair_ensemble'],200)
        a=self.answers('E009');a['E009-Q01']='independent_reference'
        self.assertEqual(derive(self.g['E009'],a)['output']['shared_covariance_term'],'0')
        a=self.answers('E005');a['E005-Q01']='fixed_level'
        self.assertEqual(derive(self.g['E005'],a)['output']['next_stress_after_initial_failure_MPa'],325)
        g=copy.deepcopy(self.g['B003']);g['problem']['records']['select_pool_size']=3
        self.assertNotEqual(derive(g,self.answers('B003'))['counts']['distinct_contributors'],16)

    def test_nested_reference_fields_are_rejected(self):
        fields = ('expected_option', 'reviewer', 'reviewed_on', 'review_attribution',
                  'approved_by_author', 'author_reviewed_question_ids', 'author_choice_review',
                  'author_review_decision_id', 'author_review_summary_english',
                  'case_content_approved_by_author', 'per_question_author_choice_review',
                  'approved_by_user', 'user_approved_question_ids', 'user_choice_review')
        for field in fields:
            with self.subTest(field=field):
                g=copy.deepcopy(self.g['B001'])
                g['questions'][0]['state']['records']['metadata']=[{field: 'ANNOTATION_TEST_MARKER'}]
                with self.assertRaisesRegex(ValueError,'Reference/review'):bundle(g)

    def test_covariance_substitution_is_exact_code_algebra(self):
        from fractions import Fraction
        for ui,ul,ub in [(2,3,1),(Fraction(5,2),Fraction(7,3),Fraction(1,4)),(4,5,0)]:
            ui,ul,ub=map(Fraction,(ui,ul,ub));r=ub**2/(ui*ul)
            self.assertEqual(2*r*ui*ul,2*ub**2)

    def test_provider_fixtures_and_reasoning_block_selection(self):
        packet,_=bundle(self.g['B001'])
        for model in self.config['models']:
            obj=loads(run.fake_transport(model,packet,0)['raw_body'])
            if model['provider']=='anthropic':obj['content'].insert(0,{'type':'thinking','thinking':'fixture'})
            parsed=parse_response(model,packet,obj)
            self.assertFalse(parsed['errors'])
            self.assertEqual(len(parsed['answers']),2)

    def test_partial_missing_invalid_and_extra_answers(self):
        model=self.config['models'][1];packet,_=bundle(self.g['B001'])
        obj=loads(run.fake_transport(model,packet,0)['raw_body'])
        obj['output'][0]['content'][0]['text']=json.dumps({'q1':next(iter(packet['questions']['q1']['criteria']))})
        parsed=parse_response(model,packet,obj)
        self.assertEqual(parsed['errors'],{'q2':'missing_answer'})
        self.assertIn('q1',parsed['answers'])
        obj['output'][0]['content'][0]['text']='{"q1": null, "q2": "NO_SUCH_OPTION"}'
        self.assertEqual(set(parse_response(model,packet,obj)['errors'].values()),{'invalid_option'})
        obj['output'][0]['content'][0]['text']='{"extra":"not_stated"}'
        with self.assertRaisesRegex(ResponseError,'unexpected_question'):parse_response(model,packet,obj)

    def test_duplicate_keys_nonfinite_and_markdown_are_rejected(self):
        for text in ['{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}','```json\n{}\n```']:
            with self.assertRaises(ValueError):loads(text)
        model=self.config['models'][1];packet,_=bundle(self.g['B001'])
        obj=loads(run.fake_transport(model,packet,0)['raw_body'])
        obj['output'][0]['content'][0]['text']='{"q1":"not_stated","q1":"other","q2":"other"}'
        with self.assertRaises(ValueError):parse_response(model,packet,obj)

    def test_wrong_model_refusal_and_truncation(self):
        packet,_=bundle(self.g['B001'])
        for model in self.config['models']:
            obj=loads(run.fake_transport(model,packet,0)['raw_body']);obj['model']='unapproved-version'
            with self.assertRaisesRegex(ResponseError,'model_version'):parse_response(model,packet,obj)
        model=self.config['models'][1];obj=loads(run.fake_transport(model,packet,0)['raw_body'])
        obj['status']='incomplete'
        with self.assertRaisesRegex(ResponseError,'incomplete'):parse_response(model,packet,obj)
        obj['output'][0]['content']=[{'type':'refusal','refusal':'fixture'}]
        with self.assertRaisesRegex(ResponseError,'refusal'):parse_response(model,packet,obj)

    def test_jev_probability_validation_and_rounding(self):
        model=self.config['models'][0];packet,_=bundle(self.g['B001'])
        obj=loads(run.fake_transport(model,packet,0)['raw_body'])
        obj['answers']['q1']['probabilities']['f0_pregnant_dams']=float('nan')
        self.assertEqual(parse_response(model,packet,obj)['errors']['q1'],'invalid_probabilities')
        obj=loads(run.fake_transport(model,packet,0)['raw_body'])
        probs=obj['answers']['q1']['probabilities'];probs.update({k:.14 for k in probs})
        self.assertFalse(parse_response(model,packet,obj)['errors'])
        self.assertAlmostEqual(parse_response(model,packet,obj)['diagnostics']['q1']['raw_probability_sum'],.98)

    def test_usage_unknowns_and_estimates_remain_distinct(self):
        for model in self.config['models']:
            u=usage_record(model,{})
            self.assertIsNone(u['reported_cost_usd']);self.assertIsNone(u['input_tokens'])
        m=self.config['models'][1]
        u=usage_record(m,{'usage':{'input_tokens':1000,'output_tokens':100}})
        self.assertIsNone(u['usage_cost_estimate_usd'])
        self.assertIsNotNone(u['usage_cost_upper_estimate_usd'])
        self.assertIsNone(u['reported_cost_usd'])

    def test_malformed_envelopes_and_usage_do_not_break_the_run(self):
        job=next(j for j in run.matrix(self.groups,self.config)['jobs'] if j['model_id']=='luna')
        model=next(m for m in self.config['models'] if m['id']=='luna')
        receipt=run.fake_transport(model,job['packet'],0)
        obj=loads(receipt['raw_body']);obj['output']=['invalid message object']
        obj['usage']={'input_tokens':'unknown','output_tokens':-1,'input_tokens_details':'bad','cost':-2}
        receipt['raw_body']=json.dumps(obj)
        result=run.finish(job,model,self.g[job['group_id']],receipt)
        self.assertEqual(set(result['errors'].values()),{'malformed_response'})
        self.assertIsNone(result['resources']['input_tokens'])
        self.assertEqual(len(result['resources']['resource_errors']),3)

    def test_fixed_denominator_does_not_reward_missing_null(self):
        lane={(0,g['group_id']):{'answers':self.answers(g['group_id']),
                                'derived':derive(g,self.answers(g['group_id']))} for g in self.groups}
        score=score_lane(self.groups,self.refs,lane,1)
        self.assertEqual(score['scientific_workflow_choices']['correct'],40)
        self.assertEqual(score['scientific_claims']['exact']['correct'],25)
        del lane[(0,'B004')]
        lane[(0,'D03')]['derived']={'cases':{'D03':{'status':'error'}}}
        score=score_lane(self.groups,self.refs,lane,1)
        self.assertEqual(score['scientific_workflow_choices']['denominator'],40)
        self.assertEqual(score['scientific_workflow_choices']['correct'],38)
        d03=next(r for r in score['per_claim'] if r['case_id']=='D03')
        self.assertFalse(d03['counts_exact'])

    def test_full_dry_run_resume_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out)
            first=run.execute(out)
            self.assertEqual(first['new_attempts'],300)
            snapshots={str(p):sha(p) for p in (out/'attempts').rglob('*.json')}
            second=run.execute(out)
            self.assertEqual(second['new_attempts'],0)
            self.assertEqual(snapshots,{str(p):sha(p) for p in (out/'attempts').rglob('*.json')})
            report=read(Path(second['report']))
            self.assertIsNone(report['model_scores']);self.assertEqual(report['real_api_attempts'],0)
            with self.assertRaises(ValueError):self.prep(out)
            with self.assertRaises(ValueError):run.execute(out,live=True)

    def test_interrupt_after_intent_never_resends(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out)
            job=read(out/'plan.json')['jobs'][0];d=out/'attempts'/job['job_id']
            write_new(d/'intent.json',{'request':job['request'],'request_sha256':job['request_sha256']})
            result=run.execute(out,limit=0)
            self.assertEqual(result['new_attempts'],0);self.assertEqual(result['recovered_without_call'],1)
            prediction=read(d/'prediction.json')
            self.assertEqual(set(prediction['errors'].values()),{'transport_uncertain'})
            self.assertIsNone(prediction['resources']['reported_cost_usd'])

    def test_interrupt_after_receipt_recovers_prediction_without_call(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out)
            job=read(out/'plan.json')['jobs'][0];d=out/'attempts'/job['job_id']
            m=next(m for m in self.config['models'] if m['id']==job['model_id'])
            write_new(d/'intent.json',{'request':job['request'],'request_sha256':job['request_sha256']})
            write_new(d/'receipt.json',run.fake_transport(m,job['packet'],0))
            result=run.execute(out,limit=0)
            self.assertEqual((result['new_attempts'],result['recovered_without_call']),(0,1))
            self.assertEqual(read(d/'prediction.json')['status'],'complete')

    def test_prepared_artifact_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out)
            (out/'inputs.json').write_text('[]')
            with self.assertRaisesRegex(ValueError,'Prepared artifact changed'):run.verify(out)

    def test_prediction_tampering_is_detected_before_scoring(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out);run.execute(out,limit=1)
            path=next((out/'attempts').glob('*/prediction.json'))
            value=read(path);value['answers'][next(iter(value['answers']))]='not_stated'
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'Persisted prediction'):run.report_run(out)

    def test_live_requires_explicit_flag_and_lock_prevents_overlap(self):
        import fcntl
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out,mode='live')
            with self.assertRaisesRegex(ValueError,'Live mode'):run.execute(out)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out)
            with (out/'run.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):run.execute(out)

    def test_partial_response_preserves_one_choice_and_blocks_composition(self):
        job=next(j for j in run.matrix(self.groups,self.config)['jobs'] if j['model_id']=='luna')
        m=next(m for m in self.config['models'] if m['id']=='luna')
        receipt=run.fake_transport(m,job['packet'],0)
        obj=loads(receipt['raw_body']);payload=loads(obj['output'][0]['content'][0]['text']);payload.pop('q2')
        obj['output'][0]['content'][0]['text']=json.dumps(payload);receipt['raw_body']=json.dumps(obj)
        result=run.finish(job,m,self.g[job['group_id']],receipt)
        self.assertEqual(len(result['answers']),1)
        self.assertEqual(set(result['errors'].values()),{'missing_answer'})
        self.assertIsNone(result['derived'])
        receipt.update(http_status=503,raw_body='<html>Unavailable</html>')
        result=run.finish(job,m,self.g[job['group_id']],receipt)
        self.assertEqual(set(result['errors'].values()),{'http_503'})

    def test_http_transport_contract_with_mocked_opener(self):
        from providers import http_transport
        import urllib.request
        class Response:
            status=200
            headers={'x-request-id':'fixture-id','Set-Cookie':'do-not-persist'}
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return b'{"fixture":true}'
        class Opener:
            def open(self,req,timeout):
                self.req=req
                return Response()
        m=self.config['models'][0];packet,_=bundle(self.g['B001']);body=request_body(m,packet);opener=Opener()
        with patch.object(urllib.request,'build_opener',return_value=opener):
            receipt=http_transport(m,body,'SECRET_CANARY',1)
        self.assertEqual(loads(opener.req.data),body)
        self.assertNotIn('SECRET_CANARY',json.dumps(receipt))
        self.assertEqual(receipt['response_headers'],{'x-request-id':'fixture-id'})

    def test_model_version_failure_halts_that_model_without_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'run';self.prep(out,mode='live')
            seen=[]
            def transport(m,body,key,timeout):
                seen.append(m['id'])
                return {'http_status':401,'raw_body':'{"error":{"message":"fixture"}}',
                        'response_headers':{},'latency_seconds':.01,'transport_error':None}
            result=run.execute(out,live=True,transport=transport)
            self.assertEqual(len(seen),6)
            self.assertEqual(len(result['halted_models']),6)
            self.assertEqual(run.execute(out,live=True,transport=transport)['new_attempts'],0)
            report=read(Path(result['report']))
            self.assertEqual(report['model_scores']['jev']['model_routed_semantic_choices']['denominator'],100)


if __name__=='__main__':
    unittest.main(verbosity=2)
