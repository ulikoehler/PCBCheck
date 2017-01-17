#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gzip
from zipfile import ZipFile

__all__ = ["readFileLines", "readGZIPFileLines", "readZIPFileLines"]

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

