# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions."""
import re
from csv import DictReader
from csv import DictWriter
from csv import reader
from csv import writer
from json import dump
from json import dumps
from json import load
from typing import Iterator
from typing import List


def read_file(filename: str, mode: str = "r", encoding: str = "utf-8") -> str:
    """Read in a file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    mode : str
        Read mode of file. Defaults to `r`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    Returns
    -------
    str
        Returns data as string.

    """
    with open(filename, mode, encoding=encoding) as f:
        data = f.read()

    return data


def write_file(
    filename: str, data: str, mode: str = "w", encoding: str = "utf-8"
) -> None:
    """Write data in a file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    data : str
        Data to be stored.
    mode : str
        Read mode of file. Defaults to `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    """
    with open(filename, mode, encoding=encoding) as f:
        f.write(data)


def read_json(filename: str, mode: str = "r", encoding: str = "utf-8") -> dict:
    """Read in a json file.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    filename : str
        Filename with full path.
    mode : str
        Read mode of file. Defaults to `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    dict
        Data as a json-formatted string.

    """
    with open(filename, mode, encoding=encoding) as f:
        data = load(f)

    return data


def write_json(
    filename: str, data: dict, mode: str = "w", encoding: str = "utf-8"
) -> None:
    """Write data to a json file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    data : dict
        Data to be written in the JSON file.
    mode : str
        Write mode of file. Defaults to `w`. See more at
        https://docs.python.org/3/library/functions.html#open
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    """
    with open(filename, mode, encoding=encoding) as f:
        dump(data, f, indent=2)


def read_csv(
    filename: str,
    newline: str = "",
    delimiter: str = ",",
    quotechar: str = '"',
    encoding: str = "utf-8",
) -> Iterator[List[str]]:
    """Read in a CSV file.

    See more at `csv <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    filename : str
        Full filename with path of file.
    newline : str
        Newline character.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    reader
        Reader object, which can be iterated over.

    """
    with open(filename, newline=newline, encoding=encoding) as csvfile:
        csv_reader = reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        return csv_reader


def write_csv(
    data: list,
    filename: str,
    newline: str = "",
    delimiter: str = ",",
    quotechar: str = '"',
    encoding: str = "utf-8",
) -> None:
    """Short summary.

    See more at `csv <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    data : list
        List of :class:`dict`. Key is column, value is cell content.
    filename : str
        Full filename with path of file.
    newline : str
        Newline character.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    """
    with open(filename, "w", newline=newline, encoding=encoding) as csvfile:
        csv_writer = writer(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in data:
            csv_writer.writerow(row)


def read_csv_as_dicts(
    filename: str,
    newline: str = "",
    delimiter: str = ",",
    quotechar: str = '"',
    encoding: str = "utf-8",
) -> List[dict]:
    """Read in CSV file into a list of :class:`dict`.

    This offers an easy import functionality of your data from CSV files.
    See more at
    `csv <https://docs.python.org/3/library/csv.html>`_.

    CSV file structure:
    1) The header row contains the column names.
    2) A row contains one dataset
    3) A column contains one specific attribute.

    Parameters
    ----------
    filename : str
        Filename with full path.
    newline : str
        Newline character.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    list
        List with one :class:`dict` each row. The keys of a :class:`dict` are
        named after the columen names.

    """
    with open(filename, "r", newline=newline, encoding=encoding) as csvfile:
        reader = DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)
        data = []
        for row in reader:
            data.append(dict(row))
    return data


def write_dicts_as_csv(
    data: dict, fieldnames: list, filename: str, delimiter: str = ","
) -> None:
    """Write :class:`dict` to a CSV file.

    This offers an easy export functionality of your data to a CSV files.
    See more at `csv <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    data : dict
        Dictionary with columns as keys, to be written in the CSV file.
    fieldnames : list
        Sequence of keys that identify the order of the columns.
    filename : str
        Filename with full path.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.

    """
    with open(filename, "w", newline="") as csvfile:
        csv_writer = DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
        csv_writer.writeheader()

        for d in data:
            for key, val in d.items():
                if isinstance(val, dict) or isinstance(val, list):
                    d[key] = dumps(val)
            csv_writer.writerow(d)


def is_valid_doi(doi: str) -> bool:
    """Validate a DOI via regular expressions.

    Parameters
    ----------
    doi : string
        A single DOI to be validated.

    Returns
    -------
    bool
        True, if DOI is valid, False if not.

    """
    patterns = [
        r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$",
        r"^10.1002/[^\s]+$",
        r"^10.\d{4}/\d+-\d+X?(\d+)\d+<[\d\w]+:[\d\w]*>\d+.\d+.\w+;\d$",
        r"^10.1021/\w\w\d+$",
        r"^10.1207\/[\w\d]+\&\d+_\d+$",
    ]
    for pat in patterns:
        if re.match(pat, doi, re.IGNORECASE):
            return True
    return False
