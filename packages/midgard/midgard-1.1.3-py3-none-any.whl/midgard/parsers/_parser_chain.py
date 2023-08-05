"""Basic functionality for parsing datafiles line by line

Description:
------------

This module contains functions and classes for parsing datafiles.


Example:
--------

    from midgard import parsers
    my_new_parser = parsers.parse_file('my_new_parser', 'file_name.txt', ...)
    my_data = my_new_parser.as_dict()

"""
# Standard library imports
import itertools
from typing import Any, Callable, Dict, NamedTuple, Optional

# Midgard imports
from midgard.files import files
from midgard.parsers._parser import Parser


# A simple structure used to define the necessary fields of a parser
class ParserDef(NamedTuple):
    """A convenience class for defining the necessary fields of a parser

    A single parser can read and parse one group of datalines, defined through the ParserDef by specifying how to parse
    each line (parser_def), how to identify each line (label), how to recognize the end of the group of lines
    (end_marker) and finally what (if anything) should be done after all lines in a group is read (end_callback).

    The end_marker, label, skip_line and end_callback parameters should all be functions with the following signatures:

        end_marker   = func(line, line_num, next_line)
        label        = func(line, line_num)
        skip_line    = func(line)
        end_callback = func(cache)

    The parser definition `parser_def` includes the `parser`, `field`, `strip` and `delimiter` entries. The `parser`
    entry points to the parser function and the `field` entry defines how to separate the line in fields. The separated
    fields are saved either in a dictionary or in a list. In the last case the line is split on whitespace by
    default. With the `delimiter` entry the default definition can be overwritten. Leading and trailing whitespace
    characters are removed by default before a line is parsed.  This default can be overwritten by defining the
    characters, which should be removed with the 'strip' entry. The `parser` dictionary is defined like:

        parser_def = { <label>: {'fields':    <dict or list of fields>,
                                 'parser':    <parser function>,
                                 'delimiter': <optional delimiter for splitting line>,
                                 'strip':     <optional characters to be removed from beginning and end of line>
                     }}

    Args:
        end_marker:   A function returning True for the last line in a group.
        label:        A function returning a label used in the parser_def.
        parser_def:   A dict with 'parser' and 'fields' defining the parser.
        skip_line:    A function returning True if the line should be skipped.
        end_callback: A function called after reading all lines in a group.
    """

    end_marker: Callable[[str, int, str], bool]
    label: Callable[[str, int], Any]
    parser_def: Dict[Any, Dict[str, Any]]
    skip_line: Optional[Callable[[str], bool]] = None
    end_callback: Optional[Callable[[Dict[str, Any]], None]] = None


class ChainParser(Parser):
    """An abstract base class that has basic methods for parsing a datafile

    This class provides functionality for parsing a file with chained groups of information. You should inherit from
    this one, and at least specify the necessary parameters in `setup_parser`.
    """

    def setup_parser(self) -> Any:
        """Set up information needed for the parser

        Return an iterable of ParserDef's that describe the structure of the file that will be parsed
        """
        raise NotImplementedError

    def read_data(self) -> None:
        """Read data from a data file and parse the contents
        """
        # Get chain of parsers
        parsers_chain = iter(self.setup_parser())
        parser = next(parsers_chain)  # Pointing to first parser
        cache = dict(line_num=0)

        with files.open(self.file_path, mode="rt", encoding=self.file_encoding) as fid:
            # Get iterators for current and next line
            line_iter, next_line_iter = itertools.tee(fid)
            next(next_line_iter, None)

            # Iterate over all file lines including last line by using zip_longest
            for line, next_line in itertools.zip_longest(line_iter, next_line_iter):
                cache["line_num"] += 1
                self.parse_line(line.rstrip(), cache, parser)

                # Skip to next parser
                if next_line is None or parser.end_marker(line.rstrip(), cache["line_num"], next_line):
                    if parser.end_callback is not None:
                        parser.end_callback(cache)
                    cache = dict(line_num=0)
                    try:
                        parser = next(parsers_chain)
                    except StopIteration:
                        break

    def parse_line(self, line: str, cache: Dict[str, Any], parser: ParserDef) -> None:
        """Parse line

        A line is parsed by separating a line in fields. How the separation is done, is defined in the `parser_def`
        entry of the ParserDef.

        Args:
            line:    Line to be parsed.
            cache:   Store temporary data.
            parser:  Dictionary with defined parsers with the keys 'parser_def', 'label' and 'end_marker'.
        """
        if not parser.label:
            return

        if parser.skip_line and parser.skip_line(line):
            return

        label = parser.label(line.rstrip(), cache["line_num"])
        if label not in parser.parser_def:
            return

        fields = parser.parser_def[label]["fields"]
        values: Dict[str, str] = dict()
        if isinstance(fields, dict):
            for field, idx in fields.items():
                values[field] = line[slice(*idx)].strip(parser.parser_def[label].get("strip"))
        elif isinstance(fields, list):
            for field, value in zip(fields, line.split(parser.parser_def[label].get("delimiter"))):
                if field is not None:
                    values[field] = value.strip(parser.parser_def[label].get("strip"))

        parse_func = parser.parser_def[label]["parser"]
        parse_func(values, cache)
