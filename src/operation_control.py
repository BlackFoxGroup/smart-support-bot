"""Cooperative cancellation shared by Manager operations."""

from __future__ import annotations

import threading


class OperationStopped(RuntimeError):
    pass


_LOCK = threading.Lock()
_EPOCH = 0
_LOCAL = threading.local()


def begin_operation() -> int:
    with _LOCK:
        token = _EPOCH
    _LOCAL.token = token
    return token


def stop_all_operations() -> int:
    global _EPOCH
    with _LOCK:
        _EPOCH += 1
        return _EPOCH


def operation_stopped() -> bool:
    token = getattr(_LOCAL, "token", None)
    if token is None:
        return False
    with _LOCK:
        return token != _EPOCH


def raise_if_stopped() -> None:
    if operation_stopped():
        raise OperationStopped("all Manager operations were stopped")
