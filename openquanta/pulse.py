"""
Pulse-Level Control for open-Quanta.

Defines microwave pulses and schedules for raw hardware control on open systems.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Pulse:
    """
    A single microwave pulse definition.
    """
    frequency: float  # Hz
    amplitude: float  # Normalized [0.0, 1.0]
    duration: float   # Nanoseconds
    phase: float = 0.0 # Radians
    shape: str = "gaussian" # Pulse envelope shape

    def __repr__(self):
        return f"Pulse(freq={self.frequency/1e9:.2f}GHz, amp={self.amplitude:.2f}, dur={self.duration}ns, shape={self.shape})"


class Schedule:
    """
    A timeline of pulses applied to specific hardware channels.
    """
    def __init__(self):
        self.instructions: List[tuple] = []
        self._current_time: float = 0.0

    def play(self, channel: int, pulse: Pulse):
        """Play a pulse on a specific channel."""
        self.instructions.append((self._current_time, channel, pulse))
        self._current_time += pulse.duration

    def delay(self, duration: float):
        """Wait for a specific duration."""
        self._current_time += duration

    @property
    def duration(self) -> float:
        """Total duration of the schedule."""
        return self._current_time

    def __repr__(self):
        return f"Schedule(duration={self.duration}ns, instructions={len(self.instructions)})"
