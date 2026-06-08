---
name: setup-actions
description: Guide the user through configuring GitHub Actions secrets for cf-speed-dns to enable automatic Cloudflare IP selection and DNS push.
---

Help the user configure the required GitHub Actions secrets for cf-speed-dns.

**For DNSPod (Tencent Cloud DNS) push (`dnspod.py`):**

Required secrets to add under *Settings → Secrets and variables → Actions*:
- `DOMAIN` — root domain, e.g. `example.com`
- `SUB_DOMAIN` — subdomain prefix, e.g. `cdn`
- `SECRETID` — Tencent Cloud API SecretId
- `SECRETKEY` — Tencent Cloud API SecretKey
- `PUSHPLUS_TOKEN` — PushPlus notification token (from https://www.pushplus.plus)

**For Cloudflare DNS push (`dnscf.py`):**

Required secrets:
- `CF_API_TOKEN` — Cloudflare API token with DNS edit permission
- `CF_ZONE_ID` — Zone ID from the Cloudflare dashboard
- `CF_DNS_NAME` — Full DNS record name, e.g. `cdn.example.com`
- `PUSHPLUS_TOKEN` — PushPlus notification token

**Verification steps:**
1. Trigger the workflow manually via *Actions → Run workflow*.
2. Check the workflow run log for "success" lines with the updated IPs.
3. Verify the DNS record has been updated in DNSPod/Cloudflare dashboard.

The workflow fetches the top optimal IPs from `https://ip.164746.xyz/ipTop.html` and updates each matching DNS A record.
