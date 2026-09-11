"""Live catalog schema. Source of truth is the VPS to VPN tree, not hand JSON."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = "1.0"
PRODUCT_ID = "vpn-installer"

STATUS_LIVE = "live"
STATUS_DEPRECATED = "deprecated"
STATUS_LEGACY = "legacy"
STATUS_UNKNOWN = "unknown"
STATUS_SCAN_ERROR = "scan_error"


@dataclass
class FeatureRecord:
    id: str
    name: str
    category: str
    source_files: list[str] = field(default_factory=list)
    source_symbols: list[str] = field(default_factory=list)
    ui_locations: list[str] = field(default_factory=list)
    operation_ids: list[str] = field(default_factory=list)
    workflow: list[str] = field(default_factory=list)
    purpose: str = "UNKNOWN"
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    api_calls: list[str] = field(default_factory=list)
    validation: list[str] = field(default_factory=list)
    success_states: list[str] = field(default_factory=list)
    error_states: list[str] = field(default_factory=list)
    troubleshooting: list[str] = field(default_factory=list)
    related_features: list[str] = field(default_factory=list)
    platform: str = "windows"
    status: str = STATUS_LIVE
    source_hash: str = ""
    source_version: str = ""
    last_scanned: str = ""
    migrated_from_manual: bool = False
    menu_feature: bool = False
    media_slots: list[str] = field(default_factory=list)
    scan_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureRecord:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        kwargs = {k: v for k, v in data.items() if k in known}
        return cls(**kwargs)


def empty_validation_report() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "missing": [],
        "extra": [],
        "outdated": [],
        "deprecated": [],
        "updated": [],
        "unchanged": [],
        "scan_errors": [],
    }
