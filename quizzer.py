#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
from django.utils import simplejson as json
import math

from models import *
from users import requireusertype
from config import *
	
class MainHandler(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/quizzer/main.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES)))
    	
class QList(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Trainer')
	def post(self):
		category = self.request.get('category')
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
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'answered':
			questions.filter("answered =", True)
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'unanswered':
			questions.filter("answered =", False)
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'correct':
			questions.filter("answeredcorrectly =", True)
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'wrong':
			questions.filter("answeredcorrectly =", False)
			questions.filter("answered =", True)
			if category != '0':
				questions.filter('category =', int(category))
		questions.order('-questiondatetime')
		
		if cursor:
			questions.with_cursor(cursor)
			prevcursors.append(cursor)
		
		qlist = []
		questionslist = questions.fetch(50)
		for q in questionslist:
			d = {}
			d['key'] = q.parent().key()
			if q.questiontype == 1:
				d['questiontype'] = 'Numerical Answer'
			elif q.questiontype == 2:
				d['questiontype'] = 'Text Answer'
			if len(q.parent().question) > 60:
				d['question'] = q.parent().question[:60] + '...'
			else:
				d['question'] = q.parent().question
			d['category'] = dict(CATEGORIES)[q.category]
			if q.timesanswered > 0:
				d['answered'] = True
			else:
				d['answered'] = False
			qlist.append(d)
		
		disablenext = False
		if len(questionslist) < 50:
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
		prevcursors = self.request.get('prevcursors')
		filterval = self.request.get('filterval')
		
		quizzer = users.get_current_user()
		
		prevcursors = prevcursors.split(',')
		
		questions = QuestionQuizzerStats.all()
		questions.filter("quizzer =", quizzer)
		if filterval == 'all':
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'answered':
			questions.filter("answered =", 0)
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'unanswered':
			questions.filter("answered =", False)
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'correct':
			questions.filter("answeredcorrectly =", True)
			if category != '0':
				questions.filter('category =', int(category))
		elif filterval == 'wrong':
			questions.filter("answeredcorrectly =", False)
			questions.filter("answered =", True)
			if category != '0':
				questions.filter('category =', int(category))
		questions.order('-questiondatetime')
		
		disableprevious = False
		if len(prevcursors) > 1:
			prevcursors.pop();
			questions.with_cursor(prevcursors.pop())
		else:
			disableprevious = True
				
		qlist = []
		questionslist = questions.fetch(50)
		for q in questionslist:
			d = {}
			d['key'] = q.parent().key()
			if q.questiontype == 1:
				d['questiontype'] = 'Numerical Answer'
			elif q.questiontype == 2:
				d['questiontype'] = 'Text Answer'
			if len(q.parent().question) > 60:
				d['question'] = q.parent().question[:60] + '...'
			else:
				d['question'] = q.parent().question
			d['category'] = dict(CATEGORIES)[q.category]
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
				self.response.out.write(json.dumps(dict(question=question.question, sessionkey=str(ans.key()), questionkey=key)))
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
				try:
					error = math.fabs((float(question.answer) - float(answer)) / float(question.answer))
					if error < 0.01:
						ans.correct = True
						correctflag = True
					else:
						ans.correct = False
				except ValueError:
					ans.correct = False
				ans.put()
				db.run_in_transaction(increment_timesanswered, question.index.key())
				
				quizzer = users.get_current_user()
				
				query = QuestionQuizzerStats.all().ancestor(question.key()).filter("quizzer =", quizzer)
				qqs = None
				if not query.count():
					qqs = QuestionQuizzerStats(parent=question, aduration=0.0)
					qqs.put()
				else:
					qqs = query.fetch(1)[0]
					
				
				if correctflag:
					db.run_in_transaction(increment_timescorrect, question.index.key())
					db.run_in_transaction(update_questionquizzer, qqs.key(), True, int(duration))
					self.response.out.write(json.dumps(dict(result="correct")))
				else:
					db.run_in_transaction(increment_timeswrong, question.index.key())
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
		
		quizzer = users.get_current_user()
		
		query = QuestionQuizzerStats.all()
		query.filter("quizzer =", quizzer).filter("category =", int(category)).order("-questiondatetime")
		
		resultlist = query.fetch(1)
		if resultlist:
			markerdate = resultlist[0].questiondatetime
			
			query = Question.all()
			query.filter("category =", int(category)).filter("datetime >", markerdate).order("datetime")
			
		else:
			query = Question.all()
			query.filter("category =", int(category)).order("datetime")
		
		cnt = 0
		for question in query.fetch(20):
			qqs = QuestionQuizzerStats(parent=question,
				quizzer=quizzer,
				category=int(category),
				questiondatetime=question.datetime,
				questiontype=question.questiontype)
			qqs.put()
			cnt += 1
			
		self.response.headers['Content-Type'] = 'text/json'
		if cnt:
			self.response.out.write(json.dumps(dict(result="success")))
		else:
			self.response.out.write(json.dumps(dict(result="failed")))

def main():
	application = webapp.WSGIApplication([('/quizzer/', MainHandler),
										  ('/quizzer/list', QList),
										  ('/quizzer/prevlist', QPrevList),
										  ('/quizzer/startquestion', StartQuestion),
										  ('/quizzer/endquestion', EndQuestion),
										  ('/quizzer/answerstable', AnswersTable),
										  ('/quizzer/requestquestions', RequestQuestions)
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()