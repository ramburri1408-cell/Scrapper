"""
Company Discovery Phase 1

Goal:
- Build 10,000+ company target database
- No Apify
- No paid scraping
- Creates data/companies.json

Sources:
1. SEC public company ticker list
2. Manual tech/staffing seed list
3. Domain guessing
4. Career URL guessing

Output:
data/companies.json
"""

import json
import re
import time
import requests
from pathlib import Path
from urllib.parse import urlparse

OUTPUT_FILE = Path("data/companies.json")

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

HEADERS = {
    "User-Agent": "RamBurriJobAgent/1.0 ram.burri1408@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}

TECH_KEYWORDS = [
    "software",
    "systems",
    "technology",
    "technologies",
    "digital",
    "cloud",
    "data",
    "analytics",
    "cyber",
    "security",
    "ai",
    "automation",
    "solutions",
    "consulting",
    "semiconductor",
    "network",
    "communications",
    "interactive",
    "computer",
    "information",
]

TECH_SEED_COMPANIES = [
    "Microsoft",
    "Google",
    "Apple",
    "Amazon",
    "Meta",
    "Netflix",
    "Salesforce",
    "Oracle",
    "Adobe",
    "ServiceNow",
    "Workday",
    "Snowflake",
    "Datadog",
    "MongoDB",
    "Atlassian",
    "Stripe",
    "Twilio",
    "Uber",
    "Airbnb",
    "DoorDash",
    "Block",
    "PayPal",
    "Fiserv",
    "Fidelity",
    "Capital One",
    "JPMorgan Chase",
    "Bank of America",
    "Wells Fargo",
    "Cognizant",
    "Infosys",
    "TCS",
    "Wipro",
    "Accenture",
    "Deloitte",
    "Capgemini",
    "EPAM",
    "Globant",
    "Apex Systems",
    "TEKsystems",
    "Insight Global",
    "Motion Recruitment",
    "Robert Half",
    "Kforce",
    "BCforward",
    "Akkodis",
    "Judge Group",
    "Randstad Digital",
]


def clean_name(name: str) -> str:
    name = str(name or "").strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s*/.*$", "", name)
    return name


def slug_company(name: str) -> str:
    text = name.lower()
    text = re.sub(
        r"\b(inc|inc\.|corp|corp\.|corporation|co|co\.|company|llc|ltd|plc|"
        r"group|holdings|holding|class a|class b|common stock|ordinary shares)\b",
        "",
        text,
    )
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def guess_domain(name: str) -> str:
    slug = slug_company(name)
    if not slug:
        return ""
    return f"{slug}.com"


def domain_responds(domain: str) -> bool:
    if not domain:
        return False

    for scheme in ["https", "http"]:
        try:
            res = requests.get(
                f"{scheme}://{domain}",
                headers=HEADERS,
                timeout=6,
                allow_redirects=True,
            )
            if res.status_code < 500:
                return True
        except Exception:
            continue

    return False


def guess_career_urls(domain: str) -> list:
    if not domain:
        return []

    return [
        f"https://{domain}/careers",
        f"https://{domain}/jobs",
        f"https://{domain}/careers/jobs",
        f"https://careers.{domain}",
        f"https://jobs.{domain}",
    ]


def detect_career_url(domain: str) -> str:
    for url in guess_career_urls(domain):
        try:
            res = requests.get(
                url,
                headers=HEADERS,
                timeout=6,
                allow_redirects=True,
            )

            if res.status_code < 400:
                text = res.text.lower()[:5000]

                if any(k in text for k in ["job", "career", "opening", "position", "apply"]):
                    return res.url

        except Exception:
            continue

    return ""


def is_likely_tech_company(name: str) -> bool:
    n = name.lower()
    return any(k in n for k in TECH_KEYWORDS)


def load_existing() -> dict:
    if OUTPUT_FILE.exists():
        rows = json.loads(OUTPUT_FILE.read_text())
        return {row["company"].lower(): row for row in rows}
    return {}


def save_companies(companies: dict):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    rows = list(companies.values())
    rows.sort(key=lambda x: (not x.get("is_likely_tech"), x["company"]))

    OUTPUT_FILE.write_text(json.dumps(rows, indent=2))

    print(f"\nSaved {len(rows)} companies to {OUTPUT_FILE}")


def add_company(
    companies: dict,
    name: str,
    source: str,
    ticker: str = "",
    cik: str = "",
    force_tech: bool = False,
):
    name = clean_name(name)

    if not name or len(name) < 2:
        return

    key = name.lower()

    if key in companies:
        companies[key]["sources"] = sorted(set(companies[key].get("sources", []) + [source]))
        return

    domain = guess_domain(name)
    domain_valid = domain_responds(domain)

    if not domain_valid:
        domain = ""

    career_url = detect_career_url(domain) if domain else ""

    companies[key] = {
        "company": name,
        "ticker": ticker,
        "cik": cik,
        "domain": domain,
        "career_url": career_url,
        "sources": [source],
        "is_likely_tech": force_tech or is_likely_tech_company(name),
        "active_hiring": None,
        "ats_platform": "",
        "last_checked": "",
    }


def collect_sec_companies(companies: dict):
    print("[SEC] Fetching public company ticker list...")

    res = requests.get(SEC_TICKERS_URL, headers=HEADERS, timeout=30)
    res.raise_for_status()

    data = res.json()
    count = 0

    for item in data.values():
        name = item.get("title", "")
        ticker = item.get("ticker", "")
        cik = str(item.get("cik_str", ""))

        add_company(
            companies,
            name=name,
            ticker=ticker,
            cik=cik,
            source="sec_company_tickers",
            force_tech=False,
        )

        count += 1

        if count % 100 == 0:
            print(f"  SEC processed: {count}")

        time.sleep(0.05)

    print(f"[SEC] Added/updated {count} companies")


def collect_seed_companies(companies: dict):
    print("[Seed] Adding tech/staffing seed companies...")

    for name in TECH_SEED_COMPANIES:
        add_company(
            companies,
            name=name,
            source="manual_tech_seed",
            force_tech=True,
        )

    print(f"[Seed] Added {len(TECH_SEED_COMPANIES)} seed companies")


def run_company_discovery():
    companies = load_existing()

    collect_seed_companies(companies)
    collect_sec_companies(companies)

    save_companies(companies)

    total = len(companies)
    tech = sum(1 for c in companies.values() if c.get("is_likely_tech"))
    with_domain = sum(1 for c in companies.values() if c.get("domain"))
    with_career = sum(1 for c in companies.values() if c.get("career_url"))

    print("\nCompany Discovery Summary")
    print(f"Total companies      : {total}")
    print(f"Likely tech companies: {tech}")
    print(f"Domains found        : {with_domain}")
    print(f"Career pages found   : {with_career}")

    return total


if __name__ == "__main__":
    run_company_discovery()
