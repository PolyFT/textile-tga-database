#!/usr/bin/env python3
"""Discover papers likely to contain paired textile TGA/LOI data and extract reviewable evidence.

This script does not promote data directly into the scientific master table.
It writes a candidate evidence queue for later verification.
"""

from __future__ import annotations
import argparse
import html
import json
import re
import time
from pathlib import Path
from io import BytesIO
from urllib.parse import urlparse, urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "automation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "candidate_extractions.csv"

SEARCH_TERMS = [
    '"flame retardant" fabric LOI thermogravimetric',
    '"limiting oxygen index" textile TGA',
    'cotton fabric flame retardant LOI TGA',
    'polyester fabric flame retardant LOI TGA',
    'polyamide nylon fabric flame retardant LOI TGA',
    'viscose lyocell fabric flame retardant LOI TGA',
    'wool silk fabric flame retardant LOI TGA',
    'aramid protective textile LOI thermogravimetric',
    'upholstery automotive textile flame retardant LOI TGA',
    'mattress ticking textile flame retardant thermogravimetric LOI',
]

TG_TERMS = re.compile(
    r'\b(TGA|TG/DTG|DTG|thermogravimetric|thermogravimetry|thermal degradation|char residue|residual mass|Tmax|T_?5\b|T_?10\b|T_?50\b)',
    re.I,
)
LOI_TERMS = re.compile(r'\b(LOI|limiting oxygen index|oxygen index)\b', re.I)
TEXTILE_TERMS = re.compile(
    r'\b(fabric|textile|fiber|fibre|nonwoven|woven|knitted|yarn|cotton|polyester|PET|nylon|polyamide|viscose|lyocell|wool|silk|aramid|upholstery|curtain|mattress)\b',
    re.I,
)
NUMERIC_TG = re.compile(
    r'(?:(?:T(?:d[, ]*)?(?:5|10|20|40|50)|Tmax|peak temperature)[^.;:\n]{0,35}?(\d{2,4}(?:\.\d+)?)\s*°?\s*C)'
    r'|(?:(?:residue|residual mass|char yield)[^.;:\n]{0,45}?(\d{1,3}(?:\.\d+)?)\s*(?:wt\.?\s*)?%)',
    re.I,
)
NUMERIC_LOI = re.compile(
    r'(?:LOI|limiting oxygen index|oxygen index)[^.;:\n]{0,50}?'
    r'(?:(?:of|=|:|was|to|from|reached|increased to|decreased to)\s*)?'
    r'(\d{1,2}(?:\.\d+)?)\s*(?:vol\.?\s*)?%',
    re.I,
)

HEADERS = {
    "User-Agent": "textile-tga-database/1.0 (public academic data curation; GitHub PolyFT/textile-tga-database)"
}


def norm_doi(value: str | None) -> str:
    if not value:
        return ""
    x = str(value).strip().lower()
    x = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', x)
    x = re.sub(r'^doi:\s*', '', x)
    return x.rstrip(' .;,')


def existing_dois() -> set[str]:
    out: set[str] = set()
    for p in (ROOT / "data").rglob("*.csv"):
        if p == OUT:
            continue
        try:
            df = pd.read_csv(p, dtype=str, low_memory=False)
        except Exception:
            continue
        for col in df.columns:
            if col.lower() == "doi":
                out.update(norm_doi(v) for v in df[col].dropna() if norm_doi(v))
    return out


def inverted_abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pairs = []
    for token, positions in inv.items():
        for pos in positions:
            pairs.append((pos, token))
    return " ".join(tok for _, tok in sorted(pairs))


def openalex_search(term: str, per_page: int = 50) -> list[dict]:
    params = {
        "search": term,
        "per-page": min(per_page, 100),
        "select": "id,doi,title,publication_year,primary_location,best_oa_location,open_access,abstract_inverted_index",
    }
    r = requests.get("https://api.openalex.org/works", params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])


def europe_pmc_fulltext(doi: str) -> tuple[str, str]:
    if not doi:
        return "", ""
    try:
        q = requests.get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": f'DOI:"{doi}"', "format": "json", "pageSize": 5},
            headers=HEADERS, timeout=25,
        )
        q.raise_for_status()
        for item in q.json().get("resultList", {}).get("result", []):
            pmcid = item.get("pmcid")
            if not pmcid:
                continue
            x = requests.get(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML",
                headers=HEADERS, timeout=30,
            )
            if x.ok and len(x.text) > 1000:
                soup = BeautifulSoup(x.text, "xml")
                return soup.get_text(" ", strip=True), f"https://europepmc.org/articles/{pmcid}"
    except requests.RequestException:
        pass
    return "", ""


ALLOW_HTML_HOSTS = {
    "pmc.ncbi.nlm.nih.gov",
    "www.mdpi.com",
    "mdpi.com",
    "pubs.rsc.org",
    "www.frontiersin.org",
    "link.springer.com",
}


SUPP_HINT = re.compile(r'(supplement|supporting|additional\s+file|ESI|Table\s*S\d|Figure\s*S\d)', re.I)

def fetch_open_html(url: str) -> tuple[str, list[str], list[str]]:
    if not url:
        return "", [], []
    try:
        host = urlparse(url).netloc.lower()
        if host not in ALLOW_HTML_HOSTS:
            return "", [], []
        r = requests.get(url, headers=HEADERS, timeout=30)
        if not r.ok or "text/html" not in r.headers.get("content-type", ""):
            return "", [], []
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(" ", strip=True)
        tables = []
        try:
            for df in pd.read_html(r.text):
                cols = " ".join(map(str, df.columns))
                blob = cols + " " + df.astype(str).head(60).to_csv(index=False)
                if LOI_TERMS.search(blob) or TG_TERMS.search(blob):
                    tables.append(blob[:6000])
        except Exception:
            pass

        supp_links = []
        for a in soup.find_all("a", href=True):
            label = " ".join(a.stripped_strings)
            href = a.get("href", "")
            probe = f"{label} {href}"
            ext_hit = re.search(r'(supp|esi|support).*(pdf|xlsx|xls|csv)$', href, re.I)
            if SUPP_HINT.search(probe) or ext_hit:
                u = urljoin(url, href)
                h = urlparse(u).netloc.lower()
                if h == host or h in ALLOW_HTML_HOSTS:
                    if u not in supp_links:
                        supp_links.append(u)
        return text, tables[:8], supp_links[:8]
    except requests.RequestException:
        return "", [], []


def fetch_supplements(links: list[str]) -> tuple[str, list[str]]:
    texts = []
    tables = []
    for url in links[:4]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=35)
            if not r.ok or len(r.content) > 12_000_000:
                continue
            ctype = r.headers.get("content-type", "").lower()
            path = urlparse(url).path.lower()
            if "pdf" in ctype or path.endswith(".pdf"):
                reader = PdfReader(BytesIO(r.content))
                text = " ".join((p.extract_text() or "") for p in reader.pages[:30])
                if text:
                    texts.append(text[:120000])
            elif "csv" in ctype or path.endswith(".csv"):
                df = pd.read_csv(BytesIO(r.content))
                blob = df.head(100).to_csv(index=False)
                if LOI_TERMS.search(blob) or TG_TERMS.search(blob):
                    tables.append(blob[:12000])
            elif path.endswith((".xlsx", ".xls")) or "spreadsheet" in ctype or "excel" in ctype:
                book = pd.read_excel(BytesIO(r.content), sheet_name=None)
                for name, df in list(book.items())[:8]:
                    blob = f"sheet={name}\n" + df.head(100).to_csv(index=False)
                    if LOI_TERMS.search(blob) or TG_TERMS.search(blob):
                        tables.append(blob[:12000])
        except Exception:
            continue
    return " ".join(texts), tables[:10]

def short_evidence(text: str, pattern: re.Pattern, radius: int = 150, max_items: int = 5) -> list[str]:
    items = []
    for m in pattern.finditer(text):
        a = max(0, m.start() - radius)
        b = min(len(text), m.end() + radius)
        snippet = re.sub(r'\s+', ' ', html.unescape(text[a:b])).strip()
        if snippet not in items:
            items.append(snippet)
        if len(items) >= max_items:
            break
    return items


def choose_oa_url(work: dict) -> str:
    loc = work.get("best_oa_location") or {}
    for key in ("landing_page_url", "pdf_url"):
        if loc.get(key):
            return loc[key]
    loc = work.get("primary_location") or {}
    return loc.get("landing_page_url") or ""


def score_candidate(text: str, tables: list[str], title: str) -> tuple[int, list[str], list[str]]:
    corpus = f"{title} {text} {' '.join(tables)}"
    score = 0
    if TEXTILE_TERMS.search(corpus):
        score += 2
    if TG_TERMS.search(corpus):
        score += 3
    if LOI_TERMS.search(corpus):
        score += 3
    loi_ev = short_evidence(corpus, NUMERIC_LOI)
    tg_ev = short_evidence(corpus, NUMERIC_TG)
    score += min(len(loi_ev), 3) * 2
    score += min(len(tg_ev), 3) * 2
    if tables:
        score += 2
    return score, loi_ev, tg_ev


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-new", type=int, default=200)
    ap.add_argument("--per-query", type=int, default=50)
    args = ap.parse_args()

    known = existing_dois()
    previous = pd.read_csv(OUT, dtype=str).fillna("") if OUT.exists() else pd.DataFrame()
    seen = set(previous.get("DOI", pd.Series(dtype=str)).map(norm_doi)) | known

    rows = []
    discovered = {}
    for term in SEARCH_TERMS:
        try:
            works = openalex_search(term, args.per_query)
        except Exception as exc:
            print(f"OpenAlex search failed for {term}: {exc}")
            continue
        for w in works:
            doi = norm_doi(w.get("doi"))
            key = doi or w.get("id") or w.get("title")
            if not key or key in discovered:
                continue
            discovered[key] = w

    for key, w in discovered.items():
        if len(rows) >= args.max_new:
            break
        doi = norm_doi(w.get("doi"))
        if doi and doi in seen:
            continue
        title = (w.get("title") or "").strip()
        abstract = inverted_abstract(w.get("abstract_inverted_index"))
        prelim = f"{title} {abstract}"
        if not (TEXTILE_TERMS.search(prelim) and (TG_TERMS.search(prelim) or LOI_TERMS.search(prelim))):
            continue

        fulltext, fulltext_url = europe_pmc_fulltext(doi)
        tables: list[str] = []
        supp_links: list[str] = []
        oa_url = choose_oa_url(w)
        if not fulltext:
            fulltext, tables, supp_links = fetch_open_html(oa_url)
            fulltext_url = oa_url if fulltext else ""
        else:
            _, page_tables, supp_links = fetch_open_html(oa_url)
            tables.extend(page_tables)
        supp_text, supp_tables = fetch_supplements(supp_links)
        tables.extend(supp_tables)
        combined = " ".join(x for x in [fulltext if fulltext else abstract, supp_text] if x)
        score, loi_ev, tg_ev = score_candidate(combined, tables, title)

        if score < 7:
            continue

        primary = w.get("primary_location") or {}
        source = primary.get("source") or {}
        oa = w.get("open_access") or {}
        status = "ready_for_review" if loi_ev and tg_ev else (
            "fulltext_found_partial" if fulltext else "metadata_only"
        )
        rows.append({
            "DOI": doi,
            "title": title,
            "year": w.get("publication_year") or "",
            "journal": source.get("display_name") or "",
            "openalex_id": w.get("id") or "",
            "landing_url": primary.get("landing_page_url") or "",
            "oa_url": choose_oa_url(w),
            "oa_status": oa.get("oa_status") or "",
            "fulltext_url": fulltext_url,
            "fulltext_found": bool(fulltext),
            "candidate_score": score,
            "status": status,
            "LOI_numeric_evidence": json.dumps(loi_ev, ensure_ascii=False),
            "TG_numeric_evidence": json.dumps(tg_ev, ensure_ascii=False),
            "supplementary_links": json.dumps(supp_links, ensure_ascii=False),
            "supplementary_content_found": bool(supp_text or supp_tables),
            "table_candidates": json.dumps(tables, ensure_ascii=False),
            "abstract_excerpt": re.sub(r'\s+', ' ', abstract)[:800],
        })
        if doi:
            seen.add(doi)
        time.sleep(0.1)

    if not rows:
        print("No new high-value candidates found.")
        return

    new = pd.DataFrame(rows)
    if not previous.empty:
        all_df = pd.concat([previous, new], ignore_index=True, sort=False)
    else:
        all_df = new
    if "DOI" in all_df:
        all_df["_doi_norm"] = all_df["DOI"].map(norm_doi)
        all_df = all_df.sort_values(["candidate_score"], ascending=False)
        all_df = all_df.drop_duplicates(subset=["_doi_norm"], keep="first")
        all_df = all_df.drop(columns=["_doi_norm"])
    all_df.to_csv(OUT, index=False)
    print(f"Added {len(new)} reviewable candidates; queue now {len(all_df)} rows.")


if __name__ == "__main__":
    main()
