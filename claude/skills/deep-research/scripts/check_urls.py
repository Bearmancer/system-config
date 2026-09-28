"""Audit URLs before they reach the user. Prints: STATUS FLAG FINAL_URL <- INPUT_URL.

Usage: python check_urls.py <url> [<url> ...]   |   python check_urls.py -f file.md   (extracts every http(s) URL)
FLAG: OK | BROKEN | JS? (verify with firecrawl_scrape) | BLOCKED (403/429: verify with firecrawl_scrape)
Exit 1 if any URL is not OK.
"""
import re, sys, urllib.request, urllib.error
from urllib.parse import urlparse, quote

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`|]+")
SOFT_404 = re.compile(rb"page not found|404 not found|doesn.t exist|no longer available", re.I)
PLACEHOLDER = re.compile(r"…|\.\.\.|XXXX|<|\{|/example\b|example\.(com|org)|://mcp\.|/mcp(\?|$)|localhost|127\.0\.0\.1")
JS_SHELL = re.compile(rb"enable javascript|requires javascript|<noscript>|id=\"(root|app|__next)\"", re.I)


def check(url):
    url = quote(url, safe=":/?#[]@!$&'()*+,;=%~")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body, final, code = r.read(300_000), r.geturl(), r.status
    except urllib.error.HTTPError as e:
        return e.code, ("BLOCKED" if e.code in (401, 403, 429, 503) else "BROKEN"), url
    except Exception as e:
        return 0, f"BROKEN({type(e).__name__})", url
    # Redirect to a site root from a deep link usually means the page is gone.
    if urlparse(url).path.strip("/") and not urlparse(final).path.strip("/"):
        return code, "BROKEN(redirect-to-root)", final
    if SOFT_404.search(body[:20_000]):
        return code, "BROKEN(soft-404)", final
    text = re.sub(rb"<script.*?</script>|<style.*?</style>|<[^>]+>", b" ", body, flags=re.S)
    if JS_SHELL.search(body) and len(text.split()) < 150:
        return code, "JS?", final
    return code, "OK", final


def main():
    args = sys.argv[1:]
    if args[:1] == ["-f"]:
        urls = URL_RE.findall(open(args[1], encoding="utf8").read())
    else:
        urls = args
    urls = [u.rstrip(".,;:") for u in dict.fromkeys(urls)]
    # Doc templates carry placeholder URLs; auditing them only produces noise.
    urls = [u for u in urls if urlparse(u).netloc and not PLACEHOLDER.search(u)]
    bad = 0
    for u in urls:
        code, flag, final = check(u)
        bad += flag != "OK"
        print(f"{code} {flag} {final} <- {u}" if final != u else f"{code} {flag} {u}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
