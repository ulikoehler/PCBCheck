#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gzip
from zipfile import ZipFile

__all__ = ["readFileLines", "readGZIPFileLines", "readZIPFileLines", "try_parse_number"]

def try_parse_number(s):
    """
    Return int(s), float(s) or s if unparsable.
    Also returns s if s starts with 0 unless it is "0"
    (and therefore can't be treated like a number)
    """
    if s.startswith("0") and len(s) != 1:
        return s
    # Try parsing a nmeric
    try:
        return int(s)
    except ValueError: # Try float or return s
        try:
            return float(s)
        except:
            return s

def readFileLines(filepath, open_fn=open):
    "Get stripped lines of a given file"
    with open_fn(filepath) as fin:
        return [l.strip() for l in fin.read().split("\n")]

def readGZIPFileLines(filepath):
    "Get stripped lines of a given file in gzip format"
    return readFileLines(filepath, open_fn=gzip.open)

def readZIPFileLines(filepath, codec="utf-8"):
    "Get stripped lines of a given ZIP file containing only one entry"
    with ZipFile(filepath, 'r') as thezip:
        names = thezip.namelist()
        if len(names) != 1:
            raise ValueError("ZIP files does not contain exactly one file: {}".format(names))
        return [l.strip() for l in
                thezip.read(names[0]).decode(codec).split("\n")]

