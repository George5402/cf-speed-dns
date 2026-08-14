#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import os
import time
import traceback

import requests

DOMAIN = os.environ["DOMAIN"]
SUB_DOMAIN = os.environ["SUB_DOMAIN"]
SECRETID = os.environ["SECRETID"]
SECRETKEY = os.environ["SECRETKEY"]
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

TENCENT_ENDPOINT = "dnspod.tencentcloudapi.com"
TENCENT_SERVICE = "dnspod"
TENCENT_VERSION = "2021-03-23"
TENCENT_REGION = ""


def tencent_api(action, payload):
    if not SECRETID or not SECRETKEY:
        raise RuntimeError("SECRETID and SECRETKEY must be configured in GitHub Actions secrets")

    timestamp = int(time.time())
    date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    content_type = "application/json; charset=utf-8"

    canonical_headers = (
        f"content-type:{content_type}\n"
        f"host:{TENCENT_ENDPOINT}\n"
    )
    signed_headers = "content-type;host"
    hashed_payload = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    canonical_request = (
        f"POST\n/\n\n{canonical_headers}\n"
        f"{signed_headers}\n{hashed_payload}"
    )

    credential_scope = f"{date}/{TENCENT_SERVICE}/tc3_request"
    hashed_canonical_request = hashlib.sha256(
        canonical_request.encode("utf-8")
    ).hexdigest()
    string_to_sign = (
        f"TC3-HMAC-SHA256\n{timestamp}\n{credential_scope}\n"
        f"{hashed_canonical_request}"
    )

    secret_date = hmac.new(
        f"TC3{SECRETKEY}".encode("utf-8"), date.encode("utf-8"), hashlib.sha256
    ).digest()
    secret_service = hmac.new(
        secret_date, TENCENT_SERVICE.encode("utf-8"), hashlib.sha256
    ).digest()
    secret_signing = hmac.new(
        secret_service, b"tc3_request", hashlib.sha256
    ).digest()
    signature = hmac.new(
        secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    authorization = (
        f"TC3-HMAC-SHA256 Credential={SECRETID}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    headers = {
        "Authorization": authorization,
        "Content-Type": content_type,
        "Host": TENCENT_ENDPOINT,
        "X-TC-Action": action,
        "X-TC-Version": TENCENT_VERSION,
        "X-TC-Timestamp": str(timestamp),
    }
    if TENCENT_REGION:
        headers["X-TC-Region"] = TENCENT_REGION

    response = requests.post(
        f"https://{TENCENT_ENDPOINT}",
        data=payload_json.encode("utf-8"),
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()
    error = result.get("Response", {}).get("Error")
    if error:
        raise RuntimeError(
            f"TencentCloud API error {error.get('Code')}: {error.get('Message')}"
        )
    return result.get("Response", {})


def get_records():
    response = tencent_api(
        "DescribeRecordList",
        {
            "Domain": DOMAIN,
            "Subdomain": SUB_DOMAIN,
            "RecordType": "A",
            "Limit": 100,
        },
    )
    records = []
    for record in response.get("RecordList", []):
        if record.get("RecordLine") == "默认":
            records.append(
                {"recordId": record["RecordId"], "value": record["Value"]}
            )
    print(
        "get_records success: ---- Time: "
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} ---- records: {records}"
    )
    return records


def get_cf_speed_test_ip(timeout=10, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://ip.164746.xyz/ipTop.html", timeout=timeout
            )
            response.raise_for_status()
            ips = [ip.strip() for ip in response.text.split(",") if ip.strip()]
            if ips:
                return ips
        except Exception as exc:
            print(
                f"get_cf_speed_test_ip failed "
                f"(attempt {attempt + 1}/{max_retries}): {exc}"
            )
            time.sleep(1)
    raise RuntimeError("Unable to obtain Cloudflare speed-test IP addresses")


def change_dns(record_id, cf_ip):
    try:
        tencent_api(
            "ModifyRecord",
            {
                "Domain": DOMAIN,
                "RecordId": record_id,
                "SubDomain": SUB_DOMAIN,
                "Value": cf_ip,
                "RecordType": "A",
                "RecordLine": "默认",
                "TTL": 600,
            },
        )
        print(
            "change_dns success: ---- Time: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} ---- ip: {cf_ip}"
        )
        return f"ip:{cf_ip} 解析 {SUB_DOMAIN}.{DOMAIN} 成功"
    except Exception as exc:
        traceback.print_exc()
        print(f"change_dns ERROR: {exc}")
        return f"ip:{cf_ip} 解析 {SUB_DOMAIN}.{DOMAIN} 失败"


def pushplus(content):
    if not PUSHPLUS_TOKEN:
        print("PUSHPLUS_TOKEN is not configured; skip notification")
        return
    response = requests.post(
        "https://www.pushplus.plus/send",
        json={
            "token": PUSHPLUS_TOKEN,
            "title": "IP优选DNSPOD推送",
            "content": content,
            "template": "markdown",
            "channel": "wechat",
        },
        timeout=20,
    )
    response.raise_for_status()


if __name__ == "__main__":
    records = get_records()
    if not records:
        raise RuntimeError(f"No default A records found for {SUB_DOMAIN}.{DOMAIN}")

    ip_addresses = get_cf_speed_test_ip()
    if len(ip_addresses) > len(records):
        raise RuntimeError(
            f"Received {len(ip_addresses)} IPs but only {len(records)} DNS records exist"
        )

    results = []
    for index, ip_address in enumerate(ip_addresses):
        results.append(change_dns(records[index]["recordId"], ip_address))

    pushplus("\n".join(results))
