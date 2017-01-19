#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parsing routines for the ODB++ netlist format
according to the ODB++ 7.0 specification:

http://www.odb-sa.com/wp-content/uploads/ODB_Format_Description_v7.pdf
"""
import re

__all__ = ["is_netlist_optimized", "parse_net_names"]

_h_optimize_re = re.compile(r"^H\s+optimize\s+([YN])\s*$", re.IGNORECASE)

def is_netlist_optimized(linerec):
    """
    Based on a netlist linerecord dict, determines if the netlist
    was optimized by the netlist optimizer.
    Returns bool (True = optimized)
    """
    # Try to look for a regex match in ANY of the lines
    metalines = linerec[None]
    potential_matches = (_h_optimize_re.match(line) for line in metalines)
    matches = filter(lambda m: m is not None, potential_matches)
    try:
        return next(matches).group(1) in ["Y", "y"]
    except StopIteration: # No such line
        raise ValueError("Can't find netlist optimization tag in line record: {}".format(linerec))


def parse_net_names(linerecords):
    """Given a netlist linerecord file, generates a dict of net ID => name mappings"""
    netnames = linerecords["Nets names"]
    splitlines = (line.partition(" ") for line in netnames)
    return {
        int(split[0][1:]): split[2] # [1:]: Throw away $ sign or whatever sign is used
        for split in splitlines
    }
