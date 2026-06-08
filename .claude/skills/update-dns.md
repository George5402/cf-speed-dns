---
name: update-dns
description: Manually run the Cloudflare optimal IP selection and push the results to DNSPod or Cloudflare DNS.
---

Run the DNS update scripts locally or review the last GitHub Actions run.

**Run locally (requires environment variables):**

For DNSPod:
```bash
export DOMAIN=example.com
export SUB_DOMAIN=cdn
export SECRETID=your_secret_id
export SECRETKEY=your_secret_key
export PUSHPLUS_TOKEN=your_token
pip install -r requirements.txt
python3 dnspod.py
```

For Cloudflare DNS:
```bash
export CF_API_TOKEN=your_token
export CF_ZONE_ID=your_zone_id
export CF_DNS_NAME=cdn.example.com
export PUSHPLUS_TOKEN=your_token
pip install -r requirements.txt
python3 dnscf.py
```

**What the scripts do:**
1. Fetch the current top optimal Cloudflare IPs from `https://ip.164746.xyz/ipTop.html` (comma-separated list).
2. Read existing DNS A records for the configured domain.
3. Update each record with the new optimal IP in order.
4. Send a WeChat push notification via PushPlus with the update results.

**Troubleshooting:**
- If the IP fetch fails after 5 retries, check connectivity to `ip.164746.xyz`.
- If DNS update fails, verify API credentials and that the record count matches the number of IPs returned.
