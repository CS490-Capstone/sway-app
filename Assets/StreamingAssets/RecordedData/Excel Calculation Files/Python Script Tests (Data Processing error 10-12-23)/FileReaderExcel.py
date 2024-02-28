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

import xlwt
from xlwt import Workbook

# fs = 1000  # Sampling frequency
# fc = 30  # Cut-off frequency of the filter
# w = fc / (fs / 2) # Normalize the frequency
# b, a = signal.butter(5, w, 'low')
# output = signal.filtfilt(b, a, signalc)


def findSizeofData(mainList):
    size = 0
    for x in mainList:
        for j in x:
            size += len(j)
    return size

# This function is the main function that will apply the butterworth filter to the dataset that we will be using.
# This fucntion will take the main 3D list as its input and will output a new list of the same size as its output.
# NOTE That the new list will be a filtered at 8hz, lowpass, and at first order.


def filterData(mainList):
    # fs = findSizeofData(mainList)  # Sampling frequency
    # fc = 8  # Cut-off frequency of the filter
    # w = fc / (fs / 2) # Normalize the frequency
    # newMainList = []
    # b, a = signal.butter(1, .008, 'low') #Apply a low pass, first order butterworth filter at 8hz to the 3-D dataset.
    # for x in mainList:
    #     sublist = []
    #     for j in x:
    #         if x != None:
    #             subList.append(list(signal.filtfilt(b, a, j, padlen=7)))
    #             print(list(signal.filtfilt(b, a, j, padlen=5)))
    #     newMainList.append(list(subList))
    #     sublist.clear()
    # return newMainList
    newMainList = []
    # Apply a low pass, fourth order butterworth filter at 8hz to the 3-D dataset.
    b, a = signal.butter(4, 8/500, 'lowpass')
    index = 0
    for x in mainList:  # what is this doing? expected output?
        subList = []
        # for j in x:
        if x != None:
            # subList = list(signal.filtfilt(b, a, j, padlen=7))
            subList.append(list(signal.filtfilt(
                b, a,  groupCoPx(x), padlen=0)))
            subList.append(list(signal.filtfilt(
                b, a,  groupCoPy(x), padlen=0)))
            # print(list(signal.filtfilt(b, a, j, padlen=7)))
            # print(subList)

        newMainList.append(list(subList))
        # if index < 5:
        #     # print("Mainlist line", index, ":", x[index])
        #     # print("filter output copx:", list(signal.filtfilt(
        #     #     b, a,  groupCoPx(x), padlen=0)))
        #     # print("Filtered line:", subList[index])
        # index += 1
        # subList.clear()
    return newMainList

# This function will calculate the CopX and CopY values.
# This function will take MX, MY and FZ
# Returns Copx first and then Copy

# kikik 2 feet shoes.txt line 10309
# 01 timestamp(ms):90727.75 force plate (fx, fy, fz, mx, my, mz):0.01384163,-0.5768337,0,-0.1828613,2.003143,-0.03312254


def calcCop(mx, my, fz):
    _copX, _copY = 0, 0
    _copX = -my/fz
    _copY = mx/fz
    return _copX, _copY


def calculateDisplacement(CopA, CopB):
    return CopB - CopA

# def calculateVelocity(CopA, CopB, TimeA, TimeB):
#    return (CopB - CopA)/(TimeB - TimeA)


def calculateVelocity(Displacement, TimeA, TimeB):
    return Displacement/(TimeB - TimeA)


def calculatePathlength(displacementXA, displacementYA):
    return (math.sqrt(pow(displacementXA, 2) + pow(displacementYA, 2)))

# make arrays for each filtered value?


def groupCoPx(mainList):
    copXlist = []
    for x in range(len(mainList)):
        copXlist.append(mainList[x][6])
        # copXlist.append(x[6])
    return copXlist


def groupCoPy(mainList):
    copYlist = []
    for y in range(len(mainList)):
        copYlist.append(mainList[y][7])
        # copXlist.append(x[6])
    return copYlist


# This is the main function that will calculate all the extra values will need for each block of values.
# param: dX, dY = list for displacementX, displacementY vX,vY: lists for velocityX, velocityY
# pL = list for pathLength, lineOfValues = filteredValues[i]
# lastValue is the last lineOfValues from previous run, if there was not a previous run, default is empty
def calculateValues(dX, dY, vX, vY, pL, lineOfValues, timeValues, lastValues=[]):
    # NOTE: lastValues = [copx, copy, timeValue]
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
    newFileName = current_file.replace('.txt', '_CalculatedFile.xls')
    # Open each file.
    f = open(current_file, "r")
    # Read from the file line by line.
    f1 = f.readlines()
    mainList = []  # We will be doing all of our calculations on this list.
    timeList = []  # We will hold all the times on here.
    timeSubList = []
    subList = []
    maxApCopX, maxMLCopY = 0, 0
    # Go throught each of the lines and using the Regex below to parse each string.
    lineIndex = 0
    # print("Check f1:")
    # for i in range(15):
    #     print(f1[i])
    for line in f1:
        res = re.findall(r"[-+]?\d*\.\d+|\d+", line)
        # Convert each number in from our regular expression from a string back into a float.
        for index in range(len(res)):
            # Convert the regex from string back into a float number so we can work with it.
            res[index] = float(res[index])
        # Currently we only want lines that have 1.0 in the title.
        if len(res) != 0 and res[0] == 1.0:

            lineIndex += 1
            # Append res to our subList.
            res.pop(0)  # gets number before timestamp
            timestamp = res.pop(0)  # gets timestanp
            # res[0] goes from number to timestamp to fx
            timeSubList.append(timestamp)
            # Calculate COPX and COPY before hand and place it in the subList.

            copx, copy = calcCop(res[3], res[4], res[2])
            # showing correct copx and copy here
            # if (lineIndex in range(5)):
            #     print(res)
            #     print("copx =", copx, "copy = ", copy)

            # if copx > 3.022 and copx < 3.0227:
            #     print(" copx: " + str(copx))

            maxApCopX = max(maxApCopX, copx)
            maxMLCopY = max(maxMLCopY, copy)
            res.append(copx)  # COPX at position [6], -My/Fz
            res.append(copy)  # COPY at position [7], Mx/Fz
            subList.append(res)
        # When we are finally see a 2.0 when can put everything we just put into subList to our mainList.
        elif len(res) != 0 and res[0] == 2.0:
            if len(subList) != 0:
                # Putting a copy of it in mainList so when we clear it we don't delete the list.
                mainList.append(list(subList))
                timeList.append(list(timeSubList))
                timeSubList.clear()
                subList.clear()

    f.close()
    # print("Check append for mainlist on first 5 entries:")
    # for i in range(5):
    #     print(mainList[0][i])
    # print("Check append for timelist on first 5 entries:")
    # for i in range(5):
    #     print(timeList[0][i])

    displacementX = []
    displacementY = []
    velocityX = []
    velocityY = []
    pathLength = []
    maxVelocityX, maxVelocityY = 0, 0
    minVelocityX, minVelocityY = 0, 0
    meanVelocityX, meanVelocityY = 0, 0
    filteredList = filterData(mainList)

    index = 0
    lastValues = []
    for stage in filteredList:
        displacementX, displacementY, velocityX, velocityY, pathLength, lastValues = calculateValues(
            displacementX, displacementY, velocityX, velocityY, pathLength, stage, timeList[index], lastValues)
        maxVelocityX = max(velocityX)
        maxVelocityY = max(velocityY)
        meanVelocityX = statistics.mean(velocityX)
        meanVelocityY = statistics.mean(velocityY)
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
    sheet1.write(0, 5, "Velocity")
    rowX = 0
    for j in range(len(filteredList)):
        print("timelist length: ", len(timeList[j]))
        for i in range(len(timeList[j])):
            # if rowX == 0:
            #     sheet1.write(rowX+1, 0, str(timeList[j][i]))
            #     sheet1.write(rowX+1, 1, str(round(filteredList[j][0][i], 4)))
            #     sheet1.write(rowX+1, 2, str(mainList[j][i][6]))
            # else:
            sheet1.write(rowX+1, 0, str(timeList[j][i]))
            sheet1.write(rowX+1, 1, str(round(filteredList[j][0][i], 4)))
            sheet1.write(rowX+1, 2, str(mainList[j][i][6]))
            sheet1.write(rowX+1, 3, str(round(displacementX[rowX], 4)))
            sheet1.write(
                rowX+1, 4, str(round(asbDisplacementX[rowX], 4)))
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
    sheet2.write(0, 5, "Velocity")
    rowY = 0
    for j in range(len(filteredList)):
        for i in range(len(timeList[j])):
            # if rowY == 0:
            #     sheet2.write(rowY+1, 0, str(timeList[j][i]))
            #     sheet2.write(rowY+1, 1, str(round(filteredList[j][1][i], 4)))
            #     sheet2.write(rowY+1, 2, str(mainList[j][i][7]))
            # else:
            sheet2.write(rowY+1, 0, str(timeList[j][i]))
            sheet2.write(rowY+1, 1, str(round(filteredList[j][1][i], 4)))
            sheet2.write(rowY+1, 2, str(mainList[j][i][7]))
            sheet2.write(rowY+1, 3, str(round(displacementY[rowY], 4)))
            sheet2.write(
                rowY+1, 4, str(round(asbDisplacementY[rowY], 4)))
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


# idk what to do with path
    sheet3 = wb.add_sheet('Path')
    sheet3.write(0, 0, "Time")
    sheet3.write(0, 1, "Path")

    for i in range(len(timeList[0])):
        sheet3.write(i+1, 0, str(timeList[0][i]))
        sheet3.write(i+1, 1, str(round(pathLength[i-1], 4)))

    wb.save(completeName)


'''
JUST AS NOTES FOR NOW:
STEP 1):
break the data up into x,y,z,mx,my,mz,copx,copy DONE
STEP 2):
Filter the data DONE 
STEP 3):
Find Max AP (Copx) and Max ML (Copy) per stage
Max Velocity Copx and Max Velocity Copy 
Displacement of X Velocity of X, Displacement of Y Velocity of Y 
Get the MAX and MEAN for each   
STEP 4):
FIND path length between time 2 and time 1
STEP 5):
output might look like this?
CoPx
Time    CoPx    Distance (d)  Abs Distance    Velocity
t1      -          -            -               -
t2      Copx1   t2 - t1       Abs(d1)         d1/(t2-t1)
.
.
.

Max Range = Max of Abs distance column
Mean Range = Mean of abs distance column

Peak Velocity = Max of Velocity column
Mean Velocity = Mean of Velocity column

*repeat these calculations for CoPY
~Calculate path length
#repeat all calculations for both AP and ML

'''
'''
NOTE on how to create files in another direcotry:
# Creating the directory that we will be putting the new files into. 
# Directory 
directory = "Calculation Files"
filename = "testy.txt"
# Parent Directory path 
parent_dir = os.getcwd()

# Path 
path = os.path.join(parent_dir, directory)

# Create the directory 
# 'Calculation Files' in 
# '/home / User / Documents' 
#print(os.path.isdir(path))
if os.path.isdir(path) == False:
    os.mkdir(path) 
    print("Directory '% s' created" % directory) 

completeName = os.path.join(path, filename)
file1 = open(completeName, "w")
file1.close()
'''
