#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ["readFileLines"]

def readFileLines(filepath):
    "Get stripped lines of a given file"
    with open(filepath) as fin:
        return [l.strip() for l in fin.read().split("\n")]
