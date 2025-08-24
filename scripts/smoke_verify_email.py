#!/usr/bin/env python3
"""
Smoke test for email verification flow for both Student and Employer users.

Environment variables required:
- API_BASE_URL (default: http://localhost:8000)
- STUDENT_EMAIL, STUDENT_PASSWORD (if password not set, will default to Test@1234 and user will be auto-registered if needed)
- EMPLOYER_EMAIL, EMPLOYER_PASSWORD (optional; same auto-register behavior if provided)

Usage:
  API_BASE_URL=http://localhost:8000 \
  STUDENT_EMAIL=student@example.com STUDENT_PASSWORD=pass \
  EMPLOYER_EMAIL=employer@example.com EMPLOYER_PASSWORD=pass \
  python3 scripts/smoke_verify_email.py

The backend must expose:
- POST /auth/login { email, password }
- POST /auth/verify/request (Authorization: Bearer ...)
- GET  /auth/verify/confirm?token=...

This script is safe and read-only with respect to user data, aside from possibly marking the account verified if not already.
"""
from __future__ import annotations
import os
import sys
import time
import json
from typing import Dict, Any, Optional

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 20


def register(email: str, password: str, role: str = "student") -> Dict[str, Any]:
    payload = {
        "email": email,
        "password": password,
        "full_name": email.split("@")[0],
        "role": role,
    }
    r = requests.post(f"{API_BASE_URL}/auth/register", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def login(email: str, password: str) -> Dict[str, Any]:
    r = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def auth_headers(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}


def request_verification(token: str) -> Dict[str, Any]:
    r = requests.post(f"{API_BASE_URL}/auth/verify/request", headers=auth_headers(token), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else {}


def confirm_verification(verification_token: str) -> Dict[str, Any]:
    r = requests.get(
        f"{API_BASE_URL}/auth/verify/confirm",
        params={"token": verification_token},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json() if r.content else {}


def test_user_flow(label: str, email: str, password: str, role: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"label": label, "email": email, "ok": False, "details": {}}
    try:
        try:
            auth = login(email, password)
        except requests.HTTPError as e:
            # Attempt auto-register then login
            if e.response is not None and e.response.status_code in (400, 401, 404):
                reg = register(email, password, role=role)
                out["details"]["auto_registered"] = True
                auth = {"access_token": reg.get("access_token"), "user": reg.get("user")}
                if not auth.get("access_token"):
                    # if register doesn't return tokens, try login now
                    auth = login(email, password)
            else:
                raise
        out["details"]["login_user"] = auth.get("user")
        access = auth.get("access_token")
        if not access:
            raise RuntimeError("No access_token in login response")

        try:
            req = request_verification(access)
            out["details"]["request_response"] = req
        except requests.HTTPError as e:
            if e.response is not None:
                out["details"]["request_error_status"] = e.response.status_code
                try:
                    out["details"]["request_error_body_json"] = e.response.json()
                except Exception:
                    out["details"]["request_error_body_text"] = e.response.text
            raise
        token = req.get("verification_token")
        if not token:
            # Fallback: sometimes only verify_url is returned
            verify_url = req.get("verify_url")
            if verify_url and "token=" in verify_url:
                token = verify_url.split("token=")[-1]
        if not token:
            raise RuntimeError("No verification_token or verify_url provided by backend")

        conf = confirm_verification(token)
        out["details"]["confirm_response"] = conf

        # Expect user JSON with is_verified True
        is_verified = bool(conf.get("is_verified") or conf.get("user", {}).get("is_verified"))
        out["ok"] = is_verified
        out["verified"] = is_verified
        return out
    except Exception as e:
        out["error"] = str(e)
        return out


def main() -> int:
    required = [
        ("STUDENT_EMAIL", os.environ.get("STUDENT_EMAIL")),
        ("STUDENT_PASSWORD", os.environ.get("STUDENT_PASSWORD") or "Test@1234"),
    ]
    missing = [k for k, v in required if not v]
    if missing:
        print("Missing env vars: " + ", ".join(missing), file=sys.stderr)
        print(__doc__)
        return 2

    student = test_user_flow("student", os.environ["STUDENT_EMAIL"], os.environ.get("STUDENT_PASSWORD", "Test@1234"), role="student")

    employer: Dict[str, Any] = {"skipped": True}
    emp_email = os.environ.get("EMPLOYER_EMAIL")
    emp_pass = os.environ.get("EMPLOYER_PASSWORD") or "Test@1234"
    if emp_email:
        employer = test_user_flow("employer", emp_email, emp_pass, role="employer")

    summary = {
        "api_base_url": API_BASE_URL,
        "student": student,
        "employer": employer,
        "all_ok": bool(student.get("ok") and (employer.get("skipped") or employer.get("ok"))),
    }

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
