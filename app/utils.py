# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions."""
from csv import reader as csv_reader
from csv import writer as csv_writer
from csv import DictReader as csv_DictReader
from csv import DictWriter as csv_DictWriter
from json import dump, load
import re


def read_file(filename, mode="r", encoding="utf-8"):
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
    assert isinstance(filename, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        data = f.read()

    assert isinstance(data, str)
    return data


def write_file(filename, data, mode="w", encoding="utf-8"):
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
    assert isinstance(filename, str)
    assert isinstance(data, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        f.write(data)


def read_json(filename, mode="r", encoding="utf-8"):
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
    assert isinstance(filename, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        data = load(f)

    assert isinstance(data, dict) or isinstance(data, list)
    return data


def write_json(filename, data, mode="w", encoding="utf-8"):
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
    assert isinstance(filename, str)
    assert isinstance(data, dict) or isinstance(data, list)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        dump(data, f, indent=2)


def read_csv(filename, newline="", delimiter=",", quotechar='"', encoding="utf-8"):
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
    assert isinstance(filename, str)
    assert isinstance(newline, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)
    assert isinstance(encoding, str)

    with open(filename, newline=newline, encoding=encoding) as csvfile:
        csv_reader = csv_reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        assert isinstance(csv_reader, csv.reader)
        return csv_reader


def write_csv(
    data, filename, newline="", delimiter=",", quotechar='"', encoding="utf-8"
):
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
    assert isinstance(data, list)
    assert isinstance(filename, str)
    assert isinstance(newline, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)
    assert isinstance(encoding, str)

    with open(filename, "w", newline=newline, encoding=encoding) as csvfile:
        writer = csv_writer(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in data:
            writer.writerow(row)


def read_csv_as_dicts(
    filename, newline="", delimiter=",", quotechar='"', encoding="utf-8"
):
    """Read in CSV file into a list of :class:`dict`.

    This offers an easy import functionality of your data from CSV files.
    See more at
    `csv <https://docs.python.org/3/library/csv.html>`_.

    CSV file structure:
    1) The header row contains the column names.
    2) A row contains one dataset
    3) A column contains one specific attribute.

    Recommendation: Name the column name the way you want the attribute to be
    named later in your Dataverse object. See the
    `pyDataverse templates <https://github.com/AUSSDA/pyDataverse_templates>`_
    for this. The created :class:`dict` can later be used for the `set()`
    function to create Dataverse objects.

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
    assert isinstance(filename, str)
    assert isinstance(newline, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)
    assert isinstance(encoding, str)

    with open(filename, "r", newline=newline, encoding=encoding) as csvfile:
        reader = csv_DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)
        data = []
        for row in reader:
            data.append(dict(row))
    assert isinstance(data, list)
    return data


def write_dicts_as_csv(data, fieldnames, filename, delimiter=",", quotechar='"'):
    """Write :class:`dict` to a CSV file

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
    assert isinstance(data, str)
    assert isinstance(fieldnames, list)
    assert isinstance(filename, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)

    with open(filename, "w", newline="") as csvfile:
        writer = csv_DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for d in data:
            for key, val in d.items():
                if isinstance(val, dict) or isinstance(val, list):
                    d[key] = json.dump(val)
            writer.writerow(d)


def is_valid_doi(doi):
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
    is_valid = False
    for pat in patterns:
        if re.match(pat, doi, re.IGNORECASE):
            is_valid = True
    return is_valid
