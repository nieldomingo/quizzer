#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
from django.utils import simplejson as json
import math
import random

from models import *
from users import requireusertype
from config import *
from utils import getsubcategories
	
class MainHandler(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def get(self):
		self.response.headers['Content-Type'] = 'application/xhtml+xml'
		path = os.path.join(os.path.dirname(__file__), 'templates/quizzer/main.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES)))
    	
class QList(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def post(self):
		category = self.request.get('category')
		subcategory = self.request.get('subcategory')
		cursor = self.request.get('cursor')
		prevcursors = self.request.get('prevcursors')
		filterval = self.request.get('filterval')
		
		quizzer = users.get_current_user()
				
		if prevcursors:
			prevcursors = prevcursors.split(',')
		else:
			prevcursors = []

		questions = QuestionQuizzerStats.all()
		questions.filter("quizzer =", quizzer)
		if filterval == 'all':
			pass
		elif filterval == 'answered':
			questions.filter("answered =", True)
		elif filterval == 'unanswered':
			questions.filter("answered =", False)
		elif filterval == 'correct':
			questions.filter("answeredcorrectly =", True)
		elif filterval == 'wrong':
			questions.filter("answeredcorrectly =", False)
			questions.filter("answered =", True)
				
		if category != '0':
			questions.filter('category =', int(category))
		if subcategory != '0':
			questions.filter('subcategory =', int(subcategory))
			
		questions.order('-questiondatetime')
		
		if cursor:
			questions.with_cursor(cursor)
			prevcursors.append(cursor)
		
		qlist = []
		qtypedict = dict(QUESTIONTYPES)
		questionslist = questions.fetch(25)
		for q in questionslist:
			d = {}
			d['key'] = q.parent().key()
			#if q.questiontype == 1:
			#	d['questiontype'] = 'Numerical Answer'
			#elif q.questiontype == 2:
			#	d['questiontype'] = 'Text Answer'
			d['questiontype'] = qtypedict[q.questiontype]
			if len(q.parent().question) > 40:
				d['question'] = q.parent().question[:40] + '...'
			else:
				d['question'] = q.parent().question
			d['category'] = dict(CATEGORIES)[q.category]
			subcategories = getsubcategories(q.category)
			d['subcategory'] = dict(subcategories)[q.subcategory]
			if q.timesanswered > 0:
				d['answered'] = True
			else:
				d['answered'] = False
			qlist.append(d)
		
		disablenext = False
		if len(questionslist) < 25:
			disablenext = True
		
		cursor = questions.cursor()
		disableprevious = False
		if not prevcursors:
			disableprevious = True
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizzer/list.html')
		self.response.out.write(template.render(path, dict(questions=qlist, cursor=cursor, disablenext=disablenext, disableprevious=disableprevious, prevcursors=','.join(prevcursors))))
		
class QPrevList(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def post(self):
		category = self.request.get('category')
		subcategory = self.request.get('subcategory')
		prevcursors = self.request.get('prevcursors')
		filterval = self.request.get('filterval')
		
		quizzer = users.get_current_user()
		
		prevcursors = prevcursors.split(',')
		
		questions = QuestionQuizzerStats.all()
		questions.filter("quizzer =", quizzer)
		if filterval == 'all':
			pass
		elif filterval == 'answered':
			questions.filter("answered =", 0)
		elif filterval == 'unanswered':
			questions.filter("answered =", False)
		elif filterval == 'correct':
			questions.filter("answeredcorrectly =", True)
		elif filterval == 'wrong':
			questions.filter("answeredcorrectly =", False)
			questions.filter("answered =", True)
			
		if category != '0':
			questions.filter('category =', int(category))
		if subcategory != '0':
			questions.filter('subcategory =', int(subcategory))
			
		questions.order('-questiondatetime')
		
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
			d['key'] = q.parent().key()
			#if q.questiontype == 1:
			#	d['questiontype'] = 'Numerical Answer'
			#elif q.questiontype == 2:
			#	d['questiontype'] = 'Text Answer'
			d['questiontype'] = qtypedict[q.questiontype]
			if len(q.parent().question) > 40:
				d['question'] = q.parent().question[:40] + '...'
			else:
				d['question'] = q.parent().question
			d['category'] = dict(CATEGORIES)[q.category]
			subcategories = getsubcategories(q.category)
			d['subcategory'] = dict(subcategories)[q.subcategory]
			if q.timesanswered > 0:
				d['answered'] = True
			else:
				d['answered'] = False
			qlist.append(d)
		
		disablenext = False
		
		cursor = questions.cursor()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizzer/list.html')
		self.response.out.write(template.render(path, dict(questions=qlist, cursor=cursor, disablenext=disablenext, disableprevious=disableprevious, prevcursors=','.join(prevcursors))))
		
class StartQuestion(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def get(self):
		key = self.request.get('key')
		
		self.response.headers['Content-Type'] = 'text/json'
		
		if key:
			question = db.get(db.Key(key))
			if question:
				ans = AnswerSession()
				ans.question = question
				ans.put()
				d = {}
				d['question'] = question.question
				d['qtype'] = question.questiontype
				d['sessionkey'] = str(ans.key())
				d['questionkey'] = key
				d['diagram'] = question.diagram
				if question.questiontype == 2:
					choices = list(question.choices)
					choices.append(question.answer)
					random.shuffle(choices)
					d['choices'] = choices
					
				self.response.out.write(json.dumps(d))
			else:
				self.response.out.write(json.dumps(dict(message="question not found")))
		else:
			self.response.out.write(json.dumps(dict(message="must supply key")))
			
class EndQuestion(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def get(self):
		questionkey = self.request.get('questionkey')
		sessionkey = self.request.get('sessionkey')
		answer = self.request.get('answer')
		duration = self.request.get('duration')
		
		self.response.headers['Content-Type'] = 'text/json'
		
		if questionkey and sessionkey:
			question = db.get(db.Key(questionkey))
			ans = db.get(db.Key(sessionkey))
			if question and ans:
				#user = users.get_current_user()
				#question.index.quizzers.append(user)
				#question.index.put()
				ans.duration = int(duration)
				ans.answer = answer
				correctflag = False
				if question.questiontype == 1:
					try:
						error = math.fabs((float(question.answer) - float(answer)) / float(question.answer))
						if error < 0.01:
							ans.correct = True
							correctflag = True
						#else:
						#	ans.correct = False
					except ValueError:
						pass
						#ans.correct = False
				elif question.questiontype == 2:
					if answer == question.answer:
						ans.correct = True
						correctflag = True
						
				ans.put()
				#db.run_in_transaction(increment_timesanswered, question.index.key())
				
				quizzer = users.get_current_user()
				
				query = QuestionQuizzerStats.all().ancestor(question.key()).filter("quizzer =", quizzer)
				qqs = None
				if not query.count():
					qqs = QuestionQuizzerStats(parent=question, aduration=0.0)
					qqs.put()
				else:
					qqs = query.fetch(1)[0]
					
				
				if correctflag:
					#db.run_in_transaction(increment_timescorrect, question.index.key())
					db.run_in_transaction(update_questionquizzer, qqs.key(), True, int(duration))
					self.response.out.write(json.dumps(dict(result="correct")))
				else:
					#db.run_in_transaction(increment_timeswrong, question.index.key())
					db.run_in_transaction(update_questionquizzer, qqs.key(), False, int(duration))
					self.response.out.write(json.dumps(dict(result="wrong")))
			else:
				self.response.out.write(json.dumps(dict(message="question not found")))
		else:
			self.response.out.write(json.dumps(dict(message="must supply keys")))

class AnswersTable(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def post(self):
		query = QuestionQuizzerStats().all()
		user = users.get_current_user()
		
		questionkey = self.request.get('questionkey')
		
		query.ancestor(db.Key(questionkey)).filter('quizzer =', user)
		
		if query.count():
			qqs = query.fetch(1)[0]
			path = os.path.join(os.path.dirname(__file__), 'templates/quizzer/answerstable.html')
			self.response.out.write(template.render(path, dict(qqs=qqs)))
		else:
			self.response.out.write("You haven't answered this question yet!")
			
class RequestQuestions(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def get(self):
		category = self.request.get('category')
		subcategory = self.request.get('subcategory')
		
		quizzer = users.get_current_user()
		
		query = QuestionQuizzerStats.all()
		query.filter("quizzer =", quizzer)
		query.filter("active =", True)
		query.filter("category =", int(category))
		query.filter("subcategory =", int(subcategory))		
		query.order("-questiondatetime")
		
		resultlist = query.fetch(1)
		if resultlist:
			markerdate = resultlist[0].questiondatetime
			
			query = Question.all()
			query.filter("active =", True)
			query.filter("category =", int(category))
			query.filter("subcategory =", int(subcategory))
			query.filter("datetime >", markerdate)
			query.order("datetime")
			
		else:
			query = Question.all()
			query.filter("active =", True)
			query.filter("category =", int(category))
			query.filter("subcategory =", int(subcategory))
			query.order("datetime")
		
		cnt = 0
		for question in query.fetch(10):
			qqs = QuestionQuizzerStats(parent=question,
				quizzer=quizzer,
				category=int(category),
				questiondatetime=question.datetime,
				questiontype=question.questiontype,
				subcategory=question.subcategory)
			qqs.put()
			cnt += 1
			
		self.response.headers['Content-Type'] = 'text/json'
		if cnt:
			self.response.out.write(json.dumps(dict(result="success")))
		else:
			self.response.out.write(json.dumps(dict(result="failed")))

class GetSubcategories(webapp.RequestHandler):
	@requireusertype('Trainer', 'Quizzer')
	def post(self):
		category = int(self.request.get('category'))
		noall = self.request.get('noall')
		
		if noall:
			allflag = False
		else:
			allflag = True
		
		subcategories = getsubcategories(category)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizzer/subcategoryoptions.html')
		self.response.out.write(template.render(path, dict(subcategories=subcategories, allflag=allflag)))

def main():
	application = webapp.WSGIApplication([('/quizzer/', MainHandler),
										  ('/quizzer/list', QList),
										  ('/quizzer/prevlist', QPrevList),
										  ('/quizzer/startquestion', StartQuestion),
										  ('/quizzer/endquestion', EndQuestion),
										  ('/quizzer/answerstable', AnswersTable),
										  ('/quizzer/requestquestions', RequestQuestions),
										  ('/quizzer/subcategories', GetSubcategories),
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()