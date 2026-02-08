# -*- coding: utf-8 -*-
"""Response format validation for handler outputs.

Provides lightweight runtime checks that every dict returned by _ok()
or _error() conforms to the canonical envelope.  Intended for use in
tests and (optionally) in debug builds.
"""
from __future__ import annotations

from typing import Any


# ── Canonical envelope keys ──────────────────────────────────────
_OK_KEYS = {"ok", "result", "error", "timing_ms"}


class ResponseValidationError(Exception):
    """Raised when a response dict does not match the expected schema."""


def validate_response(resp: dict[str, Any]) -> None:
    """Validate that *resp* matches the unified response envelope.

    Rules:
      1. Must be a dict.
      2. Must contain exactly {ok, result, error, timing_ms}.
      3. ok must be bool.
      4. timing_ms must be a number >= 0.
      5. If ok is True:  result must be a dict, error must be None.
      6. If ok is False: result must be None, error must be a dict
         with at least {code, message}.

    Raises:
        ResponseValidationError: on any violation.
    """
    if not isinstance(resp, dict):
        raise ResponseValidationError(
            f"Response must be a dict, got {type(resp).__name__}"
        )

    missing = _OK_KEYS - resp.keys()
    if missing:
        raise ResponseValidationError(
            f"Response missing keys: {missing}"
        )

    extra = resp.keys() - _OK_KEYS
    if extra:
        raise ResponseValidationError(
            f"Response has unexpected keys: {extra}"
        )

    if not isinstance(resp["ok"], bool):
        raise ResponseValidationError(
            f"\"ok\" must be bool, got {type(resp['ok']).__name__}"
        )

    timing = resp["timing_ms"]
    if not isinstance(timing, (int, float)) or timing < 0:
        raise ResponseValidationError(
            f"\"timing_ms\" must be a non-negative number, got {timing!r}"
        )

    if resp["ok"]:
        if not isinstance(resp["result"], dict):
            raise ResponseValidationError(
                "Success response must have dict \"result\", "
                f"got {type(resp['result']).__name__}"
            )
        if resp["error"] is not None:
            raise ResponseValidationError(
                "Success response must have \"error\": None"
            )
    else:
        if resp["result"] is not None:
            raise ResponseValidationError(
                "Error response must have \"result\": None"
            )
        err = resp["error"]
        if not isinstance(err, dict):
            raise ResponseValidationError(
                "Error response must have dict \"error\", "
                f"got {type(err).__name__}"
            )
        if "code" not in err or "message" not in err:
            raise ResponseValidationError(
                "Error dict must contain \"code\" and \"message\""
            )


def is_ok(resp: dict[str, Any]) -> bool:
    """Return True if *resp* is a successful response."""
    return isinstance(resp, dict) and resp.get("ok") is True


def is_error(resp: dict[str, Any]) -> bool:
    """Return True if *resp* is an error response."""
    return isinstance(resp, dict) and resp.get("ok") is False


def get_error_code(resp: dict[str, Any]) -> str | None:
    """Extract the error code string from an error response, or None."""
    err = resp.get("error")
    if isinstance(err, dict):
        return err.get("code")
    return None
