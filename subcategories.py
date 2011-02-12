#!/usr/bin/env python

from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
from django.utils import simplejson as json
import datetime

from models import *
from users import requireusertype
from config import *
from utils import refreshsubcategories

class MainHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/trainer/subcategories.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES)))

class SaveHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		subcategoryname = self.request.get('subcategoryname')
		key = self.request.get('key')
		category = int(self.request.get('category'))
		
		self.response.headers['Content-Type'] = 'text/json'
		try:
			if not key:
				scindex = 1
				query = Subcategory.all().filter('category =', category).order('-subcategory')
				subcategory = query.fetch(1)
				if subcategory:
					scindex  = subcategory[0].subcategory + 1
					
				subcat = Subcategory()
				subcat.category = category
				subcat.subcategory = scindex
				subcat.name = subcategoryname
				subcat.put()
			else:
				subcat = db.get(db.Key(key))
				subcat.name = subcategoryname
				subcat.put()
				
			taskqueue.Task(url='/trainer/subcategories/refresh', params={'category': category}).add()
			
			self.response.out.write(json.dumps(dict(result='saved')))
		except db.NotSavedError:
			self.response.out.write(json.dumps(dict(result='not saved')))
			
class ListHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		category = int(self.request.get('category'))
		
		query = Subcategory.all().filter('category =', category).order('name')
		subcategories = []
		for subcat in query:
			subcategories.append((subcat.name, subcat.key()))
			
		path = os.path.join(os.path.dirname(__file__), 'templates/trainer/subcategorylist.html')
		self.response.out.write(template.render(path, dict(subcategories=subcategories)))

class RefreshSubcategoriesHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		category = int(self.request.get('category'))
		
		refreshsubcategories(category)

def main():
	application = webapp.WSGIApplication([('/trainer/subcategories/', MainHandler),
										('/trainer/subcategories/save', SaveHandler),
										('/trainer/subcategories/list', ListHandler),
										('/trainer/subcategories/refresh', RefreshSubcategoriesHandler),
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()