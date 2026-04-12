"""
tests/test_filters.py
"""

from app.filters import LocalFilterEngine


def test_sanitize_and_enforce():
    f = LocalFilterEngine()
    mid = 'm1'
    f.add_context(mid, {'forbidden_terms': ['secret'], 'rules': [{'id':'r1','type':'remove_if_contains','pattern':'do not share'}]})
    text = 'This contains secret info and should be removed.'
    sanitized = f.sanitize_for_llm(mid, text)
    assert '[REDACTED]' in sanitized


    llm_output = {'summary': 'Public. secret here.', 'action_items': ['Share with external team', 'Do not share financials - do not share']}
    final = f.enforce_rules(mid, llm_output)
    assert 'secret' not in final['summary']
    assert final['action_items'][-1] == '[REMOVED DUE TO COMPANY POLICY]'