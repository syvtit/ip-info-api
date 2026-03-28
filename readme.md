# ifconfig.7it.vn

A simple, fast, and privacy‑friendly tool to check your public IPv4, IPv6, and current connection IP.

Inspired by tools like `ifconfig.me`, `ipify`, and `showmyip`, but designed to be:
- lightweight
- Docker‑friendly
- CI/CD ready

---

## ✨ Features

- Show **public IPv4** (forced IPv4 endpoint)
- Show **public IPv6** (via Cloudflare IPv6 edge)
- Show **current connection IP** (actual IP used for this request)
- Clean web UI (static HTML)
- Machine‑friendly API
- Ready for Docker & production

---

## 🚀 Endpoints

### Web UI

### Run with Docker (recommended)

docker pull syvtit/ip-info-api:latest
docker run -d --name ifconfig -p 8000:8000 syvtit/ip-info-api:latest

