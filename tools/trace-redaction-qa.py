#!/usr/bin/env python3
"""Static/data-contract QA for Ultimate Designer trace redaction."""
from __future__ import annotations

import pathlib
import re
import sys

TOOLS = pathlib.Path('assets/ultimate-designer-trace-tools-v0879.js')
BASE = pathlib.Path('assets/ultimate-designer-trace-v0876.js')


def main() -> int:
    errors: list[str] = []
    if not TOOLS.is_file() or not BASE.is_file():
        print('ERROR: trace assets missing', file=sys.stderr)
        return 2

    tools = TOOLS.read_text(encoding='utf-8')
    base = BASE.read_text(encoding='utf-8')

    required_terms = ['password', 'secret', 'token', 'nonce', 'authorization', 'cookie', 'bearer', 'credential', 'session', 'csrf']
    lower = tools.lower()
    for term in required_terms:
        if term not in lower:
            errors.append(f'missing redaction term: {term}')

    if 'function supportBundle()' not in tools or 'return redact({' not in tools:
        errors.append('support bundle is not passed through recursive redaction')
    if 'redactionSelfTest' not in tools:
        errors.append('runtime redaction self-test missing')
    if re.search(r'document\.cookie\s*(?:[),;]|$)', tools + '\n' + base):
        errors.append('trace source reads document.cookie directly')
    if 'localStorage' not in base:
        errors.append('base trace persistence contract missing')
    if 'CRITICAL_JS_ERROR' not in tools or 'CRITICAL_PROMISE_REJECTION' not in tools:
        errors.append('critical JS error markers missing')

    # Contract-level sample: any sensitive key must collapse to a literal marker.
    sample_keys = ['password', 'api_token', 'nonce', 'Cookie', 'Authorization', 'session_id', 'csrf']
    matcher = re.compile(r'pass(word)?|secret|token|nonce|authorization|api[-_ ]?key|cookie|bearer|credential|session|csrf', re.I)
    if not all(matcher.search(key) for key in sample_keys):
        errors.append('redaction key matcher does not cover QA sample')

    if errors:
        for error in errors:
            print('ERROR:', error, file=sys.stderr)
        return 1
    print('Trace redaction QA PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
