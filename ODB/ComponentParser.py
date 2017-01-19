#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ODB++ surface parser components
"""
import re
from collections import namedtuple
from .Decoder import DecoderOption, run_decoder
from .Structures import *
from .Utils import try_parse_number

__all__ = ["components_decoder_options", "parse_components"]

_prp_re = re.compile(r"^PRP\s+(\S+)\s+'([^']+)'\s*$") # Property record
_top_re = re.compile(r"^TOP\s+(\d+)\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+([NM])\s+(\d+)\s+(\d+)\s+(\S+)\s*$") # Toeprint record
_cmp_re = re.compile(r"^CMP\s+(\d+)\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+(-?[\.\d]+)\s+([NM])\s+(\S+)\s+(\S+)\s*(;\s*.+?)?$") # component record

ComponentRecordTag = namedtuple("ComponentRecordTag",[
        "package_ref", "location", "rotation", "mirror", "name", "part_name", "attributes"])
PropertyRecordTag = namedtuple("PropertyRecord", ["key", "value"])
# _prp_re.search("PRP Name 'EEUFR1H470'")
ToeprintRecord = namedtuple("ToeprintRecord", [
        "pin_num", "location", "rotation", "mirrored", "net_num", "subnet_num", "toeprint_name"])

def _parse_prp(match):
    key, value = match.groups()
    return PropertyRecordTag(key, value)

def _parse_top(match):
    pin_num, x, y, rot, mirror, net_num, subnet_num, toeprint_name = match.groups()
    return ToeprintRecord(
        int(pin_num),
        Point(float(x), float(y)),
        float(rot),
        mirror_map[mirror],
        int(net_num),
        int(subnet_num),
        try_parse_number(toeprint_name)
    )

def _parse_cmp(match):
    pkg_ref, x, y, rot, mirror, name, part_name, attributes = match.groups()
    attributes = parse_attributes(attributes[1:]) \
                 if attributes is not None else {}
    return ComponentRecordTag(
        int(pkg_ref),
        Point(float(x), float(y)),
        float(rot),
        mirror_map[mirror],
        try_parse_number(name),
        try_parse_number(part_name),
        attributes
    )

components_decoder_options = [
    DecoderOption(_prp_re, _parse_prp),
    DecoderOption(_top_re, _parse_top),
    DecoderOption(_cmp_re, _parse_cmp)
]

def component_name_to_id(name):
    """
    Convert a section header name ("CMP 0" in DipTrace)
    to an identifier (e.g. 0)
    """
    if name.startswith("CMP"):
        return int(name[len("CMP"):].strip())
    return name

def parse_components(components):
    # Build rulesets
    return {
        component_name_to_id(name): list(run_decoder(component, components_decoder_options))
        for name, component in components.items()
    }
