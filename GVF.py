import numpy as np
import time
import math
class GenValFunc:


    prediction = 0.0
    cumulant = 0.0
    delta = 0.0
    postPrediction = 0.0
    postReturn = 0.0
    timeDiff = 0
    numTilings = 0
    gammaNext = 0
    gammaCurrent = 0
    lamb = 0
    row = 0
    numberOfLearningSteps = 0
    averageError = 0.0


    def __init__(self, numTilings, numTiles, numTilesTotal, gamma = 0.9, lamb = 0.9, alpha = 0.1, beta = 0.01):

        self.gammaCurrent = gamma
        self.lamb = lamb
        self.numTilings = numTilings
        self.numTilesTotal = numTilesTotal
        self.currentState = np.zeros(self.numTilesTotal)
        self.nextState = np.zeros(self.numTilesTotal)
        self.weightVect = np.zeros(self.numTilesTotal)
        self.hWeightVect = np.zeros(self.numTilesTotal)
      #  self.tCoder = tileCoder.TileCoder(4, 11, 11, [169, 853], [-1023, 1023])
        self.alpha = alpha
        self.beta = beta
        self.postTimeSteps = int(round(1.0/(1.0-self.gammaCurrent)))*5
        self.recordedCumulant = np.array([])
        self.recordedPrediction = np.array([])
        self.recordedGammas = np.array([])
        self.recordedError = np.array([])
        self.eligTrace = np.zeros(self.numTilesTotal)
      #  print(self.postTimeSteps)

    def update(self, nextState, currentState, cumulant, gamma, row = 1.0):
        self.nextState = nextState
        self.currentState = currentState
        self.cumulant = cumulant
        self.gammaNext = gamma
        self.row = row
    #    print('nextState is: ' + str(nextState))
    #    print('currentState is: ' + str(currentState))

    def learn(self): #args, stoppingEvent):
        startTime = time.time()
        #TD ERROR BELOW
        self.currentStateValue = np.dot(self.weightVect, self.currentState)
        self.nextStateValue = np.dot(self.weightVect, self.nextState)
        self.delta = self.cumulant + ((self.gammaNext * self.nextStateValue) - self.currentStateValue)

        self.eligTrace = (self.lamb * self.gammaCurrent * self.eligTrace) + self.currentState
        self.weightVect = self.weightVect + (self.alpha * self.delta * self.eligTrace)

        self.prediction = self.currentStateValue

       # print 'cumulannt: %s' % self.cumulant
        print 'currentStateValue %s' % self.currentStateValue
        print 'current gamma %s' % self.gammaCurrent
        print 'nextStateValue %s' % self.nextStateValue
        print 'next gamma %s' % self.gammaNext
      #  print 'elig trace %s' % self.eligTrace
       # print 'delta: %s' % self.delta
      #  print 'eligTrace %s' % self.eligTrace
      #  print 'weightVect %s' % self.weightVect



        self.verifier()
        self.numberOfLearningSteps += 1
        self.gammaCurrent = self.gammaNext
        self.timeDiff = round(time.time()-startTime,6)


    def learnGTD(self):
        startTime = time.time()
       #TD ERROR BELOW
        self.currentStateValue = np.dot(self.weightVect, self.currentState)
        self.nextStateValue = np.dot(self.weightVect, self.nextState)

        self.delta = self.cumulant + ((self.gammaNext * self.nextStateValue) - self.currentStateValue)
        self.eligTrace = self.row * (self.currentState + (self.lamb * self.gammaCurrent * self.eligTrace))
        self.weightVect += self.alpha * ((self.delta * self.eligTrace) - ((self.gammaNext * (1-self.lamb)) * np.dot(self.eligTrace, self.hWeightVect) * self.nextState))
        self.hWeightVect += self.beta * ((self.delta * self.eligTrace) - (np.dot(self.hWeightVect, self.currentState) * self.currentState))
        self.prediction = self.currentStateValue

        self.verifier()
        self.numberOfLearningSteps += 1
        self.gammaCurrent = self.gammaNext
        self.timeDiff = round(time.time()-startTime,6)


    def verifier(self):

        self.recordedPrediction = np.append(self.recordedPrediction, [self.prediction])
        self.recordedCumulant = np.append(self.recordedCumulant, [self.cumulant])
        self.recordedGammas = np.append(self.recordedGammas, [self.gammaCurrent])
   #     print ('recorded gamma = ' + str(self.recordedGammas))
    #    print ('current gamma = ' + str(self.gammaCurrent))
     #   print ('next gamma = ' + str(self.gammaNext))
      #  print ('current prediction' + str(self.prediction))
       # print ('recorded cumulant = ' + str(self.recordedCumulant))
        #print ('current cumulant = ' + str(self.cumulant))
       # print ('current cumulant = ' + str(self.cumulant))
        if np.size(self.recordedCumulant) == self.postTimeSteps + 1:
           # print ('recorded prediction = ' + str(self.recordedPrediction))
           # print ('recorded gamma = ' + str(self.recordedGammas))
           # print ('recorded cumulant = ' + str(self.recordedCumulant))

            currentPostPrediction = self.recordedPrediction[0]
            returnTotal = 0
            gammaTotal = 1
            self.recordedGammas[0] = 1

            for i in range(0,np.size(self.recordedCumulant)-1): #0 to length of your recorded cumulant

                currentCumulant = self.recordedCumulant[i]
                gammaTotal = gammaTotal * self.recordedGammas[i]
                returnTotal = returnTotal + (gammaTotal * currentCumulant)
            #print('return total: ' + str(returnTotal))

           # print ('return total = ' + str(returnTotal))
            self.postReturn = returnTotal
            self.postPrediction = currentPostPrediction
           # print('current prediction' + str(currentPostPrediction))
            self.recordedError = np.append(self.recordedError, returnTotal - currentPostPrediction)
            if np.size(self.recordedError) == self.postTimeSteps+1:
                self.recordedError = np.delete(self.recordedError, 0)
            self.averageError = np.sum(self.recordedError)/self.postTimeSteps
            self.recordedCumulant = np.delete(self.recordedCumulant, 0)
            self.recordedPrediction = np.delete(self.recordedPrediction, 0)
            self.recordedGammas = np.delete(self.recordedGammas, 0)







