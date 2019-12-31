from captureAgents import CaptureAgent
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
  print [eval(first)(firstIndex), eval(second)(secondIndex)]
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        self.foodCarrying = 0
        self.initActions = self.aStarFromJail(self.state, )

    def inStartState(self, gameState):
        return gameState.getAgentPosition(self.index) == self.start

    def distToClosestFoodDefending(self, gameState):
        foodList = self.getFoodYouAreDefending(gameState).asList()
        pos = gameState.getAgentPosition(self.index)

        opt = 999999999999999999999999999
        for food in foodList:
            dist = util.manhattanDistance(pos, food)
            if dist < opt:
                opt = dist
        return opt

    def closestFoodToEat(self, gameState):
        """
        returns (dist, (x,y))
        """
        foodList = self.getFood(gameState).asList()
        pos = gameState.getAgentPosition(self.index)

        optDist = 999999999999999999999999999
        for food in foodList:
            dist = util.manhattanDistance(pos, food)
            if dist < optDist:
                optDist = dist
                best = food
        return optDist, best


    def aStarFromJail(self, gameState):
        """
        If we are in start position or in jail, then we want to find the
        optimal route out of jail.
        """
        pos = gameState.getAgentPosition(self.index)

        node = (pos, [])
        frontier = util.PriorityQueue()
        frontier.push(node, 0)
        explored = []

        while not frontier.isEmpty():
            currentNode, action = frontier.pop()

            if currentNode == closestFoodDefending[1]: return toDo #if current state is a goal state, return list of actions

            if currentNode not in explored:
                explored.append(currentNode)
                successors = CaptureAgent().generateSuccessor(currentNode, action)

                for succState, action, cost in successors: #succState = ((x,y), [])

                    if succState not in explored:
                        newAction = toDo + [action]
                        estCost = self.getScore(succState) + distToClosestFoodDefending(succState)[0]
                        frontier.push((succState, newAction), estCost)


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

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}


    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        min = float("-inf")
        max = float("inf")
        return self.maximize(gameState, 1, 0, min, max)

    def maximize(self, gameState, depth, agentIndex, alpha, beta):
        # Define maxVal and legal actions
        maxVal = float("-inf")
        actions = gameState.getLegalActions(agentIndex)
        # run loop if terminal conditions not met
        while not (gameState.isWin() or gameState.isLose() or depth == 0):
            for action in actions:
                # get successor
                successor = gameState.generateSuccessor(0, action)
                if (successor != None):
                    # check conditions
                    if self.minimize(successor, depth, 1, alpha, beta) > beta:
                        # if minimize is greater than beta val, call minimize
                        return self.minimize(successor, depth, 1, alpha, beta)

                    elif self.minimize(successor, depth, 1, alpha, beta) > maxVal:
                        # if minimize is greater than maxVal, set val and action
                        maxVal = self.minimize(
                            successor, depth, 1, alpha, beta)
                        maxAction = action
                # change alpha val if needed
                alpha = max(alpha, maxVal)
            if depth > 1:
                return maxVal
            else:
                return maxAction
        else:
            # terminal condition met, return evalFunc
            return self.evaluationFunction(gameState)

    def minimize(self, gameState, depth, agentIndex, alpha, beta):
        # set minVal, agents, and legal actions
        minVal = float("inf")
        agents = gameState.getNumAgents() - 1
        actions = gameState.getLegalActions(agentIndex)
        # run loop if terminal condition not met
        while not (gameState.isWin() or gameState.isLose() or depth == 0):
            for action in actions:
                # get successor
                successor = gameState.generateSuccessor(agentIndex, action)
                if (successor != None):
                    # check conditions
                    if agentIndex > agents:
                        # set val to value returned by minimize
                        val = self.minimize(
                            successor, depth, agentIndex + 1, alpha, beta)
                    elif agentIndex < agents:
                        val = self.minimize(
                            successor, depth, agentIndex + 1, alpha, beta)
                    else:
                        if depth < self.depth:
                            # set val to value returned by maximize
                            val = self.maximize(
                                successor, depth + 1, 0, alpha, beta)
                        else:
                            # val set to evalFunc
                            val = self.evaluationFunction(successor)
                # check val against alpha and minVal
                if val < alpha:
                    return val
                elif val < minVal:
                    minVal = val
                # change beta val if needed
                beta = min(beta, minVal)
            return minVal
        else:
            # terminal condition met, return evalFunc
            return self.evaluationFunction(gameState)

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)#self.getScore(successor)
        lastPos = gameState.getAgentState(self.index).getPosition()
        enemyCapsules = self.getCapsules(successor)
        # Compute distance to the nearest food
        myPos = successor.getAgentState(self.index).getPosition()

        if len(foodList) > 0: # This should always be True,  but better safe than sorry
          minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
          features['distanceToFood'] = minDistance
          if minDistance == 0:
              features['distanceToFood'] -= 10000

        if len(enemyCapsules) > 0:
            minCapsule = min([self.getMazeDistance(myPos, cap) for cap in enemyCapsules])
            features['capsuleDistance'] = minCapsule
    # Check if enemies are nearby
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemiesNearby = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        #distance to home
        myState = successor.getAgentState(self.index)

        features['numEnemiesNearby'] = len(enemiesNearby)
        features['onOffense'] = 0
        if myState.isPacman: features['onOffense'] = 1

        if myPos == lastPos:
            features['samePos'] = 1

        if len(enemiesNearby) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in enemiesNearby]
            if features['onOffense'] == 0:
                features['nearestEnemyDistanceDefense'] = min(dists)
                features['eatEnemy'] = 1
            else: # if on offense
                features['nearestEnemyDistanceOffense'] = min(dists)
                if features['nearestEnemyDistanceOffense'] <= 2:
                    features['nearestEnemyDistanceOffense'] -= 10000
                features['eatEnemy'] = 0

        if self.foodCarrying <= 5 or features['nearestEnemyDistanceDefense'] <= 2 or not myState.isPacman: #if we are defending or have to collect more, don't need to go home
          features['distanceToHome'] = 0
        else:
          features['distanceToHome'] = self.getMazeDistance(self.start, myPos)

        for enemy in enemiesNearby:
            if enemy.scaredTimer > 0:
                features['scaredEnemy'] = 1
                features['distToScared'] = self.getMazeDistance(myPos, enemy.getPosition())
                if features['distToScared'] <= 3:
                    features['eatEnemy'] = 1
                    if features['distToScared'] == 0:
                        features['eatEnemy'] = 2
            else:
                features['scaredEnemy'] = 0
                features['distToScared'] = 0
                features['eatEnemy'] = 0

        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        features['reverse'] = 0
        if action == rev: features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 75, 'distanceToFood': -1, 'distanceToHome': -2,
        'numEnemiesNearby': -100, 'nearestEnemyDistanceOffense' : 100, 'nearestEnemyDistanceDefense': -10,
        'onOffense': 10, 'scaredEnemy': 50, 'distToScared': -2, 'samePos': -1000, 'reverse': -10,
        'capsuleDistance': -50, 'eatEnemy': 100}

    class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        foodDefendingBools = self.getFoodYouAreDefending(gameState)
        foodDefendingGrid = foodDefendingBools.asList()


        # Computes whether we're on defense (1) or offense (0)
        features['onDefense'] = 1
        if myState.isPacman: features['onDefense'] = 0

        # Computes distance to invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          features['invaderDistance'] = min(dists)
          if features['invaderDistance'] == 0:
              features['eatEnemy'] = 1

          for food in range(len(foodDefendingGrid)):
              features['minDistFoodDefending'] = 999999999
              if foodDefendingBools[food] == 'T':
                  dist = self.getMazeDistance(myPos, food)
                  if dist < features['maxDistFoodDefending']:
                      features['maxDistFoodDefending'] = dist
        else:
            #finds minimum distance food defending so we can look at areas not around us
            for food in range(len(foodDefendingGrid)):
                features['maxDistFoodDefending'] = 999999999
                if foodDefendingBools[food] == 'T':
                    dist = self.getMazeDistance(myPos, food)
                    if dist > features['maxDistFoodDefending']:
                        features['maxDistFoodDefending'] = dist
            if features['maxDistFoodDefending'] == 999999999:
                features['maxDistFoodDefending'] = 10000

        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1


        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1, 'onDefense': 10, 'invaderDistance': -10, 'stop': -100, 'reverse': -1,
        'minDistFoodDefending': -2, 'maxDistFoodDefending': -1, 'eatEnemy': 1000000}
