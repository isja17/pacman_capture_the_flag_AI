# baselineTeam.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from captureAgents import CaptureAgent
from operator import itemgetter
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)
    self.team = self.getTeam(gameState) #agent indexes
    self.foodCarrying = 0
    self.depth = 50 #max depth
    self.numAgents = 4 #hard coded
    self.prevStates = []
    self.foodGoingTo = None

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
        return successor.generateSuccessor(self.index, action)
    else:
        return successor


  def getWeights(self, gameState):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def evaluationFunction(self, gameState):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState)
    weights = self.getWeights(gameState)
    return features * weights

  def chooseAction(self, gameState):
    """
    Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"

    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    foodBools = self.getFood(gameState)
    foodGrid = foodBools.asList()

    # if you are defending (respawn, or get back to your side), reset food carrying
    if not myState.isPacman:
      self.foodCarrying = 0

    if self.foodCarrying >= 5: # don't get too greedy, need to go back and return it
      bestDist = 9999
      for action in gameState.getLegalActions(self.index):
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction


    STARTING_DEPTH = 0
    MINIMAL_VALUE = -99999999
    MAXIMAL_VALUE = 99999999
    # Number of agents, including Pacman and all the ghosts
    numAgents = gameState.getNumAgents()
    ##set up a & b##
    a = MINIMAL_VALUE
    b = MAXIMAL_VALUE

    ### this was a previous attempt at making the original iterable a thing###
    def maximize(numiterable):
        v = MINIMAL_VALUE
        for num in numiterable:
            if num > v:
                v = num
            if v > self.b:
                return v
            if v > self.a:
                self.a = v
        return v


    def minimize(numiterable):
        v = MAXIMAL_VALUE
        for num in numiterable:
            if num < v:
                v = num
            if v < self.a:
                return v
            if v < self.b:
                self.b = v
        return v

    def maxLayer(gameState, depth, agentIndex, a, b):
        #only takes in team agents
        if len(gameState.getLegalActions(agentIndex)) == 0 or depth >= self.depth:
            return self.evaluationFunction(gameState)


        newA = a
        v = MINIMAL_VALUE
        for newAction in gameState.getLegalActions(agentIndex):
            num = miniLayer(gameState.generateSuccessor(agentIndex, newAction), depth, agentIndex+1, newA, b)
            if num > v:
                v = num
            if v > b:
                return v
            if v > a:
                newA = v
        return v

        # Pacman's turn, so maximize
       # maxVal = maximize(miniLayer(gameState.generateSuccessor(PACMAN_AGENT_INDEX, newAction), depth, FIRST_GHOST_INDEX) for newAction in gameState.getLegalActions(0))
        #return maxVal


    def miniLayer(gameState, depth, agent, a, b):
        if depth == 0 or depth >= self.depth or agent in self.team:
            return self.evaluationFunction(gameState)

        succAgent = (agent + 1) % self.numAgents  # Move to the next agent from the successor state
        if succAgent in self.team:
            # If true, that means we are at our last ghost at this depth and we are about to
            # recurse into one of the team layers or reach the terminals, so increment tree depth before
            # recursing out of the last ghost layer at this depth
            newDepth = depth + 1
            newB = b
            v = MAXIMAL_VALUE

            for newAction in gameState.getLegalActions(agent):
                num = maxLayer(gameState.generateSuccessor(agent, newAction), newDepth, succAgent, a, newB)
                if num < v:
                    v = num
                if v < a:
                    return v
                if v < b:
                    newB = v
            return v
            minVal = minimize(maxLayer(gameState.generateSuccessor(agent, newAction), newDepth) for newAction in gameState.getLegalActions(agent))

        else:
            # Recurse into yet another min layer from the current min layer (multiple ghosts)
            newB = b
            v = MAXIMAL_VALUE
            for newAction in gameState.getLegalActions(agent):
                num = miniLayer(gameState.generateSuccessor(agent, newAction), depth, succAgent, a, newB)
                if num < v:
                    v = num
                if v < a:
                    return v
                if v < b:
                    newB = v
            return v

        minVal = minimize(miniLayer(gameState.generateSuccessor(agent, newAction), depth, succAgent) for newAction in gameState.getLegalActions(agent))
        return minVal

    # Creation of the tree's original node
    maxScore = MINIMAL_VALUE
    # Traversing through available legal actions' minimax trees to find the best scoring one
    a = MINIMAL_VALUE
    b = MAXIMAL_VALUE
    v = MINIMAL_VALUE
    for actionTraversal in gameState.getLegalActions(self.index):
        # Root node max layer is this for loop's max comparison performed on the 1st min layer
        # therefore recurse into miniLayer, not the maxLayer:
        score = miniLayer(gameState.generateSuccessor(self.index, actionTraversal), STARTING_DEPTH, self.index+1, a, b)
        if score > v:
            v = score
            action = actionTraversal
        if v > b:
            return action
        if v > a:
            a = v

    foodLeft = len(self.getFood(gameState).asList())

    actions = gameState.getLegalActions(self.index)
    for poss in actions:
        successor = self.getSuccessor(gameState, poss)
        successorFoodLeft = len(self.getFood(successor).asList())
        if successorFoodLeft < foodLeft: # if our action has led us to eating food
            action = poss
            break


    if self.foodGoingTo != None:
        if self.getMazeDistance(myPos,self.foodGoingTo) <= 1:
            foodDefendingBools = self.getFoodYouAreDefending(gameState)
            foodGrid = foodDefendingBools.asList()
            self.foodGoingTo = random.choice(foodGrid)

    successor = self.getSuccessor(gameState, action)
    successorFoodLeft = len(self.getFood(successor).asList())
    if successorFoodLeft < foodLeft:
      self.foodCarrying += 1
    self.prevStates.append(action)
    if len(self.prevStates) >= 10:
        self.prevStates.pop()
    return action

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  An offensive reflex agent which prioritizes going into the enemies half of the
  board to eat up to five pieces of food, while making sure it does not get eaten.
  """
  def evaluationFunction(self, gameState):
    score = self.getScore(gameState)

    myState = gameState.getAgentState(self.index)
    myPos = myState.getPosition()
    foodBools = self.getFood(gameState)
    foodGrid = foodBools.asList()

    #better score for attacking

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    dangers = [a for a in enemies if not a.isPacman and a.getPosition() != None]

    if len(dangers) > 0:
     #better score for attacking
      if myState.isPacman: score -= 50

      minDist = 999999
      for enemy in dangers:
        dist = self.getMazeDistance(myPos, enemy.getPosition())
        if dist < minDist:
          minDist = dist
          closestEnemy = enemy

      if not (minDist >= 999999):
        score += minDist
        #if we will get eaten
        if minDist == 1:
          score -= 1000
        if minDist == 0: #got eaten
          score -= 200

    else: #go to nearest food
      if not myState.isPacman: score -= 50
      md = []  # maze distance storage

      if len(foodGrid) != 0:
          for food in foodGrid:
              md.append(self.getMazeDistance(myPos, food))

          if len(md) > 0:
              score -= min(md)
              if min(md) == 0 :
                  score += 1000
    return score


class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    This is a defensive reflex agent. Prioritizes patroling our side of the board
    untill an enemy is seen, then it prioritizes eating the enemy.
    """
    def evaluationFunction(self, gameState):
        """
        +100 points for not being pacman
        -min-dist-invading-enemy (so lower distances have > scores)
        +1000 for eating an invading enemy
        """
        score = self.getScore(gameState)
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()
        foodDefendingBools = self.getFoodYouAreDefending(gameState)
        foodGrid = foodDefendingBools.asList()


         #better score for defending
        if not myState.isPacman: score += 100

        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

        if len(invaders) > 0:
            minDist = 999999
            for enemy in invaders:
                dist = self.getMazeDistance(myPos, enemy.getPosition())
                if dist < minDist:
                    minDist = dist
                    closestEnemy = enemy

            if not (minDist == 999999):
                score -= minDist*2

            if minDist == 0: #eat enemy
                score += 1000

        else: #if no one is seen invading, move around
            if self.foodGoingTo == None:
                self.foodGoingTo = random.choice(foodGrid)

            score -= self.getMazeDistance(myPos,self.foodGoingTo)
            #score -= max(md)

            if myPos in self.prevStates[0:9]:
                if myPos == self.prevStates[-1] or self.prevStates[-2]:
                    score -= 100000000
                else: score -= 10

            else:
                score += 10
                self.prevStates.append(myPos)
                if len(self.prevStates) > 10:
                    self.prevStates.pop()
            #if maxDistFoodDefending = -999999999:
        return score
