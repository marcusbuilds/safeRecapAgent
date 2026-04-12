"""
# app/filters.py

"""

import re
from typing import Dict


class LocalFilterEngine:
    def __init__(self):
        # context keyed by meeting_id; in prod fetch from encrypted DB
        self.context: Dict[str, dict] = {}


    def add_context(self, meeting_id: str, ctx: dict):
        self.context[meeting_id] = ctx


    def sanitize_for_llm(self, meeting_id: str, text: str) -> str:
        """Mask forbidden terms before sending to cloud LLM."""
        ctx = self.context.get(meeting_id, {})
        terms = ctx.get('forbidden_terms', [])
        sanitized = text
        for t in terms:
            # simple case-insensitive replace
            pattern = re.compile(re.escape(t), re.IGNORECASE)
            sanitized = pattern.sub('[REDACTED]', sanitized)
        return sanitized


    def enforce_rules(self, meeting_id: str, llm_output: dict) -> dict:
        """Apply local rules & final sanitization to LLM output."""
        ctx = self.context.get(meeting_id, {})
        terms = ctx.get('forbidden_terms', [])
        rules = ctx.get('rules', [])

        # sanitize summary
        summary = llm_output.get('summary', '')
        summary = self._remove_terms(summary, terms)

        ais = llm_output.get('action_items', [])
        clean_ais = []
        # Support both list of dicts and list of strings for action_items
        for a in ais:
            if isinstance(a, dict):
                # Sanitize each string field in the dict
                a_clean = {}
                for k, v in a.items():
                    if isinstance(v, str):
                        a_clean[k] = self._remove_terms(v, terms)
                    else:
                        a_clean[k] = v
                # Optionally, check for rule violations in 'task' or 'notes'
                text_to_check = a_clean.get('task', '') + ' ' + a_clean.get('notes', '')
                if not self._violates_rules(text_to_check, rules):
                    clean_ais.append(a_clean)
                else:
                    clean_ais.append({'task': '[REMOVED DUE TO COMPANY POLICY]'})
            elif isinstance(a, str):
                a_clean = self._remove_terms(a, terms)
                if not self._violates_rules(a_clean, rules):
                    clean_ais.append(a_clean)
                else:
                    clean_ais.append('[REMOVED DUE TO COMPANY POLICY]')
            else:
                # Unknown type, just append as is
                clean_ais.append(a)

        return {'summary': summary, 'action_items': clean_ais, 'applied_rules': rules}


    def _remove_terms(self, text: str, terms: list[str]) -> str:
        for t in terms:
            pattern = re.compile(re.escape(t), re.IGNORECASE)
            text = pattern.sub('[REDACTED]', text)
        return text


    def _violates_rules(self, text: str, rules: list[dict]) -> bool:
        # simple rule engine: rule.type == "remove_if_contains" and pattern
        for r in rules:
            if r.get('type') == 'remove_if_contains':
                pat = r.get('pattern')
                if pat and re.search(re.escape(pat), text, re.IGNORECASE):
                    return True
        return False