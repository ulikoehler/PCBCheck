#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import sys
from collections import namedtuple, defaultdict
import subprocess
import re
from ansicolor import red
from ansicolor import green
from ansicolor import black

def extractToolStatistics(lines):
    """
    From a list of excellon drill lines extract the number of holes for all drill sizes.
    Returns a dict: {drill size: number of holes}
    """
    #Get a tool --> diameter mapping
    tools = extractExcellonTools(lines)
    #Iterate over lines and count holes for each tool
    currentTool = None
    drillCountByDiameter = defaultdict(int)
    toolRegex = re.compile(r"^(T\d+)$")
    drillRegex = re.compile(r"^X[\+-]\d+Y[\+-]\d+$")
    for line in lines:
        if toolRegex.match(line):
            #This line defines a new tool to use
            currentTool = toolRegex.match(line).group(0)
        if drillRegex.match(line):
            drillCountByDiameter[tools[currentTool]] += 1
    return drillCountByDiameter

def extractExcellonTools(lines):
    """
    From a list of excellon lines, extract a dict of tools
    Ignores non-tool-definition lines
    Example: ["foobar", "T01C1.0", "T02C2.2"] -> {"T01": 1.0, "T02": 2.2}
    """
    #Extract those lines that match a regex
    toolDefRegex = re.compile(r"^(T\d+)C([0-9\.]+)$")
    toolDefMatches = [toolDefRegex.match(l) for l in lines if toolDefRegex.match(l)]
    return dict([(t.group(1), float(t.group(2))) for t in toolDefMatches])

def checkExcellonMetric(self, filepath):
    "Check if a given file is a metric excellon file"
    filename = os.path.basename(filepath)
    #Read lines
    with open(filepath) as fin:
        lines = [l.strip() for l in fin.read().split("\n")]
    #Check for excellon header
    if lines[0] != "M48":
        print red("Can't find Excellon drill header (M48) in %s" % filename, bold="True")
    #Check for metric dimension: Line like METRIC,0000.00
    if lines[1].partition(",")[0] != "METRIC":
        print red("Excellon drill program %s does not seem to be metric" % filename, bold="True")
    #
    # Drill statistics
    #
    toolStats = extractToolStatistics(lines)
    print(black(self.name + ":", bold=True))
    for diameter, numDrills in toolStats.iteritems():
        print("\t%d through holes of diameter %.2fmm: " % (numDrills, diameter))
    #Print "None" if there are no holes in this file
    if not toolStats:
        print "\tNone"



ExpectedFile = namedtuple('ExpectedFile', ['extension', 'name', 'checkFN'])
expectedFiles = [
    #http://www.multi-circuit-boards.eu/support/leiterplatten-daten/gerber-daten.html
    ExpectedFile(".top", "Top copper layer", None),
    ExpectedFile(".bot", "Bottom copper layer", None),
    ExpectedFile(".smt", "Solder mask top", None),
    ExpectedFile(".smb", "Solder mask bottom", None),
    ExpectedFile(".plt", "Silk screen top", None),
    ExpectedFile(".mil", "Board outline mill data", None),
    #Drilling
    ExpectedFile(".pth", "Plated through holes", checkExcellonMetric),
    ExpectedFile(".npth", "Non-plated through holes", checkExcellonMetric),
]

def extractProjectPrefix(files):
    """
    Extract a common project prefix from all files in a directory
    Fails & exits if no such prefix is found
    Example: [ABC.top, ABC.bot] => "ABC"
    """
    commonprefix = os.path.commonprefix(files)
    if not commonprefix or not commonprefix.endswith("."):
        print red("Can't extract project name from files: %s" % ", ".join(files), bold=True)
        print red("Ensure all files have a common filename and only differ in their extension!", bold=True)
        sys.exit(1)
    return commonprefix[:-1] #Strp off dot

def checkFile(directory, expectedFile, projectName):
    "Check if a given expected file exists inside a directory"
    filename = projectName + expectedFile.extension
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
        print green("Found production data %s" % filename)
        if expectedFile.checkFN is not None:
            expectedFile.checkFN(expectedFile, filepath)
    else:
        print red("File %s (%s) missing" % (filename, expectedFile.name), bold=True)
        return None
    return filename

if __name__ == "__main__":
    #Parse commandline arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="The directory to scan for project Gerber file")
    parser.add_argument("--gerbv", action="store_true", help="Run gerbv on the files")
    args = parser.parse_args()
    #Perform check
    files = os.listdir(args.directory)
    projectName = extractProjectPrefix(files)
    print black("Found project name %s" % projectName)
    checkedFiles = [checkFile(args.directory, f, projectName) for f in expectedFiles]
    unknownFiles = set(files) - set(checkedFiles)
    if unknownFiles:
        print red("Found unknown files: %s" % ",".join(unknownFiles))
    #Open viewer if enabled
    if args.gerbv:
        filePaths = [os.path.join(args.directory, f) for  f in files]
        subprocess.call(["gerbv"] + filePaths)