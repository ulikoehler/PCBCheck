#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gzip
from collections import namedtuple, defaultdict
import os.path
from Utils import readFileLines

ToolSet = namedtuple("ToolSet", ["metadata", "tools"])
Tool = namedtuple("Tool", ["num", "type", "size", "info"]) # size in mil

def structured_array_to_tool(d):
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
