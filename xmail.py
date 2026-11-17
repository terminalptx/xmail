#!/usr/bin/env python3
"""xmail : renseignements sur une adresse e-mail (OSINT)."""
#~/bin/xmail
import argparse, hashlib, json, os, re, shutil, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests

UA = {"User-Agent": "xmail/1.0"}
EMAIL_RE = re.compile(r"^[^@\s]+@([^@\s]+\.[^@\s]+)$")
DISPOSABLE = {"yopmail.com", "mailinator.com", "guerrillamail.com", "10minutemail.com", "temp-mail.org"}


def check_domain(email):
    domain = EMAIL_RE.match(email).group(1).lower()
    result = {"domain": domain, "disposable": domain in DISPOSABLE, "mx": []}
    try:
        import dns.resolver
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        result["mx"] = sorted(str(r.exchange).rstrip(".") for r in answers)
    except Exception as exc:
        result["error"] = f"MX introuvable : {exc.__class__.__name__}"
    return result


def check_gravatar(email):
    digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()
    r = requests.get(f"https://gravatar.com/{digest}.json", headers=UA, timeout=10)
    if r.status_code != 200:
        return {"found": False}
    entry = r.json()["entry"][0]
    return {
        "found": True,
        "name": entry.get("displayName"),
        "photo": entry.get("thumbnailUrl"),
        "location": entry.get("currentLocation"),
        "links": [u.get("value") for u in entry.get("urls", [])],
        "accounts": [a.get("url") for a in entry.get("accounts", [])],
    }


def check_accounts(email):
    if not shutil.which("holehe"):
        return {"error": "holehe absent (pipx install holehe)"}
    out = subprocess.run(["holehe", "--only-used", "--no-color", "--no-clear", email],
                         capture_output=True, text=True, timeout=300).stdout
    # holehe affiche "[+] site.com" pour chaque compte trouvé
    return {"used": sorted({line[4:].strip() for line in out.splitlines() if line.startswith("[+] ")
                            and "Email used" not in line})}


def check_breaches(email):
    key = os.environ.get("HIBP_API_KEY")
    if not key:
        return {"skipped": "définir HIBP_API_KEY pour activer"}
    r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}",
                     headers={**UA, "hibp-api-key": key}, params={"truncateResponse": "false"}, timeout=15)
    if r.status_code == 404:
        return {"breaches": []}
    r.raise_for_status()
    return {"breaches": [{"name": b["Name"], "date": b["BreachDate"], "data": b["DataClasses"]} for b in r.json()]}


def web_search(email):
    user, domain = email.split("@")
    dorks = [f'"{email}"', f'"{email}" filetype:pdf', f'"{user}" site:github.com',
             f'"{email}" site:pastebin.com', f'"{user}" "{domain}"']
    result = {"dorks": [f"https://www.google.com/search?q={urllib.parse.quote(d)}" for d in dorks]}
    searx = os.environ.get("SEARXNG_URL")  # ex. https://searx.exemple.org
    if searx:
        r = requests.get(f"{searx}/search", params={"q": f'"{email}"', "format": "json"}, headers=UA, timeout=15)
        result["results"] = [{"title": x["title"], "url": x["url"]} for x in r.json().get("results", [])[:20]]
    return result


MODULES = {"domaine": check_domain, "gravatar": check_gravatar, "comptes": check_accounts,
           "fuites": check_breaches, "web": web_search}


def main():
    parser = argparse.ArgumentParser(description="Renseignements sur une adresse e-mail")
    parser.add_argument("email")
    parser.add_argument("-o", "--output", help="fichier JSON du rapport")
    args = parser.parse_args()
    email = args.email.strip().lower()
    if not EMAIL_RE.match(email):
        sys.exit("Adresse invalide.")

    report = {"email": email, "date": datetime.now().isoformat(timespec="seconds")}
    with ThreadPoolExecutor(max_workers=len(MODULES)) as pool:
        futures = {name: pool.submit(fn, email) for name, fn in MODULES.items()}
        for name, future in futures.items():
            try:
                report[name] = future.result()
            except Exception as exc:
                report[name] = {"error": str(exc)}
            print(f"\n== {name} ==\n{json.dumps(report[name], indent=2, ensure_ascii=False)}")

    out = Path(args.output or Path.home() / "loot" / f"xmail-{email}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nRapport : {out}")


if __name__ == "__main__":
    main()
