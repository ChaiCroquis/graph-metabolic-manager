"""Tests for TraceLogging: TRACE log level registration and output."""

from __future__ import annotations

import logging

import pytest

from graph_metabolic_manager._logging import TRACE


class TestTraceLevelRegistration:
    """TraceLevelRegistration: TRACE level registered with logging module."""

    def test_trace_level_value(self) -> None:
        """TRACE level is 5 (below DEBUG=10)."""
        assert TRACE == 5

    def test_trace_level_name(self) -> None:
        """getLevelName(5) returns 'TRACE'."""
        assert logging.getLevelName(5) == "TRACE"

    def test_trace_attribute_on_logging_module(self) -> None:
        """logging.TRACE is available after import."""
        assert hasattr(logging, "TRACE")
        assert logging.TRACE == 5  # type: ignore[attr-defined]

    def test_logger_has_trace_method(self) -> None:
        """Logger instances have a .trace() method."""
        test_logger = logging.getLogger("test.trace.method")
        assert hasattr(test_logger, "trace")
        assert callable(test_logger.trace)  # type: ignore[attr-defined]


class TestTraceOutput:
    """TraceOutput: TRACE messages emitted correctly."""

    def test_trace_message_emitted(self, caplog: pytest.LogCaptureFixture) -> None:
        """TRACE messages appear when level is set to TRACE."""
        test_logger = logging.getLogger("test.trace.emit")
        with caplog.at_level(TRACE, logger="test.trace.emit"):
            test_logger.log(TRACE, "formula: x = %d + %d = %d", 1, 2, 3)
        assert "formula: x = 1 + 2 = 3" in caplog.text

    def test_trace_not_emitted_at_debug(self, caplog: pytest.LogCaptureFixture) -> None:
        """TRACE messages do NOT appear when level is DEBUG."""
        test_logger = logging.getLogger("test.trace.silent")
        with caplog.at_level(logging.DEBUG, logger="test.trace.silent"):
            test_logger.log(TRACE, "should not appear")
        assert "should not appear" not in caplog.text

    def test_trace_via_logger_method(self, caplog: pytest.LogCaptureFixture) -> None:
        """logger.trace() convenience method works."""
        test_logger = logging.getLogger("test.trace.convenience")
        with caplog.at_level(TRACE, logger="test.trace.convenience"):
            test_logger.trace("method: y = %.2f", 3.14)  # type: ignore[attr-defined]
        assert "method: y = 3.14" in caplog.text


class TestTraceImportFromPackage:
    """TraceImportFromPackage: TRACE accessible from public API."""

    def test_import_from_package(self) -> None:
        """TRACE can be imported from the top-level package."""
        from graph_metabolic_manager import TRACE as pkg_trace

        assert pkg_trace == 5

    def test_in_all(self) -> None:
        """TRACE is listed in __all__."""
        import graph_metabolic_manager

        assert "TRACE" in graph_metabolic_manager.__all__
