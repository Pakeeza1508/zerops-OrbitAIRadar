import ipaddress
import socket
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {
    "fbclid",
    "gclid",
    "gclsrc",
    "dclid",
    "msclkid",
    "mc_cid",
    "mc_eid",
    "igshid",
    "ref",
    "ref_src",
    "source",
    "_hsenc",
    "_hsmi",
    "yclid",
    "wickedid",
}

BLOCKED_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".zip",
    ".mp4",
    ".mp3",
    ".css",
    ".js",
)


def canonicalize_url(url: str) -> str:
    """Normalize a URL: strip tracking params, fragments, trailing slash, lowercase host."""
    if not url:
        return ""
    url = url.strip()
    parsed = urlparse(url)
    scheme = (parsed.scheme or "https").lower()
    if scheme not in ("http", "https"):
        return ""
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    if netloc.endswith(":80") or netloc.endswith(":443"):
        netloc = netloc.rsplit(":", 1)[0]

    query_pairs = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=False)
        if k.lower() not in TRACKING_KEYS
        and not any(k.lower().startswith(p) for p in TRACKING_PREFIXES)
    ]
    query = urlencode(sorted(query_pairs))

    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    return urlunparse((scheme, netloc, path, "", query, ""))


def domain_of(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def is_public_http_url(url: str) -> bool:
    """SSRF guard: only public http(s) hosts, no private/loopback addresses."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    host = parsed.hostname
    if host in ("localhost",) or host.endswith(".local") or host.endswith(".internal"):
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    return True


def looks_like_content_url(url: str) -> bool:
    lowered = url.lower()
    if any(lowered.endswith(ext) for ext in BLOCKED_EXTENSIONS):
        return False
    path = urlparse(lowered).path
    return len(path) > 8
