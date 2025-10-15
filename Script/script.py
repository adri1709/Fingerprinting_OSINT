
import whois
import requests
import socket
import dns.resolver
import concurrent.futures
import argparse
import time
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime

# ---- PASIVO ----
def whois_lookup(domain):
    try:
        w = whois.whois(domain)
        return dict(w)
    except Exception as e:
        return {"error": str(e)}

def crtsh_search(domain):
    """Busca certificados relacionados en crt.sh (salida JSON)."""
    try:
        q = f"%25{domain}%25"
        url = f"https://crt.sh/?q={q}&output=json"
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            # crt.sh sometimes returns empty or invalid json; guard
            try:
                return r.json()
            except ValueError:
                return {"error": "crt.sh returned non-json content"}
        else:
            return {"error": f"crt.sh returned {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def wayback_snapshots(domain):
    """Consulta la Wayback Machine (disponibilidad básica)."""
    try:
        api = "http://web.archive.org/cdx/search/cdx"
        params = {"url": f"*.{domain}/*", "output": "json", "limit": 50}
        r = requests.get(api, params=params, timeout=20)
        if r.status_code == 200:
            try:
                return r.json()  # matriz de snapshots (puedes procesarla)
            except ValueError:
                return {"error": "Wayback returned non-json content"}
        return {"error": f"Wayback returned {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def github_search_code(query, github_token=None):
    """
    Búsqueda simple de GitHub code search (necesita token para límites razonables).
    Query ejemplo: 'example.com' o 'api-key filename:.env'
    """
    try:
        headers = {"Accept": "application/vnd.github+json"}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        url = "https://api.github.com/search/code"
        params = {"q": query, "per_page": 10}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {"error": f"GitHub API {r.status_code}: {r.text}"}
    except Exception as e:
        return {"error": str(e)}

# ---- ACTIVO ----
def dns_records(domain):
    """A, AAAA, NS, MX, TXT, CNAME (intenta varios tipos)."""
    resolver = dns.resolver.Resolver()
    types = ["A", "AAAA", "NS", "MX", "TXT", "CNAME"]
    out = {}
    for t in types:
        try:
            answers = resolver.resolve(domain, t, lifetime=5)
            out[t] = [str(a.to_text()) for a in answers]
        except Exception as e:
            out[t] = f"error or none: {e}"
    return out

def resolve_host(domain):
    """Equivalente básico a host/dig usando socket."""
    try:
        info = socket.gethostbyname_ex(domain)
        return {"hostname": info[0], "aliases": info[1], "ips": info[2]}
    except Exception as e:
        return {"error": str(e)}

def dir_fuzz(base_url, wordlist_path, threads=20, status_whitelist=(200,301,302,403)):
    """
    Fuzz sencillo de directorios:
      - base_url: 'https://example.com' (sin slash final recomendado)
      - wordlist_path: ruta a wordlist (una entrada por línea)
    Devuelve lista de dicts: {"url":..., "status":..., "length":...}
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "Recon-Fuzzer/1.0"})
    results = []

    # Normalize base_url
    p = urlparse(base_url)
    if not p.scheme:
        base_url = "http://" + base_url

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        words = [w.strip() for w in f if w.strip()]

    def check(path):
        url = urljoin(base_url + "/", path)
        try:
            r = session.get(url, allow_redirects=False, timeout=8)
            if r.status_code in status_whitelist:
                return {"url": url, "status": r.status_code, "length": len(r.content)}
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(check, w): w for w in words}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res:
                results.append(res)

    return results

# ---- UTIL ----
def save_json(data, outpath, pretty=False):
    with open(outpath, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        else:
            json.dump(data, f, ensure_ascii=False, default=str)

# ---- CLI simple ----
def main():
    parser = argparse.ArgumentParser(description="Recon pasivo y activo (salida JSON).")
    parser.add_argument("domain", help="Dominio o URL objetivo (ej: example.com)")
    parser.add_argument("--fuzz", help="Ruta a wordlist para fuzz (dir)")
    parser.add_argument("--github-token", help="Token opcional para GitHub API")
    parser.add_argument("--output", "-o", default="recon_results.json", help="Archivo JSON de salida")
    parser.add_argument("--pretty", action="store_true", help="Formato JSON 'pretty' (indentado)")
    parser.add_argument("--threads", type=int, default=20, help="Threads para fuzz (si se usa fuzz)")
    args = parser.parse_args()

    d = args.domain
    start = time.time()
    timestamp = datetime.utcnow().isoformat() + "Z"

    results = {
        "domain": d,
        "timestamp_utc": timestamp,
        "whois": None,
        "crtsh": None,
        "wayback": None,
        "github_search": None,
        "dns_records": None,
        "resolve_host": None,
        "fuzz_hits": None,
        "runtime_seconds": None
    }

    # WHOIS
    try:
        results["whois"] = whois_lookup(d)
    except Exception as e:
        results["whois"] = {"error": str(e)}

    # crt.sh
    try:
        results["crtsh"] = crtsh_search(d)
    except Exception as e:
        results["crtsh"] = {"error": str(e)}

    # Wayback
    try:
        results["wayback"] = wayback_snapshots(d)
    except Exception as e:
        results["wayback"] = {"error": str(e)}

    # GitHub (opcional)
    if args.github_token:
        try:
            results["github_search"] = github_search_code(d, args.github_token)
        except Exception as e:
            results["github_search"] = {"error": str(e)}

    # DNS records
    try:
        results["dns_records"] = dns_records(d)
    except Exception as e:
        results["dns_records"] = {"error": str(e)}

    # Resolve host
    try:
        results["resolve_host"] = resolve_host(d)
    except Exception as e:
        results["resolve_host"] = {"error": str(e)}

    # Fuzz (opcional)
    if args.fuzz:
        try:
            hits = dir_fuzz(d if d.startswith("http") else ("https://" + d), args.fuzz, threads=args.threads)
            results["fuzz_hits"] = hits
        except Exception as e:
            results["fuzz_hits"] = {"error": str(e)}

    # runtime
    results["runtime_seconds"] = round(time.time() - start, 2)

    # Guardar JSON
    try:
        save_json(results, args.output, pretty=args.pretty)
        print(f"[+] Resultados guardados en {args.output} (pretty={args.pretty})")
    except Exception as e:
        print(f"[!] Error al guardar JSON: {e}")
        # como fallback imprimir JSON a stdout
        print(json.dumps(results, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
