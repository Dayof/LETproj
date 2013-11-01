#coding: utf-8

from abc import *

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.forms import ValidationError

from ELO.BaseUnit import Name, Password
from ELO.EntityUnit import Adm
from Login.forms import LoginForm

class IfUiLogin:

	__metaclass__ = ABCMeta

	@abstractmethod
	def run(self): pass

class IfBusLogin:

	__metaclass__ = ABCMeta

	@abstractmethod
	def validate(self, user): pass

class IfPersLogin:

	__metaclass__ = ABCMeta

	@abstractmethod
	def getId(self, username=None, password=None): pass

	@abstractmethod
	def getPassword(self, username=None, id=None): pass

	@abstractmethod
	def getId(self, username=None, password=None): pass

class UiLogin(IfUiLogin):
	
	__busLogin = None
	
	def run(self, request):
		if request.method == 'POST':
			form = LoginForm(request.POST)
			try:
				if form.is_valid():
					self.__busLogin.validate(form.cleaned_data['username'], form.cleaned_data['password'])
				else:
					raise ValueError()
			except (ValueError, ValidationError) as exc:
				return render(request, 'login/form.html', {'form': form, 'error': exc})
			else:
				return render(request, 'login/form.html', {'form': LoginForm()})
		else:
			return render(request, 'login/form.html', {'form': LoginForm()})

	def setBus(self, busClass):
		self.__busLogin = busClass

class BusLogin(IfBusLogin):

	__persLogin = None

	def validate(self, username, password):
		if username != Name(u"Yurick") or password != Password("a793812b"):
			raise ValueError("Usuário e/ou senha incorreto.")

	def setPers(self, persClass):
		self.__persClass = persClass

class PersLogin(IfPersLogin):

	def getId(self, username=None, password=None): pass

	def getPassword(self, username=None, id=None): pass

	def getUsername(self, password=None, id=None): pass