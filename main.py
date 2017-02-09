#Author: Michael Disyak
# Implements a behaviour policy and a uses a general value function (GVF) to make predictions about various signals

from lib_robotis_hack import *
import myLib as myLib
import newPlotter as plotter
import threading
import random
random.seed(0)
import GVF
import RLtoolkit.tiles as tile
import numpy as np
import copy

D = USB2Dynamixel_Device(dev_name="/dev/tty.usbserial-AI03QEMU",baudrate=1000000)
s_list = find_servos(D)
s1 = Robotis_Servo(D,s_list[0])
s2 = Robotis_Servo(D,s_list[1])


gamma = 0.9
lamb = 0.9
numTilings = 8
alpha = 0.1/numTilings
beta = alpha/10
numTiles = 8
numTilesTotal = numTiles*numTiles*numTilings
numberOfLearningSteps = 0
pastAngle = 0.0

gvf = GVF.GenValFunc(numTilings, numTiles, numTilesTotal, gamma, lamb, alpha) #numtilings, numtiles, gamma, lambda, alpha
myPlotter = plotter.newPlotter(gvf)
myPlotter.s1 = s1
myPlotter.s2 = s2


def getState():
    # Return state values scaled to unit length and then scaled into number of tiles

    currentLoad = myLib.normalizeLoad(s1.read_load())
    print 'load is: ' + str(currentLoad)
    currentAngle = myLib.normalizeAngle(s1.read_angle())
    obs = [currentAngle * numTiles,  currentLoad * numTiles]#myLib.normalizeLoad(float(s1.read_load()))*numTiles]  # , s2.read_encoder()/853/.1, s2.read_load()/1023/.1]
    nextStateSparse = tile.tiles(numTilings, numTilesTotal, obs)  # tileIndices
    nextState = np.zeros(numTilesTotal)
    for index in nextStateSparse:  # Convert to full vector of 0s and 1s
        nextState[index] = 1
  #  nextState = np.append(nextState, 1)#bias bit
    return nextState

def controlFunctionOnpolicy(args, realTimeStop):
    #STEP 1 sendAction()
    global left
    pastAngle = s1.read_angle()
    myPlotter.initPlotter()
    currentState = getState()
    gvf.currentState = currentState
    gvf.gammaCurrent = gamma
    timeEnd = time.time() + 60 * 20#mins
    left = False
    numberOfActions = 0
    while (time.time() < timeEnd):
        startTime= time.time()
        currentPosRad = s1.read_angle()
        myPlotter.currentAngle = myLib.radToDeg(currentPosRad)
        myPlotter.currentLoad = s1.read_load()
     #   myPlotter.currentLoad = myLib.normalizeLoad(s1.read_load())
        currentPos = myLib.radToDeg(currentPosRad)
        if left:
            s1.move_angle(myLib.degToRad(currentPos + 20))
            if currentPos >= 80:
                left = False
        else:
            s1.move_angle(myLib.degToRad(currentPos - 20))
            if currentPos <= -80:
                left = True
    #STEP 2 obs = readStates
        nextState = getState() #This should be getState()

        cumulant = s1.read_load()#myLib.normalizeLoad(s1.read_load())#myLib.radToDeg(s1.read_angle())

       # print('currentState is: ' + str(np.dot(1, currentState)))
       # print('nextState is: ' + str(np.dot(1, nextState)))

        #MAYBE STEP gvf.update(nextState, currentState, cumulant, gamma, maybe row for GTD) - Update values for GVF
        gvf.update(nextState, currentState, cumulant, gamma)

        #STEP 3 learn stuff
        gvf.learn()

        currentState = copy.deepcopy(nextState)

        myPlotter.controlTime = round(time.time()-startTime,3)
        numberOfActions += 1
        myPlotter.numberOfActions = numberOfActions
        myPlotter.plot()

    realTimeStop.set()

def controlFunctionOnpolicyConditionalGamma(args, realTimeStop): #How long does it take for me to reach 90 degress or higher?
    #STEP 1 sendAction()
    myPlotter.initPlotter()
    currentState = getState()
    gvf.currentState = currentState
    gvf.gammaCurrent = 1
    timeEnd = time.time() + 60 * 30#mins
    left = False
    numberOfActions = 0
    while (time.time() < timeEnd):
        startTime= time.time()
        currentPosRad = s1.read_angle()
        myPlotter.currentAngle = currentPosRad
        myPlotter.currentLoad = s1.read_load()
        currentPos = myLib.radToDeg(currentPosRad)
        if left:
            s1.move_angle(myLib.degToRad(currentPos + 20))
            if currentPos >= 80:
             left = False
        else:
            s1.move_angle(myLib.degToRad(currentPos - 20))
            if currentPos <= -80:
                left = True

    #STEP 2 obs = readStates
       # print('current angle :' + )
        nextState = getState()
        if myLib.radToDeg(s1.read_angle()) >= 90:
            nextGamma = 0
        else:
            nextGamma = 1

        cumulant = 1

        #MAYBE STEP gvf.update(nextState, currentState, cumulant, gamma, maybe row for GTD) - Update values for GVF
        gvf.update(nextState, currentState, cumulant, nextGamma)
        #STEP 3 learn stuff
        gvf.learn()

        currentState = copy.deepcopy(nextState)

        numberOfActions += 1
        myPlotter.numberOfActions = numberOfActions
        myPlotter.controlTime = round(time.time()-startTime,3)
        myPlotter.plot()

    realTimeStop.set()


def controlFunctionOffpolicy(args, realTimeStop): #How long does it take for me to reach 99 degress or higher while moving right?
    #STEP 1 sendAction()
    myPlotter.initPlotter()
    currentState = getState()
    gvf.currentState = currentState
    gvf.gammaCurrent = gamma
    timeEnd = time.time() + 60 * 10#mins
    left = False
    numberOfActions = 0
    while (time.time() < timeEnd):
        startTime= time.time()
        currentPosRad = s1.read_angle()
        myPlotter.currentAngle = currentPosRad
        currentPos = myLib.radToDeg(currentPosRad)
        if left:#moving right
            s1.move_angle(myLib.degToRad(currentPos + 20))
            row = 1
            if currentPos >= 80:
             left = False
        else:#moving left
            row = 0
            s1.move_angle(myLib.degToRad(currentPos - 20))
            if currentPos <= -80:
                left = True

    #STEP 2 obs = readStates
       # print('current angle :' + )
        nextState = getState()

        cumulant = 1

        #MAYBE STEP gvf.update(nextState, currentState, cumulant, gamma, maybe row for GTD) - Update values for GVF
        gvf.update(nextState, currentState, cumulant, gamma, row)
        #STEP 3 learn stuff
        gvf.learnGTD()

        currentState = copy.deepcopy(nextState)

        numberOfActions += 1
        myPlotter.numberOfActions = numberOfActions
        myPlotter.controlTime = round(time.time()-startTime,3)
        myPlotter.plot()

    realTimeStop.set()


def testControl(self, realTimeStop):
    myPlotter.initPlotter()
    currentState = 1
    gvf.currentState = currentState
    gvf.gammaCurrent = gamma
    timeEnd = time.time() + 60 * 10#mins

    numberOfActions = 0
    while (time.time() < timeEnd):
        startTime = time.time()
        if currentState == 0:
            nextState = 1
            cumulant = 1
        else:
            nextState = 0
            cumulant = 1
        gvf.update(nextState, currentState, cumulant, gamma)
        gvf.learn()
        currentState = nextState#copy.deepcopy(nextState)
        numberOfActions += 1
        myPlotter.numberOfActions = numberOfActions
        myPlotter.controlTime = round(time.time()-startTime,3)
        myPlotter.plot()

    realTimeStop.set()


realTimeStop = threading.Event()
args = None
controlFunctionOffpolicy(args, realTimeStop)
myPlotter.saveFigure('GVF1_alpha_' + str(myPlotter.gvf.alpha) + '_tilings_' + str(myPlotter.gvf.numTilings) + '_gamma_' + str(
    gamma) + '_lambda_' + str(myPlotter.gvf.lamb) + '.png')

#threading.Thread(target=controlFunctionOnpolicyConditionalGamma, args=(1, realTimeStop)).start()
#threading.Thread(target=gvf.learn, args=(1, realTimeStop)).start()
#myPlotter.plotGVF(realTimeStop)
#controlFunction(None, realTimeStop)
