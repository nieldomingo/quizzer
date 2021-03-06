#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
from django.utils import simplejson as json

from models import *
from users import requireusertype
from config import *
from utils import getsubcategories

import time
	
class MainHandler(webapp.RequestHandler):
	@requireusertype('Trainer', 'Encoder')
	def get(self):
		self.response.headers['Content-Type'] = 'application/xhtml+xml'
		path = os.path.join(os.path.dirname(__file__), 'templates/questions/main.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES, questiontypes=QUESTIONTYPES)))
    	
class Save(webapp.RequestHandler):
	@requireusertype('Trainer', 'Encoder')
	def get(self):
		category = self.request.get('category')
		subcategory = self.request.get('subcategory')
		qtype = self.request.get('qtype')
		questiontext = self.request.get('question')
		answer = self.request.get('answer')
		key = self.request.get('key')
		diagram = self.request.get('diagram')
		active = self.request.get('active')
		
		if not key:
			question = Question()
		else:
			question = db.get(db.Key(key))
			
		question.category = int(category)
		question.subcategory = int(subcategory)
		question.questiontype = int(qtype)
		question.question = questiontext
		question.answer = answer
			
		if diagram:
			question.diagram = diagram
				
		if qtype == '2':
			question.choices = []
			question.choices.append(self.request.get('choice1'))
			question.choices.append(self.request.get('choice2'))
			question.choices.append(self.request.get('choice3'))
		else:
			question.choices = []
		
		if active == 'true':
			question.active = True
		else:
			question.active = False
			
		self.response.headers['Content-Type'] = 'text/json'
		try:	
			question.put()
			self.response.out.write(json.dumps(dict(result="saved")))
		except db.NotSavedError:
			self.response.out.write(json.dumps(dict(result="not saved")))
			
	def post(self):
		self.get();
			
class QList(webapp.RequestHandler):
	@requireusertype('Trainer', 'Encoder')
	def post(self):
		category = self.request.get('category')
		cursor = self.request.get('cursor')
		searchstring = self.request.get('searchstring')
		prevcursors = self.request.get('prevcursors')
		subcategory = self.request.get('subcategory')
		
		if prevcursors:
			prevcursors = prevcursors.split(',')
		else:
			prevcursors = []

		questions = Question.all()
		if category != '0':
			questions.filter('category =', int(category))
		if subcategory != '0':
			questions.filter('subcategory =', int(subcategory))
		if searchstring:
			questions.search(searchstring, properties=['question'])
		questions.order('-datetime')
		
		if cursor:
			questions.with_cursor(cursor)
			prevcursors.append(cursor)
		
		qlist = []
		qtypedict = dict(QUESTIONTYPES)
		questionslist = questions.fetch(25)
		for q in questionslist:
			d = {}
			d['key'] = q.key()
			#if q.questiontype == 1:
			#	d['questiontype'] = 'Numerical Answer'
			#elif q.questiontype == 2:
			#	d['questiontype'] = 'Text Answer'
			d['questiontype'] = qtypedict[q.questiontype]
			if len(q.question) > 60:
				d['question'] = q.question[:60] + '...'
			else:
				d['question'] = q.question
			d['answer'] = q.answer
			d['datetime'] = q.datetime.isoformat()
			d['category'] = dict(CATEGORIES)[q.category]
			qlist.append(d)
		
		disablenext = False
		if len(questionslist) < 25:
			disablenext = True
		
		cursor = questions.cursor()
		disableprevious = False
		if not prevcursors:
			disableprevious = True
		
		path = os.path.join(os.path.dirname(__file__), 'templates/questions/list.html')
		self.response.out.write(template.render(path, dict(questions=qlist, cursor=cursor, disablenext=disablenext, disableprevious=disableprevious, prevcursors=','.join(prevcursors))))
		
class QPrevList(webapp.RequestHandler):
	@requireusertype('Trainer', 'Encoder')
	def post(self):
		category = self.request.get('category')
		searchstring = self.request.get('searchstring')
		prevcursors = self.request.get('prevcursors')
		subcategory = self.request.get('subcategory')
		
		prevcursors = prevcursors.split(',')		

		questions = Question.all()
		if category != '0':
			questions.filter('category =', int(category))
		if subcategory != '0':
			questions.filter('subcategory =', int(subcategory))
		if searchstring:
			questions.search(searchstring, properties=['question'])
		questions.order('-datetime')
		
		disableprevious = False
		if len(prevcursors) > 1:
			prevcursors.pop();
			questions.with_cursor(prevcursors.pop())
		else:
			disableprevious = True
		
		qlist = []
		qtypedict = dict(QUESTIONTYPES)
		questionslist = questions.fetch(25)
		for q in questionslist:
			d = {}
			d['key'] = q.key()
			#if q.questiontype == 1:
			#	d['questiontype'] = 'Numerical Answer'
			#elif q.questiontype == 2:
			#	d['questiontype'] = 'Text Answer'
			d['questiontype'] = qtypedict[q.questiontype]
			if len(q.question) > 60:
				d['question'] = q.question[:60] + '...'
			else:
				d['question'] = q.question
			d['answer'] = q.answer
			d['datetime'] = q.datetime.isoformat()
			d['category'] = dict(CATEGORIES)[q.category]
			qlist.append(d)
		
		disablenext = False
		
		cursor = questions.cursor()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/questions/list.html')
		self.response.out.write(template.render(path, dict(questions=qlist, cursor=cursor, disablenext=disablenext, disableprevious=disableprevious, prevcursors=','.join(prevcursors))))
		
class QuestionDetail(webapp.RequestHandler):
	@requireusertype('Trainer', 'Encoder')
	def get(self):
		key = self.request.get('key')
		
		self.response.headers['Content-Type'] = 'text/json'
		
		qtypedict = dict(QUESTIONTYPES)
		
		if key:
			question = db.get(db.Key(key))
			if question:
				d = {}
				d['type'] = question.questiontype
				#if question.questiontype == 1:
				#	d['typename'] = 'Numerical Answer'
				#elif question.questiontype == 2:
				#	d['typename'] = 'Text Answer'
				d['typename'] = qtypedict[question.questiontype]
				d['category'] = question.category
				d['categoryname'] = dict(CATEGORIES)[question.category]
				d['question'] = question.question
				d['answer'] = question.answer
				d['datetime'] = question.datetime.isoformat()
				if question.diagram:
					d['diagram'] = question.diagram
				else:
					d['diagram'] = ''
				d['key'] = key
				
				if question.questiontype == 2:
					d['choice1'] = question.choices[0]
					d['choice2'] = question.choices[1]
					d['choice3'] = question.choices[2]
					
				# if statement necessary to consider the case of questions without subcategories
				# this eventually would be obsolete	
				subcategories = getsubcategories(question.category)
				if question.subcategory:
					d['subcategory'] = question.subcategory
					d['subcategoryname'] = dict(subcategories)[question.subcategory]
				else:
					d['subcategory'] = 0
					d['subcategoryname'] = ''
					
				d['subcategoryoptions'] = subcategories
				
				d['active'] = question.active
					
				self.response.out.write(json.dumps(d))
			else:
				self.response.out.write(json.dumps(dict(message="question not found")))
		else:
			self.response.out.write(json.dumps(dict(message="must supply key")))

class GetSubcategories(webapp.RequestHandler):
	@requireusertype('Trainer', 'Encoder')
	def post(self):
		category = int(self.request.get('category'))
		noall = self.request.get('noall')
		
		if noall:
			allflag = False
		else:
			allflag = True
		
		subcategories = getsubcategories(category)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/questions/subcategoryoptions.html')
		self.response.out.write(template.render(path, dict(subcategories=subcategories, allflag=allflag)))

def main():
	application = webapp.WSGIApplication([('/questions/', MainHandler),
											('/questions/save', Save),
											('/questions/list', QList),
											('/questions/prevlist', QPrevList),
											('/questions/detail', QuestionDetail),
											('/questions/subcategories', GetSubcategories),
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()