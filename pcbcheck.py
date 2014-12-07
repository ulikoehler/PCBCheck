#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import sys
from collections import namedtuple, defaultdict
import subprocess
import re
from ansicolor import red, yellow, green, black

def readFileLines(filepath):
    "Get stripped lines of a given file"
    with open(filepath) as fin:
        return [l.strip() for l in fin.read().split("\n")]

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
    lines = readFileLines(filepath)
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

#Multimap of allowed layer notes (ExpectedFile.name --> [%LN])
#Built for diptrace. Might need to be adjusted for other EDA tools.
allowedLayerNotes = defaultdict(list)
allowedLayerNotes.update({
    "Top copper layer": ["Top"],
    "Bottom copper layer": ["Bottom"],
    "Solder mask top": ["TopMask"],
    "Solder mask bottom": ["BotMask"],
    "Board outline": ["BoardOutline"],
    "Board outline": ["BoardOutline"],
    "Silk screen top": ["TopSilk"],
})

def checkGerberFile(self, filepath):
    """
    Check if the given file is a RS-274X gerber file
    - Checks for a G04 command at the beginning of the file
    - Checks for a %LN command and verifies it against the filename
    """
    filename = os.path.basename(filepath)
    lines = readFileLines(filepath)
    #Find G04 line (i.e. what software created the file)
    if not any(map(lambda l: l.startswith("G04 "), lines)):
        print (red("Couldn't find G04 command (software description) in %s. Probably not a Gerber file." % filename, bold=True))
    #Find %LN line, i.e. what the creating
    # software thinks the current layer is (e.g. "BottomMask")
    layerNoteRegex = re.compile(r"^\%LN([^\*]+)\*%$")
    layerDescription = None
    for line in lines:
        if layerNoteRegex.match(line):
            layerDescription = layerNoteRegex.match(line).group(1)
            break #Expecting only one layer note
    #Check if the layer note we found makes sense
    if layerDescription == None: #No %LN line found
        print (yellow("Couldn't find %%LN command (layer description) in %s" % filename))
    else: #We found a layer description. Check for sanity
        if layerDescription not in allowedLayerNotes[self.name]:
            print (red("Layer description '%s' in %s does not match any of the expected descriptions: %s" % (layerDescription, filename, allowedLayerNotes[self.name]), bold=True))

def extractProjectPrefix(files):
    """
    Extract a common project prefix from all files in a directory
    Fails & exits if no such prefix is found
    Example: [ABC.top, ABC.bot] => "ABC"
    """
    commonprefix = os.path.commonprefix(files)
    if not commonprefix or not commonprefix.endswith("."):
        print red("Can't extract project name from files: %s" % ", ".join(files), bold=True)
        print red("Please ensure that all files have a common filename and only differ in their extension!", bold=True)
        print red("Example: MyBoard.top, MyBoard.bot, ...", bold=True)
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

ExpectedFile = namedtuple('ExpectedFile', ['extension', 'name', 'checkFN'])
expectedFiles = [
    #http://www.multi-circuit-boards.eu/support/leiterplatten-daten/gerber-daten.html
    ExpectedFile(".top", "Top copper layer", checkGerberFile),
    ExpectedFile(".bot", "Bottom copper layer", checkGerberFile),
    ExpectedFile(".smt", "Solder mask top", checkGerberFile),
    ExpectedFile(".smb", "Solder mask bottom", checkGerberFile),
    ExpectedFile(".plt", "Silk screen top", checkGerberFile),
    ExpectedFile(".mil", "Board outline", checkGerberFile),
    #Drilling
    ExpectedFile(".pth", "Plated through holes", checkExcellonMetric),
    ExpectedFile(".npth", "Non-plated through holes", checkExcellonMetric),
]

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
