"""
Provides base generator implementation and utilities to build generators.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, cast

from mkdocs.config import Config as MKDocsConfig
from schema import Schema


class BaseGenerator(ABC):
    """
    Base class for the all yaarg generators.
    """

    options_schema = Schema({})

    def __init__(self, mkdocs: MKDocsConfig):
        self.mkdocs = mkdocs

    def validate_options(self, options: dict) -> dict:
        """
        Validates generator options.
        The result is used as `options` parameter for `generate()` method.

        Args:
            options (dict): Raw options from markdown

        Returns:
            dict: Validated options
        """
        return self.options_schema.validate(options)

    @abstractmethod
    def generate(
        self, filepath: Path, symbol: Optional[str], options: dict
    ) -> Iterable[str]:
        """
        Reads the source code and generates markdown lines.

        Args:
            filepath (Path): Path to the source code
            symbol (Optional[str]): Symbol name
            options (dict): Generator options. See also `validate_options()`.

        Returns:
            Iterable[str]: Markdown lines
        """
        pass


def markdown_heading(text: Optional[str], level: int = 1) -> str:
    """
    Creates markdown heading block.
    """
    if text is None:
        return ""

    text = ("#" * level) + " " + text
    text = text.strip()
    return text


def markdown_paragraph(text: Optional[str]) -> str:
    """
    Creates markdown paragraph block(s).
    """
    if text is None:
        return ""

    return text.strip()


class markdown_block:
    """
    Context manager to create an arbitrary markdown block.
    """

    def __init__(self):
        self.lines = [""]

    def write(self, text: str):
        """
        Appends text to the last input.

        Args:
            text (str): Appended text
        """
        self.lines[-1] += text

    def writeln(self, line: str):
        """
        Appends text to the last input and insert line break.

        Args:
            line (str): Appended line
        """
        self.write(line)
        self.lines.append("")

    def build(self) -> str:
        """
        Builds final markdown block.

        Returns:
            str: Markdown block contents
        """
        return "\n".join(self.lines).strip("\r\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
