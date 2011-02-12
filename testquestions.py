#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import deferred

import os
from django.utils import simplejson as json

from models import *
from config import *
from utils import getsubcategories
from testquestionfunctions import makeQuestion

class MainHandler(webapp.RequestHandler):
		
	def get(self):
		subcategories = [(1, 'Algebra'), (2, 'Trigonometry'), (3, 'Geometry')]
		for subcat in subcategories:
			sc = Subcategory()
			sc.category = 1
			sc.subcategory = subcat[0]
			sc.name = subcat[1]
			sc.put()
			
		subcategories = [(1, 'Mechanics (Statics)'), (2, 'Mechanics (Dynamics)'), (3, 'Strength of Materials')]
		for subcat in subcategories:
			sc = Subcategory()
			sc.category = 2
			sc.subcategory = subcat[0]
			sc.name = subcat[1]
			sc.put()
			
		subcategories = [(1, 'DC Circuits'), (2, 'AC Circuits'), (3, 'Electromagnetics')]
		for subcat in subcategories:
			sc = Subcategory()
			sc.category = 3
			sc.subcategory = subcat[0]
			sc.name = subcat[1]
			sc.put()
			
		for category in CATEGORIES:
			for subcat in getsubcategories(category[0]):
				for i in range(100):
					deferred.defer(makeQuestion, category[0], subcat[0], category[1], i, _queue='test')
		
def main():
	application = webapp.WSGIApplication([('/testquestions/', MainHandler),],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()