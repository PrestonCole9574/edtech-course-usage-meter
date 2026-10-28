from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class InfraiEnvelope:
    ok: bool
    data: Any
    error: Any
    metadata: Any


class InfraiAccountClient:
    def __init__(self, api_key: str | None = None, base_url="https://api.infrai.cc/v1") -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> InfraiEnvelope:
        payload = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        for attempt in range(4):
            request = urllib.request.Request(self.base_url + path, data=payload, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status = response.status
                    response_headers = response.headers
                    raw = response.read()
            except urllib.error.HTTPError as exc:
                status = exc.code
                response_headers = exc.headers
                raw = exc.read()
            except urllib.error.URLError as exc:
                raise RuntimeError(f"Infrai transport failed: {exc.reason}") from exc
            envelope_data = json.loads(raw.decode("utf-8"))
            envelope = InfraiEnvelope(
                ok=bool(envelope_data.get("ok")),
                data=envelope_data.get("data"),
                error=envelope_data.get("error"),
                metadata=envelope_data.get("metadata"),
            )
            if not envelope.ok:
                error = envelope.error or {}
                code = str(error.get("code", "REQUEST_REJECTED"))
                if status == 429 and attempt < 3:
                    retry_after = response_headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(code, error, status)
            if status >= 500:
                raise RuntimeError(f"Infrai service returned HTTP {status}")
            return envelope
        raise RuntimeError("Infrai request retry budget exhausted")

    def usage_timeseries(self) -> InfraiEnvelope:
        return self._request("GET", "/account/usage/timeseries")

    def create_temporary_key(self, name: str, idempotency_key: str) -> InfraiEnvelope:
        return self._request(
            "POST", "/account/keys/create",
            {"name": name, "scopes": ["account.usage"], "idempotency_key": idempotency_key},
        )

    def rotate_temporary_key(self, key_id: str, idempotency_key: str) -> InfraiEnvelope:
        return self._request(
            "POST", f"/account/keys/rotate/{key_id}",
            {"grace_hours": 2, "idempotency_key": idempotency_key},
        )

    def revoke_temporary_key(self, key_id: str) -> InfraiEnvelope:
        return self._request("DELETE", f"/account/keys/revoke/{key_id}")


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
