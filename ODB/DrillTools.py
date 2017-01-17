#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gzip
from collections import namedtuple, defaultdict
import os.path
from Utils import readFileLines

ToolSet = namedtuple("ToolSet", ["metadata", "tools"])
Tool = namedtuple("Tool", ["num", "type", "size", "info"]) # size in mil

def try_parse_number(s):
    "Return int(s), float(s) or s if unparsable"
    try:
        return int(s)
    except ValueError: # Try float or return s
        try:
            return float(s)
        except:
            return s

def parse_tools_raw(lines):
    "Parse tools lines into dictionaries"
    metadata = {}
    tools = []
    current_tool = None
    for line in lines:
        if line == "TOOLS {":
            current_tool = defaultdict(lambda: None)
        if "=" in line:
            k, _, v = line.partition("=")
            if current_tool is None:
                metadata[k] = try_parse_number(v)
            else: # Add to current tool
                current_tool[k] = try_parse_number(v)
        if line == "}":
            if current_tool is not None:
                tools.append(current_tool)
            current_tool = None
    if current_tool is not None:
        tools.append(current_tool)
    return metadata, tools

def dict_to_tool(d):
    # Remove keys which are used in the tool directl
    info = {
        k: v for k, v in d.items()
        if k not in ["NUM", "TYPE", "DRILL_SIZE"]
    }
    return Tool(d["NUM"], d["TYPE"], d["DRILL_SIZE"], info)

def parse_tools(lines):   
    metadata, tools = parse_tools_raw(lines)
    tools = (dict_to_tool(tool) for tool in tools)
    toolmap = {
        tool.num: tool for tool in tools
    }
    return ToolSet(metadata, toolmap)

def parse_tool_file(odbpath):
    lines = readFileLines(os.path.join(odbpath, "steps/pcb/layers/through_drill/tools"))
    return parse_tools(lines)

if __name__ == "__main__":
    #Parse commandline arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The ODB directory")
    args = parser.parse_args()
    #Perform check
    toolset = parse_tool_file(args.directory)
    print("Metadata:")
    for k, v in toolset.metadata.items():
        print("\t{} = {}".format(k, v))

    print("\nTools:")
    for tool in toolset.tools.values():
        print("\t{}".format(tool))
