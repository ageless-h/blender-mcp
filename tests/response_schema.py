# -*- coding: utf-8 -*-
"""Response format validation for handler outputs.

Provides lightweight runtime checks that every dict returned by _ok()
or _error() conforms to the canonical envelope.  Intended for use in
tests and (optionally) in debug builds.
"""
from __future__ import annotations

from typing import Any

_OK_KEYS = {"ok", "result", "timing_ms"}
_ERROR_KEYS = {"ok", "error", "timing_ms"}


class ResponseValidationError(Exception):
    """Raised when a response dict does not match the expected schema."""


def validate_response(resp: dict[str, Any]) -> None:
    """Validate that *resp* matches the compact response envelope.

    Rules:
      1. Must be a dict.
      2. If ok is True: must have {ok, result, timing_ms}, no error key.
      3. If ok is False: must have {ok, error, timing_ms}, no result key.
      4. ok must be bool.
      5. timing_ms must be a number >= 0.
      6. No extra keys allowed beyond required keys.

    Raises:
        ResponseValidationError: on any violation.
    """
    if not isinstance(resp, dict):
        raise ResponseValidationError(
            f"Response must be a dict, got {type(resp).__name__}"
        )

    if "ok" not in resp:
        raise ResponseValidationError("Response missing required key: 'ok'")

    if not isinstance(resp["ok"], bool):
        raise ResponseValidationError(
            f"\"ok\" must be bool, got {type(resp['ok']).__name__}"
        )

    if "timing_ms" not in resp:
        raise ResponseValidationError("Response missing required key: 'timing_ms'")

    timing = resp["timing_ms"]
    if not isinstance(timing, (int, float)) or timing < 0:
        raise ResponseValidationError(
            f"\"timing_ms\" must be a non-negative number, got {timing!r}"
        )

    if resp["ok"]:
        missing = _OK_KEYS - resp.keys()
        if missing:
            raise ResponseValidationError(
                f"Success response missing keys: {missing}"
            )
        if "error" in resp:
            raise ResponseValidationError(
                "Success response should not have 'error' key"
            )
        extra = resp.keys() - _OK_KEYS
        if extra:
            raise ResponseValidationError(
                f"Response has unexpected keys: {extra}"
            )
        if resp["result"] is not None and not isinstance(resp["result"], (dict, list)):
            raise ResponseValidationError(
                f"Success response 'result' must be dict/list/None, got {type(resp['result']).__name__}"
            )
    else:
        missing = _ERROR_KEYS - resp.keys()
        if missing:
            raise ResponseValidationError(
                f"Error response missing keys: {missing}"
            )
        if "result" in resp:
            raise ResponseValidationError(
                "Error response should not have 'result' key"
            )
        extra = resp.keys() - _ERROR_KEYS
        if extra:
            raise ResponseValidationError(
                f"Response has unexpected keys: {extra}"
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
