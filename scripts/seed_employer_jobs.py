#!/usr/bin/env python3
"""
Seed placeholder jobs for a specific employer using the existing POST /auth/employer/jobs endpoint.

Usage:
  python scripts/seed_employer_jobs.py --email employer1@example.com --password Karan123 --count 10 --base-url http://localhost:8000

Notes:
- Requires the backend to be running and accessible at base-url.
- Uses the login endpoint to obtain a bearer token, then creates jobs.
"""
import argparse
import json
import sys
from typing import List

import requests


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--count", type=int, default=10)
    p.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Backend base URL (default: http://localhost:8000)",
    )
    return p.parse_args()


def login(base_url: str, email: str, password: str) -> str:
    url = f"{base_url.rstrip('/')}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password})
    if resp.status_code != 200:
        raise SystemExit(f"Login failed ({resp.status_code}): {resp.text}")
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise SystemExit("No access token returned from login")
    return token


def sample_jobs() -> List[dict]:
    # Descriptions should be >= 50 chars due to validation
    long = (
        "We are seeking a motivated professional to join our team. "
        "You will collaborate cross-functionally to deliver high-quality outcomes, "
        "improve processes, and contribute to a positive engineering culture. "
        "Strong communication and a growth mindset are essential."
    )
    return [
        {
            "title": "Software Engineer (Full-Stack)",
            "description": long,
            "city": "Sydney",
            "state": "NSW",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": True,
            "visa_sponsorship": True,
            "international_student_friendly": True,
            "required_skills": ["python", "fastapi", "react", "sql"],
            "preferred_skills": ["aws", "docker", "ci/cd"],
        },
        {
            "title": "Frontend Developer (React)",
            "description": long,
            "city": "Melbourne",
            "state": "VIC",
            "employment_type": "full_time",
            "experience_level": "junior",
            "remote_option": True,
            "visa_sponsorship": False,
            "international_student_friendly": True,
            "required_skills": ["javascript", "react", "css"],
            "preferred_skills": ["typescript", "vite"],
        },
        {
            "title": "Backend Developer (Python/FastAPI)",
            "description": long,
            "city": "Brisbane",
            "state": "QLD",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": False,
            "visa_sponsorship": True,
            "international_student_friendly": False,
            "required_skills": ["python", "fastapi", "postgresql"],
            "preferred_skills": ["sqlalchemy", "redis"],
        },
        {
            "title": "Data Analyst (Entry-Level)",
            "description": long,
            "city": "Adelaide",
            "state": "SA",
            "employment_type": "full_time",
            "experience_level": "entry",
            "remote_option": True,
            "visa_sponsorship": False,
            "international_student_friendly": True,
            "required_skills": ["sql", "excel"],
            "preferred_skills": ["python", "tableau"],
        },
        {
            "title": "DevOps Engineer",
            "description": long,
            "city": "Perth",
            "state": "WA",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": True,
            "visa_sponsorship": True,
            "international_student_friendly": False,
            "required_skills": ["aws", "docker", "kubernetes"],
            "preferred_skills": ["terraform", "prometheus"],
        },
        {
            "title": "Product Manager (Associate)",
            "description": long,
            "city": "Sydney",
            "state": "NSW",
            "employment_type": "full_time",
            "experience_level": "junior",
            "remote_option": False,
            "visa_sponsorship": False,
            "international_student_friendly": True,
            "required_skills": ["roadmapping", "communication"],
            "preferred_skills": ["jira", "analytics"],
        },
        {
            "title": "QA Engineer (Automation)",
            "description": long,
            "city": "Melbourne",
            "state": "VIC",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": True,
            "visa_sponsorship": False,
            "international_student_friendly": True,
            "required_skills": ["selenium", "python", "cypress"],
            "preferred_skills": ["playwright", "ci/cd"],
        },
        {
            "title": "UI/UX Designer",
            "description": long,
            "city": "Canberra",
            "state": "ACT",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": True,
            "visa_sponsorship": False,
            "international_student_friendly": True,
            "required_skills": ["figma", "wireframing", "prototyping"],
            "preferred_skills": ["design systems", "css"],
        },
        {
            "title": "Mobile Developer (React Native)",
            "description": long,
            "city": "Sydney",
            "state": "NSW",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": True,
            "visa_sponsorship": True,
            "international_student_friendly": True,
            "required_skills": ["react native", "javascript"],
            "preferred_skills": ["typescript", "graphql"],
        },
        {
            "title": "Cloud Engineer (AWS)",
            "description": long,
            "city": "Hobart",
            "state": "TAS",
            "employment_type": "full_time",
            "experience_level": "mid",
            "remote_option": True,
            "visa_sponsorship": True,
            "international_student_friendly": False,
            "required_skills": ["aws", "networking", "linux"],
            "preferred_skills": ["python", "terraform"],
        },
    ]


def main():
    args = get_args()
    token = login(args.base_url, args.email, args.password)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    jobs = sample_jobs()[: max(0, args.count)]
    created = []
    for i, job in enumerate(jobs, start=1):
        url = f"{args.base_url.rstrip('/')}/auth/employer/jobs"
        resp = requests.post(url, headers=headers, data=json.dumps(job))
        if resp.status_code not in (200, 201):
            print(f"[{i}] Failed to create job: {resp.status_code} {resp.text}", file=sys.stderr)
            continue
        data = resp.json()
        created.append({"id": data.get("id"), "title": data.get("title")})
        print(f"[{i}] Created job #{data.get('id')}: {data.get('title')}")

    print(f"\nDone. Created {len(created)} job(s).")
    if created:
        print(json.dumps(created, indent=2))


if __name__ == "__main__":
    main()
