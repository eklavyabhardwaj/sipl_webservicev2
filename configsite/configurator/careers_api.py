# configurator/careers_api.py
from typing import List, Dict, Optional
import requests
import pandas as pd
from .models import ERPSettings  # admin-managed creds
import os

JOB_OPENING_ENDPOINT   = "api/resource/Job Opening"
JOB_APPLICANT_ENDPOINT = "api/resource/Job Applicant"

def _get_erp():
    erp = ERPSettings.objects.first()
    if not erp or not erp.is_enabled:
        raise RuntimeError("ERP disabled or not configured in admin.")
    base = erp.base_url.rstrip("/")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {erp.api_key}:{erp.api_secret}",
    }
    return base, headers

def fetch_job_list() -> List[Dict]:
    try:
        base, headers = _get_erp()
        url = f"{base}/{JOB_OPENING_ENDPOINT}"
        params = {
            'fields': '["name","designation","status","custom_territory","custom_qualification"]',
            'limit_start': 0,
            'limit_page_length': 999999999
        }
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        df = pd.DataFrame(data)
        if not df.empty and "status" in df.columns:
            df = df[df["status"] == "Open"]
            return df.to_dict(orient="records")
        return []
    except Exception:
        return []

def fetch_job_details(job_id: str) -> Optional[Dict]:
    try:
        base, headers = _get_erp()
        url = f"{base}/{JOB_OPENING_ENDPOINT}/{job_id}"
        params = {
            'fields': '["name","description","custom_no_of_vacancy","custom_territory","designation","custom_qualification"]'
        }
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("data")
    except Exception:
        return None

def submit_applicant(payload: Dict, local_resume_path: Optional[str] = None) -> requests.Response:
    """
    Create a Job Applicant, then attach a PDF (resume) directly to that applicant
    using /api/method/upload_file like the curl example.
    """
    base, headers = _get_erp()

    # 1) Create the Job Applicant
    applicant_url = f"{base}/{JOB_APPLICANT_ENDPOINT}"
    create_resp = requests.post(applicant_url, headers=headers, json=payload, timeout=20)
    create_resp.raise_for_status()
    applicant = create_resp.json().get("data", {})
    applicant_name = applicant.get("name")

    # 2) If a resume path is given, attach it like in your curl example
    if applicant_name and local_resume_path and os.path.exists(local_resume_path):
        try:
            upload_url = f"{base}/api/method/upload_file"
            upload_headers = {
                "Authorization": headers["Authorization"]
            }

            with open(local_resume_path, "rb") as f:
                files = {
                    "file": (os.path.basename(local_resume_path), f),
                }
                data = {
                    "doctype": "Job Applicant",
                    "docname": applicant_name,
                    "filename": os.path.basename(local_resume_path),
                    "is_private": "0",   # or "1" for private
                    "fieldname": "resume_attachment",  # <--- add this
                }

                upload_resp = requests.post(
                    upload_url, headers=upload_headers, data=data, files=files, timeout=30
                )
                upload_resp.raise_for_status()
                print("[INFO] File uploaded:", upload_resp.json())

        except Exception as e:
            print(f"[WARN] File upload failed: {e}")

    return create_resp
