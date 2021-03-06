from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import EventForm, ProfileForm

from django.http import QueryDict
from .functions.matcher import *
from .functions.reccomend import *
from .functions.groupFunctions import *
from .functions.dbHandler import EventHandler, UserHandler, GroupHandler
from .functions import dbTest
from .functions import dbHandler

import time

def testFunc1(request):
	#for production
	return

	print("testFunc1")
	start = time.time()
	dbTest.generateLukeTestCase(request.user.id)
	end = time.time()
	print("TIME DIFF: ", start - end)
	response_data = {}
	response_data['success'] = True
	return (JsonResponse(response_data))

def testFunc2(request):
	#for production
	return
	
	print("testFunc2")
	dbHandler.dropAllTables()

	response_data = {}
	response_data['success'] = True
	return (JsonResponse(response_data))


@login_required(login_url='/login/')
def event(request):
	if request.method == 'POST':
		form = EventForm(request.POST)
		if form.is_valid():
			e = form.save(commit=False)
			e.creator = request.user.id
			
			ev = EventHandler.createEvent(e.name, e.description, e.group_size, e.creator)

			print(ev)
	return redirect('index')

def updateProfile(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST, request.FILES)
		print(form)
		if form.is_valid():
			print("valid")
			user = UserHandler(request.user.id)
			p = form.cleaned_data
			print(p)
			user.setBio(p["bio"])
			user.setName(p["name"])
			user.setContactInfo(p["contactInfo"])
			if p["pic"] is not None:
				print("updating profile pic")
				print(p["pic"])
				user.profile.pic = form.cleaned_data['pic']
				user.profile.save()

	return redirect('index')
			

@login_required(login_url='/login/')
def addEvent(request):
	response_data = {}
	info = request.POST.dict()
	print(info)
	user = UserHandler(request.user.id)
	user.joinEvent(info.get('code'))
	return redirect('index')

#this is a helper function
def getGroup(event, user):
	user = UserHandler(user)
	group = user.getGroups(event)
	if group is not None:
		groupObj = {}
		groupObj['id'] = group.id
		groupObj['hash'] = group.hash
		groupObj['users'] = [getUserData(u, contactInfo=True) for u in group.getUsers()]
		return groupObj
	return None

@login_required(login_url='/login/')
def accept(request):

	response_data = {}
	info = request.GET.dict()

	event = EventHandler(info.get('eventID'))
	user = UserHandler(request.user.id)
	acceptedUser = reccomendNext(event, user)
	popUser(event, user)

	event.addEdge(user.id, acceptedUser)
	pG = findPerfectGroup(event, user)

	if(pG != None):
		response_data['group'] = getGroup(event,user)

	response_data['success'] = True
	return (JsonResponse(response_data))

@login_required(login_url='/login/')
def decline(request):
	
	response_data = {}
	info = request.GET.dict()

	popUser(info.get('eventID'), request.user.id)

	response_data['success'] = True
	return (JsonResponse(response_data))

#helper function
def getUserData(userId, event=None, contactInfo=False):
	user = UserHandler(userId)
	data = {}
	data["name"] = user.getName()
	data["id"] = user.id
	data["bio"] = user.profile.bio
	data["image"] = user.getPic().url
	if event is not None:
		event = EventHandler(event)
		#more here later
	if contactInfo:
		data["contactInfo"] = user.getContactInfo()
	return data


@login_required(login_url='/login/')
def loadData(request):
	response_data = {}
	response_data['success'] = True

	user = UserHandler(request.user.id)
	events = user.getEvents()
	json_events = []

	for e in events:
		temp = {}
		temp['id'] = e.id
		temp['name'] = e.name
		temp['isIn'] = True
		temp['addCode'] = e.addCode
		temp['description'] = e.description
		if(e.owner == user.id):
			temp['isOwner'] = True
		else:
			temp['isOwner'] = False
		g = getGroup(e, user)
		if g is not None:
			temp['group'] = g
		json_events.append(temp)

	my_events = user.getEventsOwner()
	for e in my_events:
		isIn = False
		for E in json_events:
			if(e.id == E.get('id') and user.id == e.owner):
				isIn = True
		if not isIn:	
			temp = {}
			temp[''] = e.id
			temp['name'] = e.name
			temp['addCode'] = e.addCode
			temp['isIn'] = False
			temp['isOwner'] = True
			temp['description'] = e.description
			json_events.append(temp)

	response_data['events'] = json_events
	response_data['userData'] = getUserData(user, contactInfo = True)
	return (JsonResponse(response_data))


def getNextMatch(request):
	print(request)
	
	response_data = {}
	info = request.GET.dict()

	suggestedUser = reccomendNext(info.get('eventID'), request.user.id)

	if(suggestedUser != None):
		response_data['suggested_usr'] = getUserData(suggestedUser)
	else:
		response_data['suggested_usr'] = {'id': -1, 'name': ''}
	
	response_data['success'] = True

	return (JsonResponse(response_data))


def forceGroups(request):
	print("forceGroups")
	response_data = {}
	info = request.GET.dict()

	event = EventHandler(info.get('eventID'))
	user = UserHandler(request.user.id)

	if event.owner != user.id:
		return
		print("user is not event owner!!")

	project.functions.matcher.forceGroups(event)
	g = getGroup(event,user)
	if(g != None):
		response_data['group'] = g

	response_data['success'] = True
	return (JsonResponse(response_data))

def rejectGroup(request):
	response_data = {}
	info = request.GET.dict()

	event = EventHandler(info.get('eventID'))
	print(event.exists)
	user = UserHandler(request.user.id)
	group = user.getGroups(event)
	leaveGroup(group,event, user)

	response_data['success'] = True
	return (JsonResponse(response_data))