"""Minimal, dependency-free client for the Peakerr SMM API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PeakerrAPIError(RuntimeError):
    """Raised when Peakerr rejects a request or returns an invalid response."""


@dataclass(frozen=True)
class PeakerrClient:
    api_key: str
    endpoint: str = "https://peakerr.com/api/v2"
    timeout: int = 30

    @classmethod
    def from_environment(cls) -> "PeakerrClient":
        api_key = os.getenv("PEAKERR_API_KEY", "").strip()
        if not api_key:
            raise PeakerrAPIError(
                "PEAKERR_API_KEY belum diatur. Salin .env.example menjadi .env "
                "atau export PEAKERR_API_KEY sebelum menjalankan CLI."
            )
        endpoint = os.getenv("PEAKERR_API_URL", cls.endpoint).strip().rstrip("/")
        return cls(api_key=api_key, endpoint=endpoint)

    def _post(self, action: str, **params: Any) -> Any:
        form = {"key": self.api_key, "action": action, **params}
        request = Request(
            self.endpoint,
            data=urlencode(form).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "PRO-SMM/1.0",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise PeakerrAPIError(f"Peakerr HTTP {exc.code}: {body[:500]}") from exc
        except (URLError, TimeoutError) as exc:
            raise PeakerrAPIError(f"Tidak dapat terhubung ke Peakerr: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise PeakerrAPIError("Peakerr mengembalikan respons bukan JSON.") from exc

        if isinstance(payload, dict) and payload.get("error"):
            raise PeakerrAPIError(str(payload["error"]))
        return payload

    def list_services(self) -> list[dict[str, Any]]:
        """Load the complete service catalog from Peakerr."""
        payload = self._post("services")
        if not isinstance(payload, list):
            raise PeakerrAPIError("Format respons services Peakerr tidak sesuai: expected array.")
        return [item for item in payload if isinstance(item, dict)]

    def get_balance(self) -> Any:
        """Read account balance; no order or payment action is performed."""
        return self._post("balance")


def save_services(path: str = "data/services.json") -> int:
    services = PeakerrClient.from_environment().list_services()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(services, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return len(services)
