# importing glob for it file handling capabilities
import glob
# import re for its regex capabilities
import re
# importing scipy as signal for use of its butterworth filter
from scipy import signal
# importing os module
import os
# importing math
import math
# importing statistics
import statistics

# import workbook to create excel sheets
from xlwt import Workbook

# Define all major functions for program____________________________________________________________
# ___________________________________________________________________________________________________

'''NOTE: For accessing mainList format is following
              0   1   2   3   4   5    6     7
mainList[set][fx, fy, fz, mx, my, mz, CoPx, CoPy]'''

'''NOTE: For accessing filteredList format is following

filteredList[set][CoPxList, CoPyList]'''


def findSizeofData(mainList):
    """Find full size of examples present in mainList by looping
    through each set and checking length of list.
    """
    size = 0
    for set in mainList:
        for i in set:
            size += len(i)
    return size


def filterData(mainList):
    """Filter the main data list using a butterworth filter on each
    CoPx and CoPy creating a sublist of all filtered CoPx and a sublist 
    for all filtered CoPy
    Output a filteredList with both sublists appended for each set in the 
    mainList
    """
    filteredList = []
    # Apply a low pass, fourth order butterworth filter at 8hz to the 3-D dataset.
    b, a = signal.butter(4, 8/500, 'lowpass')
    index = 0
    for set in mainList:
        subList = []
        if set != None:
            subList.append(list(signal.filtfilt(
                b, a,  groupCoPx(set), padlen=0)))
            subList.append(list(signal.filtfilt(
                b, a,  groupCoPy(set), padlen=0)))
        filteredList.append(list(subList))
    return filteredList


def groupCoPx(mainList):
    # Helper function to get a list of all CoPx ready to filter
    copXlist = []
    for x in range(len(mainList)):
        copXlist.append(mainList[x][6])
    return copXlist


def groupCoPy(mainList):
    # Helper function to get a list of all CoPy ready to filter
    copYlist = []
    for y in range(len(mainList)):
        copYlist.append(mainList[y][7])
    return copYlist


def calcCop(mx, my, fz):
    """Calculate the CoPx and CoPy values
    NOTE: These are the measure of Center of Pressure.
    Reflects the neuromuscular response to maintain stability
    """
    _copX, _copY = 0, 0
    _copX = -my/fz
    _copY = mx/fz
    return _copX, _copY


def calculateDisplacement(CopA, CopB):
    return CopB - CopA


def calculateVelocity(Displacement, TimeA, TimeB):
    return Displacement/(TimeB - TimeA)


def calculatePathlength(displacementXA, displacementYA):
    return (math.sqrt(pow(displacementXA, 2) + pow(displacementYA, 2)))


def calculateValues(dX, dY, vX, vY, pL, lineOfValues, timeValues, lastValues=[]):
    """This is the main function that will calculate all the extra values needed for 
        each block of values.
    param: dX, dY = lists for displacementX, displacementY vX,vY: lists for velocityX, velocityY
        pL = list for pathLength, lineOfValues = filteredList[i], timeValues = timeList[i]
        lastValues = [copx, copy, timeValue]"""

    # handle the last line of values from previous list, or handle first append if list is empty
    if (len(lastValues) == 0):
        dX.append(0.0)
        dY.append(0.0)
        vX.append(0.0)
        vY.append(0.0)
        pL.append(0.0)
    else:
        dX.append(calculateDisplacement(
            lastValues[0], lineOfValues[0][0]))
        dY.append(calculateDisplacement(
            lastValues[1], lineOfValues[1][0]))
        vX.append(calculateVelocity(
            dX[len(dX)-1], lastValues[2], timeValues[0]))
        vY.append(calculateVelocity(
            dY[len(dY)-1], lastValues[2], timeValues[0]))
        pL.append(calculatePathlength(
            dX[len(dX)-1], dY[len(dY)-1]))

    # Run a for loop with the range through one of the lists it shouldn't matter which one you choose because they should both be the same side.

    for index in range(len(lineOfValues[0]) - 1):
        dX.append(calculateDisplacement(
            lineOfValues[0][index], lineOfValues[0][index + 1]))
        dY.append(calculateDisplacement(
            lineOfValues[1][index], lineOfValues[1][index + 1]))
        vX.append(calculateVelocity(
            dX[len(dX)-1], timeValues[index], timeValues[index + 1]))
        vY.append(calculateVelocity(
            dY[len(dY)-1], timeValues[index], timeValues[index + 1]))
        pL.append(calculatePathlength(
            dX[len(dX)-1], dY[len(dY)-1]))
    # remember last values for next run: [last copx, last copy, last timeValue]
    lastValues = [lineOfValues[0][len(
        lineOfValues)-1], lineOfValues[1][len(lineOfValues)-1], timeValues[len(timeValues)-1]]
    return dX, dY, vX, vY, pL, lastValues

# Define MAIN FUNCTION_____________________________________________________________________________________
# __________________________________________________________________________________________________________


def main():
    # Creating the directory that we will be putting the new files into.
    # Directory
    directory = "Excel Calculation Files"
    # Parent Directory path
    parent_dir = os.getcwd()
    # Path
    path = os.path.join(parent_dir, directory)
    # Create the directory
    # 'Calculation Files' in
    # '/home / User / Documents'
    # print(os.path.isdir(path))
    if os.path.isdir(path) == False:
        os.mkdir(path)
        print("Directory '% s' created" % directory)

    # Create a list of all the text files in the the folder.
    txtfiles = []
    for file in glob.glob("*.txt"):
        txtfiles.append(file)
        print(file)

    for current_file in txtfiles:
        # Get text file(s) from current directory, prepare excel file
        newFileName = current_file.replace('.txt', '_CalculatedFile.xls')
        # Open each text file.
        f = open(current_file, "r")
        # Read from the file line by line.
        f1 = f.readlines()
        mainList = []  # We will be doing all of our calculations on this list.
        timeList = []  # We will hold all the times on here.
        timeSubList = []  # Represents each set of times
        subList = []    # Represents each set of movement data
        maxApCopX, maxMLCopY = 0, 0

        # Go through each of the lines and using the Regex below to parse each string
        for line in f1:
            res = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            # NOTE: sample line:
            # 01 timestamp(ms):40440.73 force plate (fx, fy, fz, mx, my, mz):10.60986,-24.49137,17.896,-18.85504,-21.14655,0.6189079

            # Convert each number in from our regular expression from a string back into a float.
            for index in range(len(res)):
                # Convert the regex from string back into a float number so we can work with it.
                res[index] = float(res[index])
            # Currently we only want lines that have 1.0 in the title.
            if len(res) != 0 and res[0] == 1.0:
                # Append res to our subList.
                res.pop(0)  # clear number before timestamp
                timestamp = res.pop(0)  # gets timestanp
                # res[0] goes from number to timestamp to fx
                timeSubList.append(timestamp)
                # Calculate COPX and COPY beforehand and place it in the subList.
                copx, copy = calcCop(res[3], res[4], res[2])
                # Check for Max values
                maxApCopX = max(maxApCopX, copx)
                maxMLCopY = max(maxMLCopY, copy)
                res.append(copx)  # COPX at position [6], -My/Fz
                res.append(copy)  # COPY at position [7], Mx/Fz
                subList.append(res)
            # When we finally see a 2.0 set is complete, append subList to our mainList.
            elif len(res) != 0 and res[0] == 2.0:
                if len(subList) != 0:
                    # Putting a copy of it in mainList so when we clear it we don't delete the list.
                    mainList.append(list(subList))
                    timeList.append(list(timeSubList))
                    timeSubList.clear()
                    subList.clear()
        f.close()

        # Prepare lists to populate excel sheet with values and statistical analysis
        displacementX = []
        displacementY = []
        velocityX = []
        velocityY = []
        pathLength = []
        # maxVelocityX, maxVelocityY = 0, 0
        # minVelocityX, minVelocityY = 0, 0
        # meanVelocityX, meanVelocityY = 0, 0
        filteredList = filterData(mainList)

        index = 0
        lastValues = []
        for stage in filteredList:
            displacementX, displacementY, velocityX, velocityY, pathLength, lastValues = calculateValues(
                displacementX, displacementY, velocityX, velocityY, pathLength, stage, timeList[index], lastValues)
            # maxVelocityX = max(velocityX)
            # maxVelocityY = max(velocityY)
            # meanVelocityX = statistics.mean(velocityX)
            # meanVelocityY = statistics.mean(velocityY)
            index = index + 1
        asbDisplacementX = [abs(value) for value in displacementX]
        asbDisplacementY = [abs(value) for value in displacementY]

        completeName = os.path.join(path, newFileName)

        wb = Workbook()

        sheet1 = wb.add_sheet('X')
        sheet1.write(0, 0, "Time")
        sheet1.write(0, 1, "CoPx")
        sheet1.write(0, 2, "Unfiltered CoPx")
        sheet1.write(0, 3, "Distance(d)")
        sheet1.write(0, 4, "Abs Distance")
        sheet1.write(0, 5, "Velocity X")
        rowX = 0
        for set in range(len(filteredList)):
            print("timelist length: ", len(timeList[set]))
            for i in range(len(timeList[set])):
                # Timestamp
                sheet1.write(rowX+1, 0, str(timeList[set][i]))
                sheet1.write(
                    rowX+1, 1, str(round(filteredList[set][0][i], 4)))     # CoPx
                # Unfiltered CoPx
                sheet1.write(rowX+1, 2, str(mainList[set][i][6]))
                # Distance
                sheet1.write(rowX+1, 3, str(round(displacementX[rowX], 4)))
                sheet1.write(
                    rowX+1, 4, str(round(asbDisplacementX[rowX], 4)))               # Absolute Distance
                # Velocity in x direction
                sheet1.write(rowX+1, 5, str(round(velocityX[rowX], 4)))
                rowX += 1

        print("outer forloop complete")
        sheet1.write(0, 7, "Max Range")
        sheet1.write(1, 7, str(max(asbDisplacementX)))
        sheet1.write(0, 8, "Mean Range")
        sheet1.write(1, 8, str(statistics.mean(asbDisplacementX)))
        sheet1.write(0, 9, "Peak Velocity")
        sheet1.write(1, 9, str(max(velocityX)))
        sheet1.write(0, 10, "Mean Velocity")
        sheet1.write(1, 10, str(statistics.mean(velocityX)))

        sheet2 = wb.add_sheet('Y')
        sheet2.write(0, 0, "Time")
        sheet2.write(0, 1, "CoPy")
        sheet2.write(0, 2, "Unfiltered CoPy")
        sheet2.write(0, 3, "Distance(d)")
        sheet2.write(0, 4, "Abs Distance")
        sheet2.write(0, 5, "Velocity Y")
        rowY = 0
        for set in range(len(filteredList)):
            for i in range(len(timeList[set])):
                # Timestamp
                sheet2.write(rowY+1, 0, str(timeList[set][i]))
                sheet2.write(
                    rowY+1, 1, str(round(filteredList[set][1][i], 4)))  # CoPy
                # Unfiltered CoPy
                sheet2.write(rowY+1, 2, str(mainList[set][i][7]))
                # Distance
                sheet2.write(rowY+1, 3, str(round(displacementY[rowY], 4)))
                sheet2.write(
                    rowY+1, 4, str(round(asbDisplacementY[rowY], 4)))           # Absolute Distance
                # Velocity in y direction
                sheet2.write(rowY+1, 5, str(round(velocityY[rowY], 4)))
                rowY += 1

        sheet2.write(0, 7, "Max Range")
        sheet2.write(1, 7, str(max(displacementY)))
        sheet2.write(0, 8, "Mean Range")
        sheet2.write(1, 8, str(statistics.mean(displacementY)))
        sheet2.write(0, 9, "Peak Velocity")
        sheet2.write(1, 9, str(max(velocityY)))
        sheet2.write(0, 10, "Mean Velocity")
        sheet2.write(1, 10, str(statistics.mean(velocityY)))

        sheet3 = wb.add_sheet('Path')
        sheet3.write(0, 0, "Time")
        sheet3.write(0, 1, "Path")

        for i in range(len(timeList[0])):
            sheet3.write(i+1, 0, str(timeList[0][i]))
            sheet3.write(i+1, 1, str(round(pathLength[i-1], 4)))

        wb.save(completeName)


main()
