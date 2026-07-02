"""Load and query model and hardware registries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]


class RegistryError(ValueError):
    """Raised when registry contents are missing or malformed."""


@dataclass(frozen=True)
class Registry:
    """In-memory view of ``registry/models.yaml`` and ``registry/hardware.yaml``."""

    models: dict[str, dict[str, Any]]
    machines: dict[str, dict[str, Any]]
    profiles: tuple[str, ...]

    def model(self, model_id: str) -> dict[str, Any]:
        """Return a model registry entry by id."""
        try:
            return self.models[model_id]
        except KeyError as exc:
            raise RegistryError(f"unknown model id: {model_id}") from exc

    def machine(self, env_id: str) -> dict[str, Any]:
        """Return a hardware registry entry by id."""
        try:
            return self.machines[env_id]
        except KeyError as exc:
            raise RegistryError(f"unknown env id: {env_id}") from exc


def load_registry(root: Path = Path()) -> Registry:
    """Load registry YAML files below ``root``."""
    models_data = _load_yaml_mapping(root / "registry" / "models.yaml")
    hardware_data = _load_yaml_mapping(root / "registry" / "hardware.yaml")
    models = _index_entries(models_data, "models")
    machines = _index_entries(hardware_data, "machines")
    profiles = tuple(str(profile) for profile in cast(list[Any], models_data.get("profiles", [])))
    return Registry(models=models, machines=machines, profiles=profiles)


def model_defaults(registry: Registry, model_id: str, env_id: str) -> dict[str, str | int | None]:
    """Resolve common row defaults from model and hardware registries."""
    model = registry.model(model_id)
    machine = registry.machine(env_id)
    runtimes = cast(list[Any], model.get("runtimes", []))
    env_runtimes = cast(list[Any], machine.get("runtimes", []))
    runtime = next((str(item) for item in runtimes if item in env_runtimes), str(runtimes[0]) if runtimes else "")
    profiles = cast(list[Any], model.get("profiles", []))
    quantizations = cast(list[Any], model.get("quantization", []))
    return {
        "revision": _optional_string(model.get("revision")),
        "runtime": runtime,
        "profile": str(profiles[0]) if profiles else "",
        "quantization": str(quantizations[0]) if quantizations else None,
        "max_model_len": _optional_int(model.get("max_model_len")),
    }


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise RegistryError(f"{path} must be a YAML mapping")
    return cast(dict[str, Any], data)


def _index_entries(data: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    entries = data.get(key)
    if not isinstance(entries, list):
        raise RegistryError(f"registry key {key!r} must be a list")
    indexed: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise RegistryError(f"registry key {key!r} contains an entry without string id")
        indexed[str(entry["id"])] = cast(dict[str, Any], entry)
    return indexed


def _optional_string(value: object | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: object | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return int(str(value))
