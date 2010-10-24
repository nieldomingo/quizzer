#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
from django.utils import simplejson as json
import cgi
import urllib
import random
import datetime
import math

from models import *
from users import requireusertype
from users import getUserType
from users import getQuizzers
from chart import piechart
from config import *

class MainHandler(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Encoder', 'Trainer')
	def get(self):
		usertype = getUserType()
		if usertype == 'Quizzer':
			self.redirect('/quizzer/')
		elif usertype == 'Encoder':
			self.redirect('/questions/')
		elif usertype == 'Trainer':
			self.redirect('/questions/')
		
class LogoutHandler(webapp.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url('/'))

class TestQuestionsHandler(webapp.RequestHandler):
	def get(self):
		question = "Lorem ipsum est ad kasd meliore, at vim facilis eloquentiam, ex est elit utamur dissentiet. Ne usu tollit laoreet, fabulas posidonium duo no. Cum quaeque consequuntur at. Qui ei eius interesset. Novum consectetuer vel eu, has admodum inciderint te."
		answer = "100"
		for category in CATEGORIES:
			for i in range(30):
				q = Question(questiontype=1, question=category[1] + " Question %s "%i + question, answer=answer, category=category[0])
				q.put()

def main():
	application = webapp.WSGIApplication([('/', MainHandler),
	                                      ('/logout', LogoutHandler),
	                                      ('/testquestions', TestQuestionsHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
