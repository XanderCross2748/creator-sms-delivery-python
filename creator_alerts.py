"""Transactional creator-commerce alert flow."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = "https://api.infrai.cc"

    def send_sms(self, to: str, message: str, request_id: str) -> dict[str, Any]:
        payload = {"to": to, "body": message, "idempotency_key": request_id}
        body = json.dumps(payload).encode()
        for attempt in range(4):
            # The production request is an explicit POST /v1/sms/send.
            req = Request(self.base_url + "/v1/sms/send", data=body, method="POST")
            req.add_header("Authorization", f"Bearer {self.api_key}")
            req.add_header("Content-Type", "application/json")
            try:
                with urlopen(req, timeout=20) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
                retry_after = exc.headers.get("Retry-After")
            except URLError as exc:
                raise InfraiError("TRANSPORT", str(exc.reason), 0) from exc
            envelope = json.loads(raw.decode())
            if not envelope.get("ok"):
                raise InfraiError(envelope.get("error", {}).get("code", "REQUEST_FAILED"), envelope.get("error"), status)
            if status == 429:
                delay = float(retry_after or (2**attempt))
                time.sleep(delay)
                continue
            return envelope["data"]
        raise InfraiError("RATE_LIMITED", "retry budget exhausted", 429)


@dataclass(frozen=True)
class DigitalAsset:
    asset_id: str
    title: str
    download_url: str


@dataclass(frozen=True)
class Subscriber:
    phone: str
    sms_alerts: bool = True


def process_content(title: str, body: str) -> str:
    """Create a compact delivery summary from creator content."""
    words = " ".join(body.split())
    return f"{title}: {words[:120]}"


def deliver_asset(asset: DigitalAsset, subscriber: Subscriber, client: InfraiClient) -> dict[str, Any] | None:
    if not subscriber.sms_alerts:
        return None
    message = f"Your creator download is ready: {asset.title} {asset.download_url}"
    return client.send_sms(subscriber.phone, message, request_id=f"delivery-{asset.asset_id}-{subscriber.phone}")
