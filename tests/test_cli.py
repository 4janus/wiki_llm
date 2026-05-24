"""Tests for CLI commands."""

from typer.testing import CliRunner

from src.cli import app


def test_advisor_command_is_registered():
    """Verify 'advisor' command is registered in the CLI."""
    runner = CliRunner()
    result = runner.invoke(app, ["advisor", "--help"])
    assert result.exit_code == 0
    assert "root" in result.output.lower() or "mappe" in result.output.lower()
