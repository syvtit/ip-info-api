from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import ipaddress

app = FastAPI()


def get_ip_info(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")

    if x_forwarded_for:
        ip_list = [ip.strip() for ip in x_forwarded_for.split(",")]
        real_ip = ip_list[0]
        proxy_chain = ip_list
    else:
        real_ip = request.client.host
        proxy_chain = []

    return real_ip, proxy_chain, x_forwarded_for


@app.get("/", response_class=PlainTextResponse)
def info(request: Request):
    ip, proxy_chain, xff = get_ip_info(request)

    try:
        ip_obj = ipaddress.ip_address(ip)
        version = "IPv4" if ip_obj.version == 4 else "IPv6"
        is_private = ip_obj.is_private
        is_global = ip_obj.is_global
    except:
        version = "Unknown"
        is_private = "N/A"
        is_global = "N/A"

    ipv4 = ip if "." in ip else "N/A"
    ipv6 = ip if ":" in ip else "N/A"

    user_agent = request.headers.get("user-agent", "unknown")

    output = f"""
ip: {ip}
ipv4: {ipv4}
ipv6: {ipv6}
version: {version}
private: {is_private}
global: {is_global}

x-forwarded-for: {xff}
proxy-chain: {proxy_chain}

user-agent: {user_agent}
"""

    return output.strip()
