"""
_logging — Custom TRACE log level for patent formula visibility.

TRACE (level 5) sits below DEBUG (level 10) and is used exclusively
for formula-level detail: each intermediate value in the patent's
mathematical model is shown with actual computed numbers substituted.

Usage::

    import logging
    from graph_metabolic_manager import TRACE

    logger = logging.getLogger(__name__)

    if logger.isEnabledFor(TRACE):
        logger.log(TRACE, "edge(%d,%d) C = %d + %d = %.1f", u, v, du, dv, C)

To enable TRACE output::

    logging.basicConfig(level=5)
    # or
    logging.getLogger("graph_metabolic_manager").setLevel(5)
"""

from __future__ import annotations

import logging

TRACE: int = 5
"""Custom log level for patent formula tracing (below DEBUG=10)."""


def _register_trace_level() -> None:
    """Register TRACE level with the logging module (idempotent).

    After calling this:

    - ``logging.TRACE`` is available as an integer constant (5).
    - ``logger.trace(msg, ...)`` works on any Logger instance.
    - ``logging.getLevelName(5)`` returns ``"TRACE"``.
    """
    if not hasattr(logging, "TRACE"):
        logging.addLevelName(TRACE, "TRACE")
        logging.TRACE = TRACE  # type: ignore[attr-defined]

    if not hasattr(logging.Logger, "trace"):

        def _trace(
            self: logging.Logger,
            message: str,
            *args: object,
            **kwargs: object,
        ) -> None:
            if self.isEnabledFor(TRACE):
                self._log(TRACE, message, args, **kwargs)

        logging.Logger.trace = _trace  # type: ignore[attr-defined]


# Register on import so any module importing TRACE gets a working level.
_register_trace_level()
