from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from dashboard.data_access import (
    DashboardData,
    DashboardSourcePaths,
    RunHistoryData,
    load_dashboard_data,
    load_run_history,
)

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "dashboard_demo"


class _FakeContext:
    def __enter__(self) -> _FakeContext:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> Literal[False]:
        _ = (exc_type, exc, tb)
        return False


class FakeSidebar:
    def selectbox(
        self,
        _label: str,
        options: list[str],
        index: int = 0,
        key: str | None = None,
    ) -> str:
        _ = key
        return options[index]

    def markdown(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def caption(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def divider(self) -> None:
        return None

    def expander(self, *_args: Any, **_kwargs: Any) -> _FakeContext:
        return _FakeContext()

    def page_link(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class FakeStreamlit:
    def __init__(self) -> None:
        self.sidebar = FakeSidebar()
        self.session_state: dict[str, str] = {}

    def set_page_config(self, **_kwargs: Any) -> None:
        return None

    def title(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def markdown(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def stop(self) -> None:
        raise RuntimeError("stop called unexpectedly")

    def error(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def exception(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def spinner(self, *_args: Any, **_kwargs: Any) -> _FakeContext:
        return _FakeContext()

    def columns(self, spec: int | list[float], **_kwargs: Any) -> list[_FakeContext]:
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContext() for _ in range(count)]

    def tabs(self, labels: list[str]) -> list[_FakeContext]:
        return [_FakeContext() for _ in labels]

    def expander(self, *_args: Any, **_kwargs: Any) -> _FakeContext:
        return _FakeContext()

    def dataframe(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def area_chart(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def bar_chart(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def info(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def write(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def code(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def slider(
        self,
        _label: str,
        min_value: int = 0,
        max_value: int = 10,
        value: int = 1,
    ) -> int:
        _ = (min_value, max_value)
        return value

    def text_input(
        self,
        _label: str,
        value: str = "",
        placeholder: str = "",
    ) -> str:
        return value or placeholder or ""

    def selectbox(
        self,
        _label: str,
        options: list[str],
        index: int = 0,
        key: str | None = None,
    ) -> str:
        _ = key
        return options[index]

    def page_link(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def fixture_dashboard_data() -> DashboardData:
    return load_dashboard_data(str(FIXTURE_ROOT / "gold"))


def fixture_run_history() -> RunHistoryData:
    return load_run_history(str(FIXTURE_ROOT / "runs"))


def fixture_source_paths(*, demo_active: bool = False) -> DashboardSourcePaths:
    return DashboardSourcePaths(
        gold_dir=FIXTURE_ROOT / "gold",
        run_dir=FIXTURE_ROOT / "runs",
        serving_db=FIXTURE_ROOT / "serving.db",
        demo_mode="AUTO",
        demo_active=demo_active,
    )


def load_module_from_path(module_path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
