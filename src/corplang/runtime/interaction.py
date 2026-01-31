"""Interaction adapters for agent communication.

Provides a minimal, production-friendly stdin adapter and simple
agent routing helper used by the `loop stdin using ...` statement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, List


class InteractionAdapter(ABC):
    """Abstract base for agent interaction mechanisms."""

    @abstractmethod
    def read(self) -> Optional[str]:
        """Read input from the interaction source; return None on termination."""

    @abstractmethod
    def write(self, data: Any) -> None:
        """Write output to the interaction sink."""

    @abstractmethod
    def is_active(self) -> bool:
        """Check if adapter is still active."""

    @abstractmethod
    def close(self) -> None:
        """Release any resources and mark adapter inactive."""


class StdinAdapter(InteractionAdapter):
    """Minimal stdin adapter for interactive console loops."""

    def __init__(self) -> None:
        self._active = True

    def read(self) -> Optional[str]:
        if not self._active:
            return None
        try:
            return input("> ")
        except (EOFError, KeyboardInterrupt):
            self._active = False
            return None

    def write(self, data: Any) -> None:
        print(data)

    def is_active(self) -> bool:
        return self._active

    def close(self) -> None:
        self._active = False

    # Back-compat wrappers if older executors call legacy names
    def read_input(self) -> Optional[str]:  # type: ignore[override]
        """Read the input system."""
        return self.read()

    def write_output(self, data: Any) -> None:  # type: ignore[override]
        """Write the input system."""
        self.write(data)


def choose_target_agent(agent_names: Optional[List[str]], raw_input: str) -> Tuple[Optional[str], str]:
    """Select a target agent and routed input.

    Rules:
    - No agents: return (None, raw_input)
    - One agent: route to it unchanged
    - Multiple agents: allow prefix routing in the form "Name: message";
      if no valid prefix, default to the first agent.
    """
    if not agent_names:
        return None, raw_input
    if len(agent_names) == 1:
        return agent_names[0], raw_input

    txt = raw_input or ""
    if ":" in txt:
        prefix, _, rest = txt.partition(":")
        target = prefix.strip()
        if target in agent_names:
            return target, rest.lstrip()
    # default routing
    return agent_names[0], raw_input
