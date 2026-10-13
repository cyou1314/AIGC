#!/usr/bin/env python3
"""Validate review evidence bookkeeping; never evaluates visual quality."""
import argparse
import json
from pathlib import Path

LEVELS = {'brief', 'source', 'render', 'interaction'}
SEVERITIES = {'blocker', 'major', 'minor', 'taste'}


def evaluate(review):
    if review.get('domain') not in {'poster', 'character', 'costume', 'environment', 'ui'}:
        raise ValueError('Unknown design domain')
    level = review.get('evidence_level')
    if level not in LEVELS:
        raise ValueError('Unknown evidence level')
    if level != 'brief':
        assets = review.get('artifacts', [])
        if not assets or any(not Path(p).is_absolute() or not Path(p).is_file()
                             or Path(p).stat().st_size == 0 for p in assets):
            raise ValueError('Evidence requires nonempty existing absolute artifact paths')
    findings = review.get('findings', [])
    if not isinstance(findings, list):
        raise ValueError('Findings must be a list')
    for finding in findings:
        if finding.get('severity') not in SEVERITIES:
            raise ValueError('Unknown severity')
        if not all(isinstance(finding.get(k), str) and finding[k].strip()
                   for k in ['evidence', 'impact', 'fix', 'preserve', 'verify']):
            raise ValueError('Findings need evidence, impact, fix, preserve and verify')
    if level == 'interaction' and not review.get('interaction_checks'):
        raise ValueError('Interaction evidence needs actual check descriptions')
    blocked = any(f['severity'] in {'blocker', 'major'} and not f.get('resolved', False)
                  for f in findings)
    if review.get('decision') == 'accepted' and (blocked or level in {'brief', 'source'}):
        raise ValueError('Acceptance requires inspected output and no unresolved major/blocker')
    return {'gate': 'blocked' if blocked else 'review-record-valid',
            'evidence_level': level, 'findings': len(findings),
            'proof': 'bookkeeping-only; human/agent inspection remains authoritative'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(evaluate(json.loads(args.review.read_text(encoding='utf-8'))), ensure_ascii=False))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
