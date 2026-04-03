#!/usr/bin/env python3
"""
/hack Pipeline Status Report
Reads targets.json and prints a human-readable status for each target.
"""

import json
import os
import sys
from datetime import datetime

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(filename):
    path = os.path.join(PIPELINE_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)

def status_icon(status):
    icons = {
        'done': '\u2705',
        'in_progress': '\U0001f504',
        'pending': '\u274c',
        'blocked': '\U0001f512',
        'skipped': '\u23ed\ufe0f',
    }
    return icons.get(status, '\u2753')

def format_phase_intel(phase):
    icon = status_icon(phase['status'])
    if phase['status'] == 'done':
        return f"  {icon} Intel: done"
    elif phase['status'] == 'in_progress':
        contacts = phase.get('contacts_found', [])
        note = phase.get('notes', '')
        line = f"  {icon} Intel: in progress"
        if contacts:
            line += f" (contacts: {', '.join(contacts)})"
        if note:
            line += f"\n     Note: {note}"
        return line
    else:
        return f"  {icon} Intel: not started"

def format_phase_calls(phase, personas_db):
    icon = status_icon(phase['status'])
    completed = phase.get('personas_completed', [])
    remaining = phase.get('personas_remaining', [])
    total = len(completed) + len(remaining)

    if phase['status'] == 'done':
        return f"  {icon} Calls: {total}/{total} personas complete"
    elif phase['status'] == 'in_progress':
        lines = [f"  {icon} Calls: {len(completed)}/{total} personas ({', '.join(completed) if completed else 'none yet'})"]
        if remaining:
            lines.append(f"     Missing: {', '.join(remaining)}")
        return '\n'.join(lines)
    elif phase['status'] == 'pending':
        return f"  {icon} Calls: not started (0/{total})"
    else:
        return f"  {icon} Calls: {phase['status']}"

def format_phase_emails(phase):
    icon = status_icon(phase['status'])
    if phase['status'] == 'done':
        return f"  {icon} Emails: sent"
    elif phase['status'] == 'in_progress':
        return f"  {icon} Emails: in progress"
    else:
        return f"  {icon} Emails: not sent"

def format_phase_portal(phase):
    icon = status_icon(phase['status'])
    if phase['status'] == 'done':
        return f"  {icon} Portal: audited"
    else:
        return f"  {icon} Portal: not audited"

def format_phase_page(phase):
    icon = status_icon(phase['status'])
    if phase['status'] == 'done':
        url = phase.get('url', 'unknown')
        return f"  {icon} Page: {url}"
    else:
        return f"  {icon} Page: not built"

def format_phase_outreach(phase):
    icon = status_icon(phase['status'])
    if phase['status'] == 'done':
        return f"  {icon} Outreach: sent"
    elif phase['status'] == 'blocked':
        reason = phase.get('reason', 'unknown')
        return f"  {icon} Outreach: blocked ({reason})"
    else:
        return f"  {icon} Outreach: {phase['status']}"

def main():
    targets = load_json('targets.json')
    personas = load_json('personas.json')
    learnings = load_json('learnings.json')

    print(f"\n{'='*50}")
    print(f"  /hack Pipeline Status - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")

    # Summary counts
    total_targets = len(targets)
    active = sum(1 for t in targets.values() if t['status'] == 'active')
    total_calls_done = 0
    total_calls_remaining = 0

    for key, target in targets.items():
        calls = target['phases'].get('calls', {})
        total_calls_done += len(calls.get('personas_completed', []))
        total_calls_remaining += len(calls.get('personas_remaining', []))

    print(f"  Targets: {active} active / {total_targets} total")
    print(f"  Calls: {total_calls_done} done / {total_calls_done + total_calls_remaining} total")
    print(f"  Learnings: {len(learnings)} recorded")
    print(f"  Critical learnings: {sum(1 for l in learnings if l['severity'] == 'critical')}")
    print()

    for key, target in targets.items():
        name = target['name']
        status_badge = f"[{target['status'].upper()}]"
        print(f"  {name} {status_badge}")
        print(f"  {'~' * len(name)}")

        phases = target['phases']
        print(format_phase_intel(phases.get('intel', {'status': 'pending'})))
        print(format_phase_calls(phases.get('calls', {'status': 'pending', 'personas_completed': [], 'personas_remaining': list(personas.keys())}), personas))
        print(format_phase_emails(phases.get('emails', {'status': 'pending'})))
        print(format_phase_portal(phases.get('portal', {'status': 'pending'})))
        print(format_phase_page(phases.get('page', {'status': 'pending'})))
        print(format_phase_outreach(phases.get('outreach', {'status': 'pending'})))

        if target.get('notes'):
            print(f"  \U0001f4dd Note: {target['notes']}")

        print()

    # Show critical learnings
    critical = [l for l in learnings if l['severity'] == 'critical']
    if critical:
        print(f"  {'='*50}")
        print(f"  Critical Learnings (apply to ALL targets)")
        print(f"  {'='*50}")
        for l in critical:
            print(f"  \u26a0\ufe0f  [{l['applies_to']}] {l['learning']}")
        print()

if __name__ == '__main__':
    main()
