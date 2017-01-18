#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODB++ surface parser components
"""
import re
from enum import Enum
from collections import namedtuple
from .Decoder import DecoderOption

__all__ = ["surface_parser_options",
           "SurfaceBeginTag",
           "SurfaceEndTag", "Polarity"]

Surface = namedtuple("Surface", ["polarity", "dcode", "polygons", "attributes"])

SurfaceBeginTag = namedtuple("SurfaceBeginTag", ["polarity", "dcode", "attributes"])
SurfaceEndTag = namedtuple("SurfaceEndTag", [])

# Enums
class Polarity(Enum):
    """Polarity of a layer"""
    Positive = 1
    Negative = 2
    
_polarity_map = {
    "P": Polarity.Positive,
    "N": Polarity.Negative
}

# Surface syntax regular expressions
_surface_re = re.compile(r"^S\s+([PN])\s+(\d+)\s*(;\s*.+?)?$")
_surface_end_re = re.compile(r"^SE\s*$")

def _parse_surface_start(match):
    "Parse a surface begin tag regex match"
    polarity, dcode, attributes = match.groups()
    # Parse attribute string
    attributes = parse_attributes(attributes[1:]) \
                 if attributes is not None else {}
    return SurfaceBeginTag(_polarity_map[polarity],
                           int(dcode), attributes)

def _parse_surface_end(match):
    "Parse a surface end tag regex match"
    return SurfaceEndTag()


surface_parser_options = [
    DecoderOption(_surface_re, _parse_surface_start),
    DecoderOption(_surface_end_re, _parse_surface_end)
]
