"""Validation for externally opened job-posting URLs."""

from urllib.parse import urlparse


def validate_job_url(url: str) -> str:
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Job URL must be a valid http:// or https:// address.")
    return cleaned
