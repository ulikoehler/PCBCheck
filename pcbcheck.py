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
        print("\t%d through holes of diameter %.2fmm" % (numDrills, diameter))
    #Print "None" if there are no holes in this file
    if not toolStats:
        print "\tNone"

#Multimap of allowed layer notes (ExpectedFile.name --> [%LN])
#Built for diptrace. Might need to be adjusted for other EDA tools.
allowedLayerNotes = defaultdict(list)
allowedLayerNotes.update({
    "Top copper layer": ["Top", ['Copper', 'L1', 'Top']],
    "Bottom copper layer": ["Bottom", ['Copper', 'L2', 'Bot']],
    "Solder mask top": ["TopMask", ['Soldermask', 'Top']],
    "Solder mask bottom": ["BotMask", ['Soldermask', 'Bot']],
    "Board outline": ["BoardOutline", ['Profile']],
    "Silk screen top": ["TopSilk", ['Legend', 'Top']],
})

#Gerber aperture
# id: The aperture identifier, e.g. D11
# type: "C"/"R"
# diameter: float, with implicit units
Aperture = namedtuple("Aperture", ["id", "type", "diameter"])

def parseGerberApertures(lines):
    "From a list of gerber lines, parse all embedded apertures"
    apertureRegex = re.compile(r"%AD(D\d+)([CR]),(\d+\.\d+)\*%")
    apertures = []
    #Find lines defining apertures
    for line in lines:
        if apertureRegex.match(line):
            match = apertureRegex.match(line)
            apertures.append(Aperture(match.group(1), match.group(2), float(match.group(3))))
    return apertures

def findAperture(apertures, identifier):
    "Find an aperture in a list of apertures (returns None if not found)"
    for aperture in apertures:
        if aperture.id == identifier: return aperture
    return None

def parseGerberUnit(lines):
    """Returns the extended gerber unit ("mm"/"in") or None if not found"""
    if "%MOIN*%" in lines:
        return "in"
    elif "%MOMM*%" in lines:
        return "mm"
    else: return None

def findCoordinateFormat(lines):
    """
    Try to find a FSLAX line and return the decimal-point factor for coordinates.
    """
    rgx = re.compile(r"\%FSLAX(\d{2})Y(\d{2})\*\%")
    for line in lines:
        m = rgx.match(line)
        if m is not None:
            return 10.**int(m.group(1)[-1]),10.**int(m.group(2)[-1])
    print(red("Could not find coordinate format info %FSLAX. Using default %FSLAX33"))
    return 100000.,100000.

def checkBoardOutline(self, filepath):
    filename = os.path.basename(filepath)
    #Basic gerber checks
    checkGerberFile(self, filepath)
    #Compute board outline
    millLines = readFileLines(filepath)
    # Find factors to get absolute coordinates:
    x_factor, y_factor = findCoordinateFormat(millLines)
    #We can only interpret the file if coordinates are absolute
    if not "G90*" in millLines:
        print (yellow("Mill coordinates in %s don't seem to be absolute (G90 missing!)" % filename))
        return
    #Determine coordinate units
    unit = parseGerberUnit(millLines)
    if unit is None: #Neither inch nor mm found
        print (yellow("Could not find coordinate units (mm/in) in %s" % filename))
        return
    #Parse the aperture list
    apertures = parseGerberApertures(millLines)
    selectApertureRegex = re.compile(r"(D\d+)\*")
    move2DRegex = re.compile(r"X(\d+)Y(\d+)D(\d)\*") #Move (D2) or draw (D1)
    move1DRegex = re.compile(r"([XY])(\d+)D(\d)\*") #With only one coordinate
    #Try to interpret gerber file
    minCoords = (sys.maxsize, sys.maxsize)
    maxCoords = (0, 0)
    lastCoords = (0, 0)
    currentAperture = None
    for line in millLines:
        if selectApertureRegex.match(line):
            apertureCode = selectApertureRegex.match(line).group(1)
            currentAperture = findAperture(apertures, apertureCode)
        elif move2DRegex.match(line):
            match = move2DRegex.match(line)
            x = int(match.group(1)) / x_factor
            y = int(match.group(2)) / y_factor
        elif move1DRegex.match(line):
            match = move1DRegex.match(line)
            if match.group(1) == "X":
                x = int(match.group(2)) / x_factor
                y = lastCoords[1]
            elif match.group(1) == "Y":
                x = lastCoords[0]
                y = int(match.group(2)) / y_factor
            else: raise Exception("Internal error: Invalid coordinate type in 1D move: %s" % match.group(1))
        else: continue
        #Compute min/max coordinates
        lastCoords = (x, y)
        minCoords = (min(minCoords[0], lastCoords[0]), min(minCoords[1], lastCoords[1]))
        maxCoords = (max(maxCoords[0], lastCoords[0]), max(maxCoords[1], lastCoords[1]))
    #Compute board size (minimum enclosing rectangle)
    boardSize = (maxCoords[0] - minCoords[0], maxCoords[1] - minCoords[1])
    #Print info
    print (black("\tGerber offset: %s" % str(minCoords)))
    print (black("\tBoard size (minimum rectangle): %.1f %s x %.1f %s" % \
            (boardSize[0], unit, boardSize[1], unit)))

def checkCopperLayer(self, filepath):
    #Basic gerber checks
    checkGerberFile(self, filepath)
    #Check if smallest aperture is < 6mil = 150um
    #NOTE: We currently don't compute the clearance (way too complicated)
    lines = readFileLines(filepath)
    apertures = parseGerberApertures(lines)
    unit = parseGerberUnit(lines)
    limit = 0.152 #TODO use inches if unit == "in"
    if unit == "in": limit = 0.006
    for aperture in apertures:
        if aperture.diameter < limit:
            print red("Aperture %s (size %.3f %s) is smaller than %.3f %s minimum width" % \
                        (aperture.id, aperture.diameter, unit, limit, unit))

def checkGerberFile(self, filepath):
    """
    Check if the given file is a RS-274X gerber file
    - Checks for a G04 command at the beginning of the file
    - Checks for a %LN command and verifies it against the filename
    - Checks for a G04 #@! TF.FileFunction command
    """
    filename = os.path.basename(filepath)
    lines = readFileLines(filepath)
    #Find G04 line (i.e. what software created the file)
    if not any(map(lambda l: l.startswith("G04 "), lines)):
        print (red("Couldn't find G04 command (software description) in %s. Probably not a Gerber file." % filename, bold=True))
    #Find %LN line, i.e. what the creating
    # software thinks the current layer is (e.g. "BottomMask")
    layerNoteRegex = re.compile(r"^\%LN([^\*]+)\*%$")
    fileFunctionRegex = re.compile(r"G04 #@! TF\.FileFunction,([^\*]+)\*")
    layerDescription = None
    for line in lines:
        if layerNoteRegex.match(line):
            layerDescription = layerNoteRegex.match(line).group(1)
            break #Expecting only one layer note
        elif fileFunctionRegex.match(line):
            layerDescription = fileFunctionRegex.match(line).group(1)
            layerDescription = layerDescription.split(",")
    #Check if the layer note we found makes sense
    if layerDescription == None: #No %LN line found
        print (yellow("Couldn't find %%LN command or file function command in %s" % filename))
    else: #We found a layer description. Check for sanity
        if isinstance(layerDescription, list): # FileFunction command
            if layerDescription not in allowedLayerNotes[self.name]:
                    print (red("Layer description '%s' in %s does not match any of the expected descriptions: %s" % (layerDescription, filename, allowedLayerNotes[self.name]), bold=True))

        else: # %LN command
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
        print green("Found %s data %s" % (expectedFile.format, filename))
        if expectedFile.checkFN is not None:
            expectedFile.checkFN(expectedFile, filepath)
    else:
        print red("File %s (%s) missing" % (filename, expectedFile.name), bold=True)
        return None
    return filename

ExpectedFile = namedtuple('ExpectedFile', ['extension', 'name', 'format', 'checkFN'])
expectedFiles = [
    #http://www.multi-circuit-boards.eu/support/leiterplatten-daten/gerber-daten.html
    ExpectedFile(".top", "Top copper layer", "RS-274X", checkCopperLayer),
    ExpectedFile(".bot", "Bottom copper layer", "RS-274X", checkCopperLayer),
    ExpectedFile(".smt", "Solder mask top", "RS-274X", checkGerberFile),
    ExpectedFile(".smb", "Solder mask bottom", "RS-274X", checkGerberFile),
    ExpectedFile(".plt", "Silk screen top", "RS-274X", checkGerberFile),
    ExpectedFile(".mil", "Board outline", "RS-274X", checkBoardOutline),
    #Drilling
    ExpectedFile(".pth", "Plated through holes", "Excellon", checkExcellonMetric),
    ExpectedFile(".npth", "Non-plated through holes", "Excellon", checkExcellonMetric),
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
    print black("Project name: %s" % projectName)
    checkedFiles = [checkFile(args.directory, f, projectName) for f in expectedFiles]
    unknownFiles = set(files) - set(checkedFiles)
    if unknownFiles:
        print red("Found unknown files: %s" % ",".join(unknownFiles))
    #Open viewer if enabled
    if args.gerbv:
        filePaths = [os.path.join(args.directory, f) for  f in files]
        subprocess.call(["gerbv"] + filePaths)
