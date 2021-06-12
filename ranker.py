import numpy as np
import PySimpleGUI as gui
import random
import pickle

FACTOR = 32
STARTING_ELO = 1000
TYPES = [('CREATOR', 'U60'), ('ITEM', 'U100'), ('YEAR', int), ('ELO', int), ('MATCHES', int)]
COMP_BUTTON_TOOLTIP = "Click to select %"
PICKLE_FILE = "rankerDoNotDelete.p"
MATRIX_SAVE_NAME = "rankerDoNotDelete_%.npy"

def main():
    gui.theme('DarkTeal4')
    layout = [
        [gui.Button("Create New Workspace", key="addnewspace", tooltip="Click to create a new workspace, using the items entered below"), gui.Button("Load Existing Workspace", key="loadexistingspace", tooltip="Click to load a workspace that you've previously created")],
        [gui.Text("Workspace: ", key="workspacetext", size=(30, 1))],
        [gui.Multiline(size=(88, 20), key="input", default_text="Copy and paste items from Excel (or other spreadsheet) here.\nYou can include up to three fields, but only one, item, is required.\nThe fields are creator, item (movie, song, etc.), and year, in that order.\n\nSo the format of entires should look like this (optional entries in brackets):\n[creator] item [year]")],
        [IButton("Start Comparing!", key="launchcomparison", tooltip="Click to start comparing entires in your workspace", visible=False), IButton("Add More to Workspace", key="addmoreto", visible=False, tooltip="Click to add more items to the current workspace, using the items entered below"), IButton("See Rankings", key="seerankings", visible=False, tooltip="Click to see the current rankings of your items for this workspace, based on comparisons made so far")]
    ]
    inputParsedMatrix = False
    workspaceName = ""
    window = gui.Window("Ranker", layout)
    while True:
        event, values = window.read()
        if event == 'launchcomparison':
            startComparisons(inputParsedMatrix)
            saveExistingWorkspace(inputParsedMatrix, workspaceName)
        elif event == 'seerankings':
            launchResultsPage(inputParsedMatrix);
        elif event == 'loadexistingspace':
            inputParsedMatrix, workspaceName = loadExistingWorkspace(getWorkspaceNames())
            if inputParsedMatrix is not False:
                window["launchcomparison"].Update(visible=True)
                window["addmoreto"].Update(visible=True)
                window["seerankings"].Update(visible=True)
                window["workspacetext"].Update("Workspace: " + workspaceName)
            else:
                createErrorPopup("Failed to load workspace, save file may have been deleted.")
        elif event == "addnewspace":
            inputParsedMatrix = parseInput(values["input"], False)
            if inputParsedMatrix is not False:
                workspaceName = launchGetNamePopup(getWorkspaceNames())
                addToWorkspaceNames(workspaceName)
                window["launchcomparison"].Update(visible=True)
                window["addmoreto"].Update(visible=True)
                window["seerankings"].Update(visible=True)
                window["workspacetext"].Update("Workspace: " + workspaceName)
                window.Element("input").update("Data added to Ranker:\n" + values["input"])
        elif event == "addmoreto":
            updatedMatrix = parseInput(values["input"], inputParsedMatrix)
            if updatedMatrix is not False:
                inputParsedMatrix = updatedMatrix
                window.Element("input").update("Data added to Ranker:\n" + values["input"])
        elif event in (None, 'Exit'):
            break

def startComparisons(inputParsedMatrix):
    oldMatchData = None
    matchData = getNextMatch(inputParsedMatrix)
    layout = [
        [gui.Text("Total Comparisons Made: " + str(int(sum(inputParsedMatrix["MATCHES"]/2))), key="counter", size=(71, 1)), gui.Button("Undo Last", key="undo", tooltip="Click to undo your last selection", visible=False)],
        [gui.Button(matchData["stringA"], size=(80, 1), key="optiona", tooltip=COMP_BUTTON_TOOLTIP.replace("%", matchData["stringA"]))],
        [gui.Button(matchData["stringB"], size=(80, 1), key="optionb", tooltip=COMP_BUTTON_TOOLTIP.replace("%", matchData["stringB"]))],
        [gui.Button("Skip", key="skip", tooltip="Click to skip this comparison and see a new one"), gui.Button("Close and Save", key="exitcomps", tooltip="Click to exit the comparison screen and go back to the main screen")]
    ]
    window = gui.Window("Comparisons", layout)
    while True:
        event, values = window.read()
        if event == "optiona" or event == "optionb":
            updateMatrixFromResult(inputParsedMatrix, matchData["indexA"] if event == "optiona" else matchData["indexB"], matchData["indexA"] if event == "optionb" else matchData["indexB"])
            oldMatchData = matchData
            matchData = getNextMatch(inputParsedMatrix)
            updateComparisonButtons(window, matchData)
        elif event == "skip":
            oldMatchData = matchData
            matchData = getNextMatch(inputParsedMatrix)
            updateComparisonButtons(window, matchData)
        elif event == "undo":
            matchData = oldMatchData
            oldMatchData = None
            undoLastResult(inputParsedMatrix, matchData)
            updateComparisonButtons(window, matchData)
        elif event in (None, 'Exit', 'exitcomps'):
            window.close()
            break
        window["undo"].Update(visible=bool(oldMatchData))
        window["counter"].Update("Total Comparisons Made: " +  str(int(sum(inputParsedMatrix["MATCHES"]/2))))

def launchResultsPage(matrix):
    resultString = "Rank\tCreator\tItem\tYear\tScore"
    rank = 1
    for shit in np.sort(matrix, order="ELO")[::-1]:
        resultString = resultString + "\n" + str(rank) + "\t" + shit["CREATOR"] + "\t" + shit["ITEM"] + "\t" + getDisplayYear(shit["YEAR"]) + "\t" + str(shit["ELO"])
        rank += 1
    layout = [[gui.Text("Current results (this can be copied and pasted directly into Excel):")],[gui.Multiline(size=(75, 21), default_text=resultString)]]
    window = gui.Window("Results Screen", layout)
    window.read()

def launchGetNamePopup(existingNames):
    layout = [
        [gui.Text("Name your new workspace:")],
        [gui.Input(key="input"), gui.Button("Submit")],
    ]
    window = gui.Window("Input Workspace Name", layout)
    nameToReturn = ""
    while True:
        event, values = window.read()
        if event == 'Submit':
            nameToReturn = values["input"]
            if nameToReturn == "" or nameToReturn in existingNames:
                createErrorPopup("Names cannot be blank or be the same as an existing workspace!\nUpdate the name or risk old workspaces being overrode!")
                continue
            else:
                window.close()
                break
        elif event in (None, 'Exit'):
            window.close()
            break
    return nameToReturn

def getDisplayYear(year):
    if year == 0:
        return ""
    return str(year)

def createErrorPopup(message):
    layout = [[gui.Text(message)],[gui.OK()]]
    window = gui.Window("Error", layout)
    while True:
        event, values = window.read()
        if event in (None, "Exit", "OK"):
            break
    window.close()

def IButton(*args, **kwargs):
    return gui.Col([[gui.Button(*args, **kwargs)]], pad=(0,0))

def loadExistingWorkspace(names):
    layout = [
        [gui.Text("Select a workspace from the list:")],
        [gui.InputCombo([x for x in names], size=(15,1), key='combo')],
        [gui.Button("Submit")]
    ]
    window = gui.Window("Workspace Loader", layout)
    while True:
        event, values = window.read()
        window.close()
        break
    workspaceName = values['combo']
    if workspaceName:
        try:
            file = MATRIX_SAVE_NAME.replace("%", workspaceName)
            return (np.load(file), workspaceName)
        except:
            return (False, "")
    return (False, "")

def getWorkspaceNames():
    try: #if file exists, load it
        return pickle.load(open(PICKLE_FILE, "rb"))["names"]
    except: #if file doesn't exist, create it
        pickle.dump({"names" : []}, open(PICKLE_FILE, "wb"))
        return []

def addToWorkspaceNames(name):
    namesList = pickle.load(open(PICKLE_FILE, "rb"))
    namesList["names"].append(name)
    pickle.dump(namesList, open(PICKLE_FILE, "wb"))

def saveExistingWorkspace(matrix, name):
    fileName = MATRIX_SAVE_NAME.replace("%", name)
    np.save(fileName, matrix)

def updateComparisonButtons(window, matchData):
    stringA = matchData["stringA"]
    stringB = matchData["stringB"]
    window["optiona"].Update(stringA)
    window["optionb"].Update(stringB)
    window["optiona"].set_tooltip(COMP_BUTTON_TOOLTIP.replace("%", stringA))
    window["optionb"].set_tooltip(COMP_BUTTON_TOOLTIP.replace("%", stringB))

def parseInput(rawInput, currentMatrix):
    values = []
    while rawInput[-1:] == "\n": #Trailing newlines would give us dummy rows
        rawInput = rawInput[:-1]
    newLineDividedInput = rawInput.split("\n")
    for line in newLineDividedInput:
        tabDividedLine = line.split("\t")
        numberOfVals = len(tabDividedLine)
        creator = ""
        item = ""
        year = 0
        if numberOfVals == 1: #only given item
            item = tabDividedLine[0]
        elif numberOfVals == 3: #all fields given
            creator = tabDividedLine[0]
            item = tabDividedLine[1]
            year = int(tabDividedLine[2] if tabDividedLine[2].isnumeric() else 0)
        elif tabDividedLine[1].isnumeric(): #given item and year
            item = tabDividedLine[0]
            year = int(tabDividedLine[1])
        else: #given creator and item (or year val was bad)
            creator = tabDividedLine[0]
            item = tabDividedLine[1]
        values.append((creator, item, year, STARTING_ELO, 0))
    if currentMatrix is not False:
        return addToMatrix(currentMatrix, values)
    return createMatrix(values)

def createMatrix(values):
    matrix = np.array(values, dtype=TYPES)
    return matrix

def addToMatrix(matrix, values):
    newMatrix = np.append(matrix, np.array(values, dtype=TYPES))
    return newMatrix

def updateMatrixFromResult(matrix, winningIndex, losingIndex):
    matrix[winningIndex]["MATCHES"] += 1
    matrix[losingIndex]["MATCHES"] += 1
    winnerELO, loserELO = updatedELO(matrix[winningIndex]["ELO"], matrix[losingIndex]["ELO"])
    matrix[winningIndex]["ELO"]= winnerELO
    matrix[losingIndex]["ELO"] = loserELO

def undoLastResult(matrix, data):
    matrix[data["indexA"]]["ELO"] = data["eloA"]
    matrix[data["indexB"]]["ELO"] = data["eloB"]
    matrix[data["indexA"]]["MATCHES"] -= 1
    matrix[data["indexB"]]["MATCHES"] -= 1

def getNextMatch(matrix):
    a = random.choice(np.where(matrix["MATCHES"] == min(matrix["MATCHES"]))[0])
    targetELO = matrix[a]["ELO"] #want to find opponent with similar ELO, if possible
    options = np.where((matrix["ELO"] >= targetELO-FACTOR) & (matrix["ELO"] <= targetELO+FACTOR))[0]
    b = None
    if len(options) > 1: #if length is one, only item is a
        options = options[options != a]
        b = random.choice(options)
    else: #if nothing falls in the ELO range, pick anything
        while b == a or b is None:
            b = random.randrange(len(matrix))
    return {"indexA": a, "indexB": b, "stringA": constructMatchString(matrix, a), "stringB": constructMatchString(matrix, b), "eloA": matrix[a]["ELO"], "eloB": matrix[b]["ELO"]}

def constructMatchString(matrix, index):
    if matrix[index]["CREATOR"] != "":
        return matrix[index]["CREATOR"] + " - " + matrix[index]["ITEM"]
    return matrix[index]["ITEM"]

def updatedELO(winnerELO, loserELO):
    expWinner = 1/(1+10**((loserELO-winnerELO)/400))
    expLoser = 1/(1+10**((winnerELO-loserELO)/400))
    return (round(winnerELO + FACTOR*(1-expWinner)), round(loserELO + FACTOR*(-expLoser)))

main()
