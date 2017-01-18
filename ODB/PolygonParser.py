#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODB++ polygon parser components
"""
import re
from collections import namedtuple
from enum import Enum
from .Structures import Point
from .Decoder import DecoderOption

__all__ = ["Polygon", "PolygonSegment", "PolygonCircle",
           "PolygonBeginTag", "PolygonSegmentTag", "PolygonCircleTag", "PolygonEndTag",
           "PolygonType", "CircleDirection", "polygon_parser_options"]

# Polygon steps consist of PolygonSegment and PolygonCircle objects
Polygon = namedtuple("Polygon", ["start", "type", "steps"])
PolygonSegment = namedtuple("PolygonSegment", ["start", "end"])
PolygonCircle = namedtuple("PolygonCircle", ["start", "end", "center", "direction"])


PolygonBeginTag = namedtuple("PolygonBeginTag", ["end", "type"])
PolygonSegmentTag = namedtuple("PolygonSegmentTag", ["end"])
PolygonCircleTag = namedtuple("PolygonCircleTag", ["end", "center", "direction"])
PolygonEndTag = namedtuple("PolygonEndTag", [])

# Enums
class PolygonType(Enum):
    """Type of a polygon"""
    Island = 1
    Hole = 2

_polygon_type_map = {
    "I": PolygonType.Island,
    "H": PolygonType.Hole
}

class CircleDirection(Enum):
    """Direction of a circle in a polygon"""
    Clockwise = 1
    CounterClockwise = 2
    
_circle_direction_map = {
    "Y": CircleDirection.Clockwise,
    "N": CircleDirection.CounterClockwise
}

# Regular expressions for contour syntax
_ob_re = re.compile(r"^OB\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+([IH])")
_os_re = re.compile(r"^OS\s+(-?[\.\d]+)\s+(-?[\.\d]+)")
_oc_re = re.compile(r"^Oc\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+([YN])")
_oe_re = re.compile(r"^OE\s*$")

def _parse_os(match):
    "Parse a polynom segment tag regex match"
    x, y = match.groups()
    return PolygonSegmentTag(Point(float(x), float(y)))

def _parse_oc(match):
    "Parse a polynom circle tag regex match"
    xe, ye, xc, yc, cw = match.groups()
    return PolygonCircleTag(Point(float(xe), float(ye)),
                            Point(float(xc), float(yc)),
                            _circle_direction_map[cw])

def _parse_oe(match):
    "Parse a polynom end tag regex match"
    return PolygonEndTag()

def _parse_ob(match):
    "Parse a polynom begin tag regex match"
    x, y, ptype = match.groups()
    return PolygonBeginTag(Point(float(x), float(y)),
                           _polygon_type_map[ptype]) # Empty step list

polygon_parser_options = [
    DecoderOption(_ob_re, _parse_ob),
    DecoderOption(_os_re, _parse_os),
    DecoderOption(_oc_re, _parse_oc),
    DecoderOption(_oe_re, _parse_oe)
]
