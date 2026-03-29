from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import ipaddress

app = FastAPI(title="ifconfig.7it.vn")

# Static files (UI)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# -----------------------
# Helpers
# -----------------------
def is_cli(request: Request) -> bool:
    ua = (request.headers.get("user-agent") or "").lower()
    return ua.startswith("curl/") or ua.startswith("wget/") or "httpie" in ua


def _first_ip_from_xff(xff: str | None) -> str | None:
    if not xff:
        return None
    return xff.split(",")[0].strip() or None


def get_client_ip(request: Request) -> str:
    return (
        request.headers.get("cf-connecting-ip")
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


# -----------------------
# Routes
# -----------------------

@app.get("/", response_class=PlainTextResponse)
def root(request: Request):
    # CLI → trả IP thẳng
    if is_cli(request):
        return get_client_ip(request)

    # Browser → trả UI HTML
    return FileResponse("app/static/index.html")


@app.get("/api/info")
def api_info(request: Request):
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


@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"
