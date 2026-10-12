# Regression: ISSUE-001 — verify pyproject.toml runner configuration
# Found by /qa on 2026-10-12
# Report: .gstack/qa-reports/run-20261012194003Z/qa-report-backend-2026-10-12.md

import tomllib
import os

def test_pyproject_runner_configuration():
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Check uv package mode is disabled for non-package app
    assert "tool" in data, "tool section missing in pyproject.toml"
    assert "uv" in data["tool"], "tool.uv section missing in pyproject.toml"
    assert data["tool"]["uv"].get("package") is False, "tool.uv.package must be false"

    # Check pytest configuration
    assert "pytest" in data["tool"], "tool.pytest section missing in pyproject.toml"
    assert "ini_options" in data["tool"]["pytest"], "tool.pytest.ini_options section missing"
    ini_options = data["tool"]["pytest"]["ini_options"]
    assert ini_options.get("testpaths") == ["tests"], "testpaths must be ['tests']"
    assert "." in ini_options.get("pythonpath", []), "pythonpath must include '.'"
