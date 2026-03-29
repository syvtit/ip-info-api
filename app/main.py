from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import ipaddress

app = FastAPI(title="ifconfig.7it.vn")

# UI
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


# -----------------------
# Helpers
# -----------------------
def _first_ip_from_xff(xff: str | None) -> str | None:
    if not xff:
        return None
    return xff.split(",")[0].strip() or None


def get_client_ip(request: Request) -> str:
    return (
        request.headers.get("cf-connecting-ip")  # Cloudflare
        or _first_ip_from_xff(request.headers.get("x-forwarded-for"))
        or request.client.host
    )


def ip_meta(ip: str) -> dict:
    try:
        obj = ipaddress.ip_address(ip)
        return {
            "version": "IPv4" if obj.version == 4 else "IPv6",
            "scope": "private" if obj.is_private else "public",
        }
    except ValueError:
        return {"version": "unknown", "scope": "unknown"}


def is_cli(request: Request) -> bool:
    ua = (request.headers.get("user-agent") or "").lower()
    return any(x in ua for x in ["curl", "wget", "httpie"])


# -----------------------
# Routes
# -----------------------

@app.get("/", response_class=PlainTextResponse)
def root(request: Request):
    """
    Smart root:
    - CLI → trả IP (giống ifconfig.io)
    - Browser → redirect UI
    """
    if is_cli(request):
        return get_client_ip(request)

    return RedirectResponse("/ui", status_code=307)


@app.get("/raw", response_class=PlainTextResponse)
def raw(request: Request):
    """Machine-friendly"""
    return get_client_ip(request)


@app.get("/json", response_class=JSONResponse)
def json_api(request: Request):
    """API-friendly"""
    ip = get_client_ip(request)
    meta = ip_meta(ip)

    xff = request.headers.get("x-forwarded-for")
    chain = [s.strip() for s in xff.split(",")] if xff else [ip]

    return {
        "ip": ip,
        "version": meta["version"],
        "scope": meta["scope"],
        "proxy_chain": chain,
        "user_agent": request.headers.get("user-agent"),
    }


@app.get("/headers", response_class=JSONResponse)
def headers(request: Request):
    """Debug headers"""
    return dict(request.headers)


@app.get("/health", response_class=JSONResponse)
def health():
    return {"status": "ok"}


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return FileResponse("app/static/robots.txt", media_type="text/plain")


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    return FileResponse("app/static/sitemap.xml", media_type="application/xml")
