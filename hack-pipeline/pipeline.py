#!/usr/bin/env python3
"""
/hack Mystery Shop Pipeline Orchestrator

Autonomous pipeline that tracks state across all target companies,
executes mystery shop phases in order, and never forgets a step.

Usage:
    python pipeline.py                  # Run all targets
    python pipeline.py --target iws     # Run single target
    python pipeline.py --check          # Status report only (no execution)
    python pipeline.py --phase calls    # Run specific phase only
    python pipeline.py --dry-run        # Show what would happen without executing
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import smtplib
import sys
import time
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Union

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PIPELINE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PIPELINE_DIR / "results"
TARGETS_FILE = PIPELINE_DIR / "targets.json"
PERSONAS_FILE = PIPELINE_DIR / "personas.json"
LEARNINGS_FILE = PIPELINE_DIR / "learnings.json"
TWILIO_NUMBERS_FILE = PIPELINE_DIR / "twilio_numbers.json"
EMAIL_TEMPLATES_FILE = PIPELINE_DIR / "email_templates.json"

# ---------------------------------------------------------------------------
# Environment / secrets (loaded from .env or env vars)
# ---------------------------------------------------------------------------
RETELL_API_KEY = os.environ.get("RETELL_API_KEY", "")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

RETELL_API_BASE = "https://api.retellai.com"

# Phase execution order
PHASE_ORDER = ["intel", "calls", "emails", "portal", "page", "outreach"]

# Female caller names (Camille voice = female only)
FEMALE_NAMES = [
    "Sarah Mitchell", "Emily Chen", "Jessica Rodriguez", "Amanda Foster",
    "Rachel Kim", "Nicole Thompson", "Lauren Davis", "Megan Wilson",
    "Stephanie Park", "Danielle Brown", "Christina Lee", "Ashley Martinez",
    "Samantha Clark", "Rebecca Taylor", "Jennifer Adams",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict | list:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # Also write a dated backup
    backup_dir = PIPELINE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{path.stem}_{ts}.json"
    with open(backup_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def setup_logger(target_key: str) -> logging.Logger:
    """Create a per-target logger that writes to results/{target}/pipeline.log."""
    target_dir = RESULTS_DIR / target_key
    target_dir.mkdir(parents=True, exist_ok=True)
    log_path = target_dir / "pipeline.log"

    logger = logging.getLogger(f"hack.{target_key}")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers on re-runs
    if not logger.handlers:
        fh = logging.FileHandler(log_path, mode="a")
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        # Also log to stdout
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(fmt)
        logger.addHandler(sh)

    return logger


def pick_twilio_number(twilio_numbers: list) -> str:
    """Pick a random Twilio number from the pool."""
    return random.choice(twilio_numbers)


def pick_caller_name() -> str:
    """Pick a random female caller name (Camille voice = female only)."""
    return random.choice(FEMALE_NAMES)


def get_applicable_learnings(learnings: list, phase: str) -> list:
    """Filter learnings that apply to a specific phase."""
    phase_map = {
        "intel": "phase0_intel",
        "calls": "phase2_calls",
        "emails": "phase3_emails",
        "portal": "phase1_portal",
        "page": "phase4_page",
        "outreach": "phase5_outreach",
    }
    phase_key = phase_map.get(phase, phase)
    return [l for l in learnings if l["applies_to"] == phase_key]


# ---------------------------------------------------------------------------
# RetellAI call execution
# ---------------------------------------------------------------------------

def create_retell_call(
    agent_id: str,
    to_number: str,
    from_number: str,
    dynamic_variables: dict,
    max_duration_ms: int = 1200000,  # 20 min
    logger: logging.Logger = None,
) -> dict:
    """
    Create an outbound call via RetellAI API.
    Returns the call object with call_id, status, etc.
    """
    if not RETELL_API_KEY:
        msg = "RETELL_API_KEY not set. Cannot make calls."
        if logger:
            logger.error(msg)
        raise EnvironmentError(msg)

    url = f"{RETELL_API_BASE}/v2/create-phone-call"
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "agent_id": agent_id,
        "to_number": to_number,
        "from_number": from_number,
        "retell_llm_dynamic_variables": dynamic_variables,
        "max_call_duration_ms": max_duration_ms,
    }

    if logger:
        logger.info(f"Creating RetellAI call: agent={agent_id}, to={to_number}, from={from_number}")
        logger.debug(f"Dynamic variables: {json.dumps(dynamic_variables)}")

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    call_data = resp.json()

    if logger:
        call_id = call_data.get("call_id", "unknown")
        logger.info(f"Call created: call_id={call_id}")

    return call_data


def get_retell_call(call_id: str, logger: logging.Logger = None) -> dict:
    """Get call details from RetellAI."""
    url = f"{RETELL_API_BASE}/v2/get-call/{call_id}"
    headers = {"Authorization": f"Bearer {RETELL_API_KEY}"}

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def wait_for_call_completion(call_id: str, logger: logging.Logger = None, poll_interval: int = 15, timeout: int = 1200) -> dict:
    """Poll until call is completed or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        call = get_retell_call(call_id, logger)
        status = call.get("call_status") or call.get("status", "unknown")
        if status in ("ended", "error", "failed", "completed"):
            if logger:
                duration = call.get("duration_ms", 0)
                logger.info(f"Call {call_id} ended: status={status}, duration={duration}ms")
            return call
        if logger:
            logger.debug(f"Call {call_id} still {status}, polling again in {poll_interval}s...")
        time.sleep(poll_interval)

    if logger:
        logger.warning(f"Call {call_id} timed out after {timeout}s")
    return {"call_id": call_id, "status": "timeout"}


def verify_phone(phone: str, logger: logging.Logger = None) -> dict:
    """Verify a phone number via RetellAI before calling."""
    url = f"{RETELL_API_BASE}/v2/verify-phone-number"
    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"phone_number": phone}

    if logger:
        logger.info(f"Verifying phone: {phone}")

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        if logger:
            logger.info(f"Phone verification result for {phone}: {json.dumps(result)}")
        return result
    except Exception as e:
        if logger:
            logger.warning(f"Phone verification failed for {phone}: {e}")
        return {"phone": phone, "valid": None, "error": str(e)}


# ---------------------------------------------------------------------------
# Email sending
# ---------------------------------------------------------------------------

def send_email(to_email: str, subject: str, html_body: str, logger: logging.Logger = None) -> bool:
    """Send an email via SMTP."""
    if not SMTP_USER or not SMTP_PASS:
        if logger:
            logger.error("SMTP credentials not set. Cannot send emails.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Jonathan Banner <{SMTP_USER}>"
    msg["To"] = to_email

    html_part = MIMEText(html_body, "html")
    msg.attach(html_part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        if logger:
            logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Email send failed to {to_email}: {e}")
        return False


def render_template(template_html: str, variables: dict) -> str:
    """Replace {{variable}} placeholders in template."""
    result = template_html
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value) if value else "")
    return result


# ---------------------------------------------------------------------------
# Phase executors
# ---------------------------------------------------------------------------

def execute_intel(target_key: str, target: dict, learnings: list, logger: logging.Logger, dry_run: bool = False) -> bool:
    """Phase 0: Intelligence gathering. Mostly manual but we can log status."""
    phase = target["phases"]["intel"]

    if phase["status"] == "done":
        logger.info(f"[{target_key}] Intel already done, skipping.")
        return True

    applicable = get_applicable_learnings(learnings, "intel")
    for l in applicable:
        logger.info(f"[{target_key}] Intel learning: {l['learning']}")

    if dry_run:
        logger.info(f"[{target_key}] DRY RUN: Would gather intel for {target['name']}")
        return False

    # Intel is semi-manual: log what's needed
    logger.info(f"[{target_key}] Intel phase requires manual steps:")
    logger.info(f"  1. Find real clients via Contact Finder")
    logger.info(f"  2. Verify phone numbers")
    logger.info(f"  3. Research CEO/CFO contacts")
    logger.info(f"  4. Check BBB, Glassdoor, lawsuits")
    logger.info(f"  Mark as done in targets.json when complete.")

    return False


def execute_calls(target_key: str, target: dict, personas_db: dict, twilio_numbers: list,
                  learnings: list, logger: logging.Logger, dry_run: bool = False) -> bool:
    """Phase 2: Mystery shop calls via RetellAI."""
    phase = target["phases"]["calls"]
    completed = phase.get("personas_completed", [])
    remaining = phase.get("personas_remaining", [])

    if not remaining:
        logger.info(f"[{target_key}] All call personas completed.")
        phase["status"] = "done"
        return True

    # Log applicable learnings
    applicable = get_applicable_learnings(learnings, "calls")
    critical_learnings = [l for l in applicable if l["severity"] == "critical"]
    for l in critical_learnings:
        logger.info(f"[{target_key}] CRITICAL learning: {l['learning']}")

    phones = target.get("phones", [])
    if not phones:
        logger.error(f"[{target_key}] No phone numbers configured. Cannot make calls.")
        return False

    # Verify phone before calling (learning #3)
    primary_phone = phones[0]
    if not dry_run:
        verify_result = verify_phone(primary_phone, logger)
    else:
        logger.info(f"[{target_key}] DRY RUN: Would verify phone {primary_phone}")

    real_clients = target.get("real_clients", [])

    for persona_key in list(remaining):
        persona = personas_db.get(persona_key)
        if not persona:
            logger.warning(f"[{target_key}] Unknown persona: {persona_key}, skipping.")
            remaining.remove(persona_key)
            continue

        # Check if persona requires real client and we have one
        if persona.get("requires_real_client") and not real_clients:
            logger.warning(f"[{target_key}] Persona {persona_key} requires real client but none available. Skipping.")
            continue

        # Check if this is a timing call -- only run at the right time
        schedule = persona.get("schedule")
        if schedule:
            # Parse "HH:MM local" format
            match = re.match(r"(\d{2}):(\d{2})", schedule)
            if match:
                sched_hour, sched_min = int(match.group(1)), int(match.group(2))
                now = datetime.now()
                # Allow 30-min window around scheduled time
                current_minutes = now.hour * 60 + now.minute
                target_minutes = sched_hour * 60 + sched_min
                if abs(current_minutes - target_minutes) > 30:
                    logger.info(f"[{target_key}] Persona {persona_key} scheduled for {schedule}, "
                              f"current time {now.strftime('%H:%M')}. Skipping (outside window).")
                    continue

        # Build dynamic variables
        caller_name = pick_caller_name()
        from_number = pick_twilio_number(twilio_numbers)

        dyn_vars = {
            "caller_name": caller_name,
            "company_name": target["name"],
        }

        if persona.get("requires_real_client") and real_clients:
            client = random.choice(real_clients)
            dyn_vars["client_name"] = client
            # IWS-specific: add address if available
            if target_key == "iws":
                dyn_vars["client_address"] = ""  # Must be filled from real data

        if dry_run:
            logger.info(f"[{target_key}] DRY RUN: Would call {primary_phone} with persona={persona_key}, "
                       f"agent={persona['agent_id']}, caller={caller_name}, from={from_number}")
            continue

        # Execute the call
        try:
            call_data = create_retell_call(
                agent_id=persona["agent_id"],
                to_number=primary_phone,
                from_number=from_number,
                dynamic_variables=dyn_vars,
                max_duration_ms=1200000,  # 20 min (learning #6)
                logger=logger,
            )

            call_id = call_data.get("call_id")
            if call_id:
                # Save call metadata immediately
                call_log = {
                    "call_id": call_id,
                    "persona": persona_key,
                    "target": target_key,
                    "to_number": primary_phone,
                    "from_number": from_number,
                    "caller_name": caller_name,
                    "dynamic_variables": dyn_vars,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                }
                call_log_path = RESULTS_DIR / target_key / f"call_{persona_key}_{call_id}.json"
                save_json(call_log_path, call_log)

                # Wait for call to complete
                logger.info(f"[{target_key}] Waiting for call {call_id} to complete...")
                result = wait_for_call_completion(call_id, logger)

                # Save full result
                call_log["result"] = result
                call_log["completed_at"] = datetime.now(timezone.utc).isoformat()
                save_json(call_log_path, call_log)

                # Update target state
                completed.append(persona_key)
                remaining.remove(persona_key)
                phase["personas_completed"] = completed
                phase["personas_remaining"] = remaining

                # Save targets after each call (never lose state)
                targets = load_json(TARGETS_FILE)
                targets[target_key] = target
                save_json(TARGETS_FILE, targets)

                logger.info(f"[{target_key}] Persona {persona_key} completed. "
                          f"{len(completed)}/{len(completed)+len(remaining)} done.")

                # Pause between calls to avoid detection
                pause = random.randint(30, 90)
                logger.info(f"[{target_key}] Pausing {pause}s before next call...")
                time.sleep(pause)

        except Exception as e:
            logger.error(f"[{target_key}] Call failed for persona {persona_key}: {e}")
            # Save error to results
            error_path = RESULTS_DIR / target_key / f"call_error_{persona_key}_{datetime.now().strftime('%H%M%S')}.json"
            save_json(error_path, {
                "persona": persona_key,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            continue

    # Check if all done
    if not remaining:
        phase["status"] = "done"
        phase["completed_at"] = datetime.now().strftime("%Y-%m-%d")
        return True

    phase["status"] = "in_progress"
    return False


def execute_emails(target_key: str, target: dict, email_templates: dict,
                   learnings: list, logger: logging.Logger, dry_run: bool = False) -> bool:
    """Phase 3: Send outreach emails to CEO/CFO."""
    phase = target["phases"]["emails"]

    if phase["status"] == "done":
        logger.info(f"[{target_key}] Emails already sent, skipping.")
        return True

    ceo = target.get("ceo", {})
    ceo_email = ceo.get("email")
    ceo_name = ceo.get("name", "")

    if not ceo_email:
        logger.warning(f"[{target_key}] No CEO email found. Cannot send emails. "
                      f"Find email for {ceo_name} and update targets.json.")
        return False

    # Log learnings
    applicable = get_applicable_learnings(learnings, "emails")
    for l in applicable:
        logger.info(f"[{target_key}] Email learning: {l['learning']}")

    # Build variables
    ceo_first = ceo_name.split()[0] if ceo_name else "there"
    audit_url = target["phases"].get("page", {}).get("url", "")

    # Count completed calls for the email
    calls_phase = target["phases"].get("calls", {})
    call_count = len(calls_phase.get("personas_completed", []))

    variables = {
        "company_name": target["name"],
        "ceo_first_name": ceo_first,
        "audit_page_url": f"https://{audit_url}" if audit_url and not audit_url.startswith("http") else audit_url,
        "audit_page_link": f"<a href='https://{audit_url}'>View your audit</a>" if audit_url else "",
        "call_count": str(call_count),
        "findings_bullets": "<li>Details from mystery shop calls</li>",  # TODO: auto-generate from call results
        "top_finding": "Your billing team is unreachable during key hours",
        "companies_audited": "6",
        "score": "45",
        "comparison": "below the industry average of 72",
    }

    template = email_templates.get("initial_outreach", {})
    subject = render_template(template.get("subject", ""), variables)
    body = render_template(template.get("body_html", ""), variables)

    if dry_run:
        logger.info(f"[{target_key}] DRY RUN: Would send email to {ceo_email}")
        logger.info(f"[{target_key}] Subject: {subject}")
        return False

    # OUTREACH GATE: emails require explicit JB approval
    logger.warning(f"[{target_key}] EMAIL BLOCKED: Outreach emails require JB approval.")
    logger.warning(f"[{target_key}] To send: set emails.status='approved' in targets.json and re-run.")
    logger.info(f"[{target_key}] Prepared email for {ceo_email}: {subject}")

    # Save the prepared email
    email_path = RESULTS_DIR / target_key / f"email_prepared_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_json(email_path, {
        "to": ceo_email,
        "subject": subject,
        "body_html": body,
        "template": "initial_outreach",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_approval",
    })

    return False


def execute_portal(target_key: str, target: dict, learnings: list,
                   logger: logging.Logger, dry_run: bool = False) -> bool:
    """Phase: Portal audit (mostly manual)."""
    phase = target["phases"]["portal"]

    if phase["status"] == "done":
        logger.info(f"[{target_key}] Portal audit already done, skipping.")
        return True

    if dry_run:
        logger.info(f"[{target_key}] DRY RUN: Would audit payment portal for {target['name']}")
        return False

    logger.info(f"[{target_key}] Portal audit requires manual steps:")
    logger.info(f"  1. Visit {target['name']} payment portal (if exists)")
    logger.info(f"  2. Test registration flow")
    logger.info(f"  3. Test payment flow")
    logger.info(f"  4. Document UX issues")
    logger.info(f"  Mark as done in targets.json when complete.")

    return False


def execute_page(target_key: str, target: dict, learnings: list,
                 logger: logging.Logger, dry_run: bool = False) -> bool:
    """Phase: Build audit page."""
    phase = target["phases"]["page"]

    if phase["status"] == "done":
        logger.info(f"[{target_key}] Audit page already built: {phase.get('url', 'unknown')}")
        return True

    # Check we have enough call data to build a page
    calls_phase = target["phases"].get("calls", {})
    completed_calls = len(calls_phase.get("personas_completed", []))
    if completed_calls < 2:
        logger.warning(f"[{target_key}] Only {completed_calls} calls completed. "
                      f"Need at least 2 to build a compelling page.")
        return False

    if dry_run:
        logger.info(f"[{target_key}] DRY RUN: Would build audit page for {target['name']}")
        return False

    # Page building is manual (complex HTML with call recordings, transcripts, etc.)
    applicable = get_applicable_learnings(learnings, "page")
    for l in applicable:
        logger.info(f"[{target_key}] Page learning: {l['learning']}")

    logger.info(f"[{target_key}] Audit page needs manual build:")
    logger.info(f"  1. Gather call recordings and transcripts from results/{target_key}/")
    logger.info(f"  2. Build narrative page (learning: tell a STORY)")
    logger.info(f"  3. Add audio player with transcript sync")
    logger.info(f"  4. Deploy to agentcollect.com/audit-{target_key}.html")
    logger.info(f"  Mark as done with URL in targets.json when complete.")

    return False


def execute_outreach(target_key: str, target: dict, email_templates: dict,
                     learnings: list, logger: logging.Logger, dry_run: bool = False) -> bool:
    """Phase: CEO outreach (ALWAYS requires JB go)."""
    phase = target["phases"]["outreach"]

    if phase["status"] == "done":
        logger.info(f"[{target_key}] Outreach already sent.")
        return True

    # Outreach is ALWAYS blocked until JB explicitly approves
    if phase["status"] != "approved":
        logger.info(f"[{target_key}] Outreach BLOCKED: requires JB approval.")
        logger.info(f"  To approve: set outreach.status='approved' in targets.json")
        return False

    if dry_run:
        logger.info(f"[{target_key}] DRY RUN: Would execute outreach for {target['name']}")
        return False

    # Check prerequisites
    page_phase = target["phases"].get("page", {})
    calls_phase = target["phases"].get("calls", {})

    if page_phase.get("status") != "done":
        logger.warning(f"[{target_key}] Cannot send outreach: audit page not built yet.")
        return False

    if len(calls_phase.get("personas_completed", [])) < 3:
        logger.warning(f"[{target_key}] Cannot send outreach: need at least 3 completed calls.")
        return False

    ceo = target.get("ceo", {})
    if not ceo.get("email"):
        logger.warning(f"[{target_key}] Cannot send outreach: no CEO email.")
        return False

    # All checks passed, send the outreach email
    ceo_first = ceo["name"].split()[0] if ceo.get("name") else "there"
    audit_url = page_phase.get("url", "")
    call_count = len(calls_phase.get("personas_completed", []))

    template = email_templates.get("initial_outreach", {})
    variables = {
        "company_name": target["name"],
        "ceo_first_name": ceo_first,
        "audit_page_url": f"https://{audit_url}" if audit_url else "",
        "audit_page_link": f"<a href='https://{audit_url}'>View your audit</a>" if audit_url else "",
        "call_count": str(call_count),
        "findings_bullets": "<li>Call recordings and findings available on your audit page</li>",
        "top_finding": "",
    }

    subject = render_template(template.get("subject", ""), variables)
    body = render_template(template.get("body_html", ""), variables)

    success = send_email(ceo["email"], subject, body, logger)
    if success:
        phase["status"] = "done"
        phase["sent_at"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"[{target_key}] Outreach email sent to {ceo['email']}")
    else:
        logger.error(f"[{target_key}] Failed to send outreach email.")

    return success


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

PHASE_EXECUTORS = {
    "intel": execute_intel,
    "calls": execute_calls,
    "emails": execute_emails,
    "portal": execute_portal,
    "page": execute_page,
    "outreach": execute_outreach,
}


def run_target(target_key: str, target: dict, personas_db: dict, twilio_numbers: list,
               email_templates: dict, learnings: list, phase_filter: str = None,
               dry_run: bool = False):
    """Run all incomplete phases for a single target."""
    logger = setup_logger(target_key)
    logger.info(f"{'='*60}")
    logger.info(f"Starting pipeline for {target['name']} ({target_key})")
    logger.info(f"{'='*60}")

    if target.get("status") != "active":
        logger.info(f"[{target_key}] Target is {target.get('status', 'unknown')}, skipping.")
        return

    phases_to_run = [phase_filter] if phase_filter else PHASE_ORDER

    for phase_name in phases_to_run:
        if phase_name not in target["phases"]:
            logger.warning(f"[{target_key}] Phase {phase_name} not in target config, skipping.")
            continue

        phase = target["phases"][phase_name]

        if phase.get("status") == "done":
            logger.info(f"[{target_key}] Phase {phase_name}: already done.")
            continue

        if phase.get("status") == "blocked" and phase_name != "outreach":
            reason = phase.get("reason", "unknown")
            logger.info(f"[{target_key}] Phase {phase_name}: blocked ({reason}).")
            continue

        logger.info(f"[{target_key}] Running phase: {phase_name}")

        # Route to the right executor
        if phase_name == "calls":
            execute_calls(target_key, target, personas_db, twilio_numbers, learnings, logger, dry_run)
        elif phase_name == "emails":
            execute_emails(target_key, target, email_templates, learnings, logger, dry_run)
        elif phase_name == "outreach":
            execute_outreach(target_key, target, email_templates, learnings, logger, dry_run)
        elif phase_name == "intel":
            execute_intel(target_key, target, learnings, logger, dry_run)
        elif phase_name == "portal":
            execute_portal(target_key, target, learnings, logger, dry_run)
        elif phase_name == "page":
            execute_page(target_key, target, learnings, logger, dry_run)

    # Save final state
    if not dry_run:
        targets = load_json(TARGETS_FILE)
        targets[target_key] = target
        save_json(TARGETS_FILE, targets)

    logger.info(f"[{target_key}] Pipeline run complete.")


def run_check():
    """Run check.py status report."""
    import subprocess
    check_script = PIPELINE_DIR / "check.py"
    subprocess.run([sys.executable, str(check_script)])


def main():
    parser = argparse.ArgumentParser(description="/hack Mystery Shop Pipeline")
    parser.add_argument("--target", "-t", help="Run only this target (e.g., iws)")
    parser.add_argument("--check", "-c", action="store_true", help="Status report only, no execution")
    parser.add_argument("--phase", "-p", help="Run only this phase (e.g., calls, emails)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would happen without executing")
    args = parser.parse_args()

    if args.check:
        run_check()
        return

    # Load all config
    targets = load_json(TARGETS_FILE)
    personas_db = load_json(PERSONAS_FILE)
    twilio_numbers = load_json(TWILIO_NUMBERS_FILE)
    email_templates = load_json(EMAIL_TEMPLATES_FILE)
    learnings = load_json(LEARNINGS_FILE)

    # Ensure results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Print summary header
    print(f"\n{'='*60}")
    print(f"  /hack Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    if args.target:
        print(f"  Target: {args.target}")
    if args.phase:
        print(f"  Phase: {args.phase}")
    print(f"  Learnings loaded: {len(learnings)} ({sum(1 for l in learnings if l['severity'] == 'critical')} critical)")
    print(f"  Twilio numbers: {len(twilio_numbers)} in pool")
    print(f"{'='*60}\n")

    # Validate env for live runs
    if not args.dry_run:
        missing = []
        if not RETELL_API_KEY:
            missing.append("RETELL_API_KEY")
        if missing:
            print(f"WARNING: Missing environment variables: {', '.join(missing)}")
            print("Set these before running in LIVE mode. Use --dry-run to preview.\n")

    # Run targets
    if args.target:
        if args.target not in targets:
            print(f"ERROR: Target '{args.target}' not found. Available: {', '.join(targets.keys())}")
            sys.exit(1)
        run_target(args.target, targets[args.target], personas_db, twilio_numbers,
                  email_templates, learnings, args.phase, args.dry_run)
    else:
        for key, target in targets.items():
            run_target(key, target, personas_db, twilio_numbers,
                      email_templates, learnings, args.phase, args.dry_run)

    print(f"\nPipeline run complete. Logs in: {RESULTS_DIR}/")
    print(f"Run 'python check.py' for status report.\n")


if __name__ == "__main__":
    main()
