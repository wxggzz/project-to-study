"""Output style presets for the generated docs.

A style only changes emphasis and verbosity — it never changes facts or evidence.
Four presets:

- ``standard`` (default): full prose, balanced for general onboarding.
- ``concise``: drops optional explanatory prose; keeps tables, commands, and
  evidence. Good for experienced readers.
- ``teaching``: adds plain-English callouts and a glossary; emphasises the
  learning manual. Good for newcomers / AI-assisted builders.
- ``ops``: front-loads operation, deployment, and troubleshooting in the index
  and flags those documents as operational priorities.
"""

from __future__ import annotations

from dataclasses import dataclass


class StyleName:
    STANDARD = "standard"
    CONCISE = "concise"
    TEACHING = "teaching"
    OPS = "ops"

    ALL = (STANDARD, CONCISE, TEACHING, OPS)


@dataclass(frozen=True)
class Style:
    name: str = StyleName.STANDARD

    @property
    def verbose(self) -> bool:
        """Include optional explanatory prose (everything except concise)."""

        return self.name != StyleName.CONCISE

    @property
    def teaching(self) -> bool:
        return self.name == StyleName.TEACHING

    @property
    def ops_focus(self) -> bool:
        return self.name == StyleName.OPS


def resolve(name: str | None) -> Style:
    """Resolve a style name to a :class:`Style`, defaulting to standard."""

    key = (name or StyleName.STANDARD).lower()
    if key not in StyleName.ALL:
        allowed = ", ".join(StyleName.ALL)
        raise ValueError(f"Unknown style '{name}'. Choose one of: {allowed}.")
    return Style(key)
