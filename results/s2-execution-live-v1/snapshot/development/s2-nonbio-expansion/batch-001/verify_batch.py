"""Offline integrity, review-attribution, and arithmetic checks for this batch.

This is not a scientific correctness test, semantic classifier, or rule runner.
Use --release for current published content. Historical --write-checks requires the original archive.
"""
import argparse
import copy
import hashlib
import itertools
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[2]


def read(name):
    return json.loads((B/name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def reviewed_input_sha(problem, revisions, decision_id):
    """Check the exact source edits while retaining the original review hash."""
    matches = [r for r in revisions if r['problem_id'] == problem['problem_id']]
    assert len(matches) <= 1
    restored = copy.deepcopy(problem)
    for revision in matches:
        assert revision['prior_decision_id'] == decision_id
        assert canonical_sha(restored) == revision['after_problem_input_sha256']
        assert revision['edits']
        for edit in revision['edits']:
            path = edit['path']
            assert path in [['evidence', 0, 'text'], ['evidence', 0, 'location']]
            parent = restored
            for key in path[:-1]:
                parent = parent[key]
            assert parent[path[-1]] == edit['after']
            parent[path[-1]] = edit['before']
        assert canonical_sha(restored) == revision['before_problem_input_sha256']
    return canonical_sha(restored)


def artifact_hashes():
    return {str(p.relative_to(B)):sha(p) for p in sorted(B.rglob("*"))
            if p.is_file() and "history" not in p.relative_to(B).parts
            and "__pycache__" not in p.parts and p.name not in {"checks.json", "checks.sha256"}}


def verify_content():
    inputs, evaluation, sources, inventory = [read(n) for n in ["inputs.json", "evaluation.json", "sources.json", "existing_inventory.json"]]
    ps=inputs['problems']; es=evaluation['problems']; ss=sources['source_records']
    pids=[p['problem_id'] for p in ps]
    qids=[q['question_id'] for p in ps for q in p['questions']]
    sids=[s['source_id'] for s in ss]
    assert len(pids)==len(set(pids))==10
    assert len(qids)==len(set(qids))==18
    assert len(sids)==len(set(sids))==12
    assert evaluation['problem_count']==10 and evaluation['question_count']==18
    assert pids==[p['problem_id'] for p in es]
    assert sources['source_family_count']==len({s['source_family'] for s in ss})==10
    assert sources['newly_introduced_source_families']==9
    old= json.loads((ROOT/'development/s2-nonbio-v1/choice-review-v1/inputs.json').read_text())
    oldq={q['question_id'] for q in old['questions']}
    assert not set(qids)&oldq
    assert not set(pids)&set(inventory['current_groups'])
    decisions=read('review_decisions.json')['decisions']
    source_revision = read('source_revisions.json')
    assert source_revision['authorized_by'] == 'user' and source_revision['summary']
    assert source_revision['references_changed'] is False
    revisions = source_revision['input_revisions']
    assert [r['problem_id'] for r in revisions] == ['E010']
    assert len({d['decision_id'] for d in decisions})==len(decisions)
    accepted_questions={}; accepted_problems={}
    for d in decisions:
        assert d['reviewer']=='user' and d['decision_id'] and d['approved_questions']
        assert d['decision'] in {'accepted_as_proposed', 'accepted_with_requested_minor_edits'}
        for qid,accepted in d['approved_questions'].items():
            assert qid in qids and qid not in accepted_questions
            accepted_questions[qid]=(d['decision_id'],accepted)
        for pid in d['approved_problem_ids']:
            assert pid in pids and pid not in accepted_problems
            problem_input=next(p for p in ps if p['problem_id']==pid)
            assert all(q['question_id'] in d['approved_questions'] for q in problem_input['questions'])
            assert reviewed_input_sha(problem_input, revisions, d['decision_id'])==d['current_problem_input_sha256_after_requested_edits']
            accepted_problems[pid]=d['decision_id']
    summary=dict(user_accepted_problems=len(accepted_problems),pending_problems=10-len(accepted_problems),
                 user_accepted_questions=len(accepted_questions),pending_questions=18-len(accepted_questions),
                 next_problem_for_review=next((p for p in pids if p not in accepted_problems),None))
    assert evaluation['review_summary']==summary
    expected_reference_status = ('fully_user_accepted' if summary['pending_questions'] == 0
                                 else 'partially_user_accepted')
    assert evaluation['reference_status'] == expected_reference_status

    permitted_problem={"problem_id", "title", "source_ids", "target_treatment", "scope", "evidence", "scientific_claim", "claim_origin", "records", "questions", "source_assets"}
    forbidden={"reference_option", "evidence_rationale", "expected_outcome", "review_status", "prepared_by", "reviewed_by", "approved_by_user", "approval_evidence", "review_issues", "closest_existing_problem_ids", "substantive_difference", "reference_provenance", "deterministic_work"}
    def inspect(x):
        if isinstance(x,dict):
            assert not set(x)&forbidden
            for v in x.values():inspect(v)
        elif isinstance(x,list):
            for v in x:inspect(v)
    inspect(inputs)
    doc=(B/'BATCH_REVIEW.md').read_text()
    log=(B/'REVIEW_LOG.md').read_text()
    anchors=set(re.findall(r'<a id="([^"]+)"',doc))
    assert set(re.findall(r'\]\(#([^)]+)\)',doc))<=anchors

    for p,e in zip(ps,es):
        pid=p['problem_id']; assert re.fullmatch(r'E\d{3}',pid)
        assert set(p)==permitted_problem
        assert p['source_ids']==e['reference_provenance']['source_ids']
        assert set(p['source_ids'])<=set(sids)
        expected_status=('user_reviewed' if pid in accepted_problems else
                         'user_prepared_partially_accepted' if any(q['question_id'] in accepted_questions for q in p['questions']) else
                         'user_prepared_pending_review')
        assert e['review_status']==expected_status
        assert all(x in inventory['current_groups'] for x in e['closest_existing_problem_ids'])
        block=doc.split(f"## {pid} — ",1)[1].split('\n<a id=',1)[0]
        assert p['title'] in block
        assert f"Status: {expected_status}." in block
        for k in ['target_treatment','scope','scientific_claim','claim_origin']:assert p[k] in block
        for ev in p['evidence']:
            assert ev['source_id'] in p['source_ids']
            assert ev['location'] and ev['kind']=='source_faithful_adaptation'
            assert ev['text'] in block
        if p['records']:
            records_in_md=json.loads(re.search(r'\*\*Supplied records / design constants:\*\*\s+```json\n(.*?)\n```',block,re.S)[1])
            assert records_in_md==p['records']
        for asset in p['source_assets']:
            ap=(B/asset).resolve(); assert ap.is_relative_to(B) and ap.is_file()
            assert asset in [f for s in ss if s['source_id'] in p['source_ids'] for f in s['local_files']]
        assert [q['question_id'] for q in p['questions']]==[q['question_id'] for q in e['questions']]
        for q,eq in zip(p['questions'],e['questions']):
            qid=q['question_id']; assert qid.startswith(pid+'-Q')
            assert set(q)=={'question_id','instruction','options'}
            assert len(q['options'])==len(set(q['options']))
            assert all(isinstance(v,str) and v for v in q['options'].values())
            assert eq['reference_option'] in q['options']
            if qid in accepted_questions:
                decision_id,accepted=accepted_questions[qid]
                assert eq['review_status']=='user_reviewed' and eq['approved_by_user'] is True
                assert eq['reviewed_by']=='user'
                assert eq['approval_evidence']['record_file']=='review_decisions.json'
                assert eq['approval_evidence']['decision_id']==decision_id
                assert eq['reference_option']==accepted['reference_option']
                assert canonical_sha(q)==accepted['question_input_sha256']
            else:
                decision_id='None'
                assert eq['prepared_by']=='user'
                assert eq['review_status']=='user_prepared_pending_review'
                assert eq['approved_by_user'] is False and eq['approval_evidence'] is None
            qb=block.split(f'#### {qid}\n',1)[1].split('\n#### ',1)[0].split('\n### ',1)[0]
            instruction=qb.strip().split('\n\n',1)[0]
            assert instruction==q['instruction']
            actual_options=dict(re.findall(r'^- `([^`]+)`: (.+)$',qb,re.M))
            assert actual_options==q['options']
            reference_label='Accepted' if qid in accepted_questions else 'Proposed'
            assert re.search(r'\*\*'+reference_label+r' reference:\*\* `([^`]+)`',qb)[1]==eq['reference_option']
            assert re.search(r'\*\*Evidence rationale:\*\* (.+)',qb)[1]==eq['evidence_rationale']
            assert re.search(r'\*\*Downstream role:\*\* (.+)',qb)[1]==eq['downstream_role']
            assert f"| {pid} | {expected_status} | {qid} | {eq['review_status']} | {decision_id} |" in log
            md_decision=decision_id if decision_id!='None' else 'none'
            review_line = (f"**Question status:** {eq['review_status']}; reviewed by: user; decision: {md_decision}."
                           if qid in accepted_questions else
                           f"**Question status:** {eq['review_status']}; user-prepared; user approval: {md_decision}.")
            assert review_line in qb
        out_in_md=json.loads(re.search(r'\*\*(?:Proposed|Accepted) downstream outcome:\*\*\s+```json\n(.*?)\n```',block,re.S)[1])
        assert out_in_md==e['deterministic_work']['expected_outcome']
    for s in ss:
        assert s['url'].startswith('https://') and s['version'] and s['access_date'] and s['inspected_locations']
        assert s['linked_problem_ids']==[p['problem_id'] for p in ps if s['source_id'] in p['source_ids']]
        for f in s['local_files']:assert (B/f).is_file(),f
        for pid in s['linked_problem_ids']:
            block=doc.split(f'## {pid} — ',1)[1].split('\n<a id=',1)[0]
            assert f"[{s['title']}]({s['url']})" in block and s['version'] in block
    for f,h in inventory['protected_sha256'].items():
        assert sha(ROOT/f)==h, f'Protected original changed: {f}'

    calc={}; pm={p['problem_id']:p for p in ps}; em={p['problem_id']:p for p in es}
    r=pm['E001']['records']; cells=list(itertools.product(r['implant_setting_codes'],r['anneal_setting_codes']))
    counts=defaultdict(int)
    for c in cells:counts[c]+=r['wafers_per_intersection']
    calc['E001']=dict(implant_batches=len(r['implant_setting_codes']), anneal_batches=len(r['anneal_setting_codes']), wafer_records=sum(counts.values()),full_setting_combinations=len(counts),wafers_per_full_setting=next(iter(set(counts.values()))),complete_blocks=r['illustrated_blocks'])
    calc['E002']={"actual_eligible_application_count":None}
    assert 'eight consecutive cycles' in pm['E003']['evidence'][0]['text']
    calc['E003']={"reported_reaction_cycles":8}
    calc['E004']={"exact_parent_lot_count":None}
    r=pm['E005']['records']; calc['E005']=dict(next_stress_after_initial_failure_MPa=r['starting_stress_MPa']-r['step_MPa'],next_stress_after_initial_runout_MPa=r['starting_stress_MPa']+r['step_MPa'])
    r=pm['E006']['records']; calc['E006']=dict(paired_realizations=r['paired_realizations'],paired_execution_count=r['paired_realizations']*r['executions_per_paired_realization'],values_entering_pair_ensemble=r['paired_realizations'])
    r=pm['E007']['records']; n=len(r['macro_start_dates']); a=n*r['original_micro_members_per_date']+len(r['original_extra_start_years']); b=n*r['smbb_micro_members_per_date']+len(r['smbb_extra_start_years'])
    assert not set(r['original_extra_start_years'])&set(r['smbb_extra_start_years'])
    calc['E007']=dict(original_members=a,smbb_members=b,total_members=a+b)
    r=pm['E008']['records']; groups=defaultdict(list)
    assert len(r['factor_order'])==8 and len(r['runs'])==20
    assert [x['column'] for x in r['runs']]==list(range(1,21))
    for row in r['runs']:
        assert len(row['factor_settings'])==8 and set(row['factor_settings'])<={'+','-'}
        groups[tuple(row['factor_settings'])].append(row['column'])
    calc['E008']=dict(run_count=len(r['runs']),distinct_complete_settings=len(groups),repeated_column_groups=sorted(g for g in groups.values() if len(g)>1),singleton_settings=sum(len(g)==1 for g in groups.values()),pure_error_df=sum(len(g)-1 for g in groups.values()))
    # Exact rational checks of the published covariance substitution. These are
    # algebra fixtures, not observations, uncertainty estimates, or new experiments.
    for uI,uL,uB in [(Fraction(2),Fraction(3),Fraction(1)),(Fraction(5,2),Fraction(7,3),Fraction(1,4)),(Fraction(4),Fraction(5),Fraction(0))]:
        r=uB*uB/(uI*uL)
        assert 2*r*uI*uL==2*uB*uB
    calc['E009']=dict(compared_laboratory_results=2,calibration_visits=3)
    r=pm['E010']['records']; n=r['initial_EUs']-r['precipitation_QC_exclusions']-r['generator_exclusions']
    assert n==r['reported_retained_EUs']
    calc['E010']=dict(original_EUs=r['initial_EUs'],retained_EUs=n,joint_assignment_events=n,range_level_records=n*r['ranges_per_EU'])
    for pid,out in calc.items():
        expected=em[pid]['deterministic_work']['expected_outcome']
        for k,v in out.items():assert expected[k]==v,(pid,k,v,expected[k])

    history=B/'history/initial-presented/manifest.json'
    snap={"present":history.exists()}
    if history.exists():
        hm=json.loads(history.read_text())
        for f,h in hm['snapshot_sha256'].items():assert sha(history.parent/f)==h
        for f,h in hm['evidence_sha256'].items():assert sha(B/f)==h
        snap.update(integrity_verified=True, manifest_sha256=sha(history),
                    note="The snapshot preserves first-presented drafts. Its checks.json is the preparation checkpoint; current checks may include the subsequent snapshot-integrity check.")
    return dict(problem_count=10, question_count=18, source_record_count=12, source_family_count=10,
                new_source_families_relative_to_original=9,
                ids_unique_and_noncolliding=True, internal_links_and_source_assets_resolve=True,
                external_links="Successful source retrievals or actual full-text web inspection recorded; publisher/download 403 exceptions are explicit in sources.json. No blanket live-URL success is claimed.",
                every_reference_option_exists=True, markdown_json_question_option_reference_agreement=True,
                markdown_json_scope_evidence_records_outcome_agreement=True,
                reference_fields_absent_from_model_inputs=True, review_status_bound_to_explicit_user_decisions=True,
                authorized_source_qualifications=len(revisions),
                review_summary=summary,
                original_protected_files_unchanged=len(inventory['protected_sha256']),
                offline_calculations=calc, calculation_scope="Counts and identities conditional on supplied source facts and proposed semantic interpretation; no model calls and no empirical reanalysis.",
                snapshot=snap)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--write-checks',action='store_true'); args=ap.parse_args()
    result=verify_content()
    if args.write_checks:
        report=dict(batch_id="batch-001", checked_at_utc=datetime.now(timezone.utc).isoformat(),
                    automated_checks=result,
                    source_review=dict(reference_status=("user_reviewed" if result["review_summary"]["pending_questions"] == 0 else "pending_user_review"),
                      review_decisions="review_decisions.json", independent_human_annotation=False,
                      review_basis="Recorded source locations and inspection limits in sources.json; accepted scopes in review_decisions.json.",
                      unresolved="Source and inference limits are recorded per problem in evaluation.json and REVIEW_LOG.md. Automated checks validate structure and arithmetic."),
                    artifact_sha256=artifact_hashes(),
                    hash_policy="SHA-256 of all current batch files except checks.json, checks.sha256, history/, and __pycache__/. checks.sha256 covers checks.json to avoid self-reference. history/initial-presented/manifest.json independently covers the preserved drafts and their evidence dependencies.")
        (B/'checks.json').write_text(json.dumps(report,indent=2)+"\n")
        (B/'checks.sha256').write_text(sha(B/'checks.json')+"  checks.json\n")
    report=read('checks.json')
    assert report['artifact_sha256']==artifact_hashes(), 'Current artifact hashes differ; review changes before --write-checks.'
    assert (B/'checks.sha256').read_text().split()[0]==sha(B/'checks.json')
    print(json.dumps(dict(status="passed", problem_count=10, question_count=18,
                         review_summary=result['review_summary'],
                         artifact_hashes_verified=len(report['artifact_sha256']), snapshot=result['snapshot'],
                         original_files_unchanged=result['original_protected_files_unchanged'],
                         scientific_correctness="not established by these checks", checks_sha256=sha(B/'checks.json')),indent=2))


if __name__=='__main__':main()
