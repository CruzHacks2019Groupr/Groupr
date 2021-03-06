import networkx as nx
import itertools
from .dbHandler import UserHandler, EventHandler, GroupHandler

def findPerfectGroup(Event, User):
	User = UserHandler(User)
	PerfectGroups = nx.cliques_containing_node(Event.G(), User.id)
	for i in PerfectGroups:
		print(i)
		if len(i) is Event.groupSize:
			for j in i:
				Event._removeUserFromGraph(j)
			return GroupHandler.createGroup(i, Event)
	return None

def forceGroups(Event):
	possibleGroups = list(itertools.combinations(list(Event.DG()), Event.groupSize))    		#All combinations of the Node list in groups of length n are stored in list
	dg = Event.DG()
	print(possibleGroups)
	i = 0
	groupCombo = [list(list())]	
	scoreList = []										  										#Nested loops build a combination of groups (disjoint is used to make sure the same person doesnt end up in a group twice)
	while i < len(possibleGroups) and not set(possibleGroups[0]).isdisjoint(possibleGroups[i]):
		print(i)
		groupCombo.append([])
		groupCombo[i].append(possibleGroups[i])                         						#Add first group
		scoreList.append(computeScore(dg, possibleGroups[i]))           						#Add score of first group
		j = i + 1
		while j < len(possibleGroups):
			for k in groupCombo[i]:                                        						#Checks if any shared members in current running groupCombo
				if not set(k).isdisjoint(possibleGroups[j]):
					break												   						#Breaks if shared members
				groupCombo[i].append(possibleGroups[j])                    						#If there is no break then group is added to combo
				scoreList[i] += computeScore(dg, possibleGroups[j])            				#Score is added as well
			j+=1
		i+=1

	BestIndex = 0
	for k in range(len(scoreList)):											   			#Finds best group combo (highest score)
		if scoreList[k] > scoreList[BestIndex]:
			BestIndex = k

	groupList = []
	for k in groupCombo[BestIndex]:
		groupList.append(GroupHandler.createGroup(k, Event))
		for l in k:
			Event._removeUserFromGraph(l)

	groupList.append(GroupHandler.createGroup(list(Event.DG()), Event))
	print(groupList)
	return groupList

def computeScore(DG, L):													   				#For a given group computes the score, which is the number edges
	score = 0
	for i in L:
		for j in L:
			if i != j and i in DG.neighbors(j):
				score+=1;
	return score