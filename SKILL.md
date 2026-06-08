---
name: cf-speed-dns
description: Work with cf-speed-dns — a GitHub Actions project that fetches optimal Cloudflare IPs every 5 minutes and pushes them to DNSPod or Cloudflare DNS. Use when configuring secrets, running scripts locally, or debugging DNS update failures.
---

# cf-speed-dns

A GitHub Actions project that automatically selects the fastest Cloudflare IPs and updates DNS records via Tencent DNSPod (`dnspod.py`) or Cloudflare DNS API (`dnscf.py`), with WeChat push notifications via PushPlus.

## When to use

Use this skill when setting up the project, configuring GitHub Actions secrets, running the update scripts locally, or debugging DNS sync failures.

## Instructions

### Setting up GitHub Actions

Add these secrets under *Settings → Secrets and variables → Actions*:

**For DNSPod (`dnspod.py`):**
- `DOMAIN` — root domain, e.g. `example.com`
- `SUB_DOMAIN` — subdomain prefix, e.g. `cdn`
- `SECRETID` — Tencent Cloud API SecretId
- `SECRETKEY` — Tencent Cloud API SecretKey
- `PUSHPLUS_TOKEN` — PushPlus token from https://www.pushplus.plus

**For Cloudflare DNS (`dnscf.py`):**
- `CF_API_TOKEN` — Cloudflare API token with DNS edit permission
- `CF_ZONE_ID` — Zone ID from the Cloudflare dashboard
- `CF_DNS_NAME` — full record name, e.g. `cdn.example.com`
- `PUSHPLUS_TOKEN` — PushPlus token

### Running locally

```bash
pip install -r requirements.txt

# DNSPod
DOMAIN=example.com SUB_DOMAIN=cdn SECRETID=xx SECRETKEY=xx PUSHPLUS_TOKEN=xx python3 dnspod.py

# Cloudflare DNS
CF_API_TOKEN=xx CF_ZONE_ID=xx CF_DNS_NAME=cdn.example.com PUSHPLUS_TOKEN=xx python3 dnscf.py
```

### How it works

1. Fetches top optimal IPs from `https://ip.164746.xyz/ipTop.html` (comma-separated, up to 5 retries).
2. Reads existing A records for the configured domain.
3. Updates each record in order with the new IPs.
4. Sends a WeChat notification via PushPlus with the results.

### Debugging

- IP fetch failing: check connectivity to `ip.164746.xyz`; the endpoint returns a plain comma-separated string.
- DNS update failing: verify API credentials are correct and the number of existing DNS records matches the number of IPs returned.
- Record count mismatch: `dnspod.py` uses list index access — if the API returns fewer records than IPs, it will raise an `IndexError`.
