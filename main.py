#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
#import json
from django.utils import simplejson as json
import cgi
import urllib
import random
import datetime
import math

from models import *
from users import requireusertype
from users import getUserType

CATEGORIES = [(1, 'Math'), (2, 'Engineering Science'), (3, 'Electrical Engineering')]
QUESTIONSPERQUIZ = 5

class MainHandler(webapp.RequestHandler):
	@requireusertype('Quizzer', 'Encoder', 'Trainer')
	def get(self):
		usertype = getUserType()
		if usertype == 'Quizzer':
			self.redirect('/myquizzes')
		elif usertype == 'Encoder':
			self.redirect('/managequestions')
		elif usertype == 'Trainer':
			self.redirect('/managequestions')
		
class LogoutHandler(webapp.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url('/'))
		
class ManageQuestionHandler(webapp.RequestHandler):
	@requireusertype('Encoder', 'Trainer')
	def get(self):
		#path = os.path.join(os.path.dirname(__file__), 'templates/manage_questions.html')
		path = os.path.join(os.path.dirname(__file__), 'templates/managequestions.html')
		self.response.out.write(template.render(path, {}))

class SaveQuestionHandler(webapp.RequestHandler):
	@requireusertype('Encoder', 'Trainer')
	def get(self):
		category = self.request.get('questioncategory')
		questiontype = self.request.get('questiontype')
		question = self.request.get('question')
		answer = self.request.get('answer')
		key = self.request.get('key')
		
		if not key:
			q = Question(questiontype=int(questiontype), question=question, answer=answer, category=int(category))
			
			try:
				q.put()
				self.response.out.write(json.dumps(dict(result="saved")))
			except db.NotSavedError:
				self.response.out.write(json.dumps(dict(result="not saved")))
		else:
			q = db.get(db.Key(key))
			q.questiontype = int(questiontype)
			q.question = question
			q.answer = answer
			q.category = int(category)
			
			try:	
				q.put()
				self.response.out.write(json.dumps(dict(result="saved")))
			except db.NotSavedError:
				self.response.out.write(json.dumps(dict(result="not saved")))

class GetQuestionsHandler(webapp.RequestHandler):
	@requireusertype('Encoder', 'Trainer')
	def post(self):
		questions = Question.all()
		
		totalcount = questions.count()
		limit = 25
		offset = 0
		
		if self.request.get('offset'):
			offset = int(self.request.get('offset'))
		
		qlist = []
		questionslist = questions.fetch(limit, offset)
		for q in questionslist:
			d = {}
			d['key'] = q.key()
			d['author'] = q.author
			if q.questiontype == 1:
				d['questiontype'] = 'Numerical Answer'
			elif q.questiontype == 2:
				d['questiontype'] = 'Text Answer'
			d['question'] = q.question
			d['answer'] = q.answer
			d['datetime'] = q.datetime.isoformat()
			d['category'] = dict(CATEGORIES)[q.category]
			qlist.append(d)
		
		newoffset = offset + limit
		if (offset - limit) >= 0:
			prev=True
		else:
			prev=False
		path = os.path.join(os.path.dirname(__file__), 'templates/questionslist.html')
		if newoffset < totalcount:
			self.response.out.write(template.render(path, dict(questions=qlist, offset=newoffset, prev=prev, next=True)))
		else:
			self.response.out.write(template.render(path, dict(questions=qlist, offset=newoffset, prev=prev, next=False)))

class QuestionViewHandler(webapp.RequestHandler):
	@requireusertype('Encoder', 'Trainer')
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		
		category = dict(CATEGORIES)[question.category]
		path = os.path.join(os.path.dirname(__file__), 'templates/questionview.html')
		self.response.out.write(template.render(path, dict(question=question, category=category)))
		
class EditQuestionHandler(webapp.RequestHandler):
	@requireusertype('Encoder', 'Trainer')
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		path = os.path.join(os.path.dirname(__file__), 'templates/editquestion.html')
		self.response.out.write(template.render(path, dict(question=question, categories=CATEGORIES)))
	
	@requireusertype('Encoder', 'Trainer')		
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/editquestion.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES)))
		
class DeleteQuestionsHandler(webapp.RequestHandler):
	@requireusertype('Encoder', 'Trainer')
	def post(self):
		keys = self.request.get('keys')
		for key_name in keys.split(','):
			question = db.get(db.Key(key_name))
			question.delete();
			
class MyQuizzesHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/myquizzes.html')
		self.response.out.write(template.render(path, {}))

class GenerateQuizFormHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/generatequizform.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES)))
		
class GenerateQuizHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		category = self.request.get('category')
		user = users.get_current_user()
		query = Question.all()
		query.filter('category =', int(category))
		totalcount = query.count()
		
		quiz = Quiz()
		timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		quiz.title = 'Generated Quiz %s [%s]'%(timestamp, dict(CATEGORIES)[int(category)])
		quiz.quiztype = 0
		quiz.quizzer = user
		
		if totalcount >= 10:
			indices = random.sample(range(totalcount), QUESTIONSPERQUIZ)
			for index, question in enumerate(query):
				if index in indices:
					quiz.questions.append(question.key())
		else:
			for question in query:
				quiz.questions.append(question.key())
		
		quiz.put()
		
		self.response.out.write("%s"%totalcount)
		
class ListQuizHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		user = users.get_current_user()
		
		query = Quiz.all()
		query.filter('quizzer =', user)
		query.order('-datetime')
		quizzes = []
		for q in query:
			quizzes.append(dict(title=q.title, completed=q.completed, key=q.key(), author=q.author.nickname()))
			
		path = os.path.join(os.path.dirname(__file__), 'templates/listquiz.html')
		self.response.out.write(template.render(path, dict(quizzes=quizzes)))

class QuizHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		key_name = self.request.get('key')
		quiz = db.get(db.Key(key_name))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quiz.html')
		self.response.out.write(template.render(path, dict(quiz=quiz)))
		
class QuizQuestionViewHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizquestionview.html')
		self.response.out.write(template.render(path, dict(question=question)))
		
class QuizQuestionAnswerHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		
		sessionkey = self.request.get('sessionkey')
		quizsession = db.get(db.Key(sessionkey))
		
		duration = self.request.get('duration')
		answer = self.request.get('answer')
		
		if question.questiontype == 1:
			qsa = QuizSessionAnswer()
			qsa.answer = answer
			qsa.duration = int(duration)
			qsa.question = question
			try:
				error = math.fabs((float(question.answer) - float(answer)) / float(question.answer))
				if error < 0.01:
					self.response.headers['Content-Type'] = 'text/json'
					self.response.out.write(json.dumps(dict(result="correct")))
					qsa.correct = True
				else:
					self.response.headers['Content-Type'] = 'text/json'
					self.response.out.write(json.dumps(dict(result="wrong")))
			except ValueError:
				self.response.headers['Content-Type'] = 'text/json'
				self.response.out.write(json.dumps(dict(result="wrong")))
			qsa.put()
			quizsession.answers.append(qsa.key())
			quizsession.put()
			
			db.run_in_transaction(increment_timesanswered, question.key())
				
class QuizEndHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def post(self):
		key_name = self.request.get('quizkey')
		quiz = db.get(db.Key(key_name))
		
		sessionkey = self.request.get('sessionkey')
		quizsession = db.get(db.Key(sessionkey))
		
		quizsession.completed = True
		
		numcorrect = 0
		totalduration = 0
		
		results = []
		for index, key in enumerate(quizsession.answers):
			qsa = db.get(key)
			results.append(qsa)
			if qsa.correct:
				numcorrect += 1
			totalduration += qsa.duration
				
		quizsession.percentscore = numcorrect * 100 / len(results)
		quizsession.duration = totalduration
		
		quiz.completed = True
		
		quizsession.put()
		quiz.put()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizend.html')
		self.response.out.write(template.render(path, dict(results=results)))
		
class StartQuizHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def get(self):
		key_name = self.request.get('quizkey')
		quiz = db.get(db.Key(key_name))
		
		quizsession = QuizSession()
		quizsession.quiz = quiz
		
		quizsession.put()
		
		sessionkey = str(quizsession.key())
		
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write(json.dumps(dict(sessionkey=sessionkey)))
		
class QuizStatisticsHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def post(self):
		key_name = self.request.get('quizkey')
		quiz = db.get(db.Key(key_name))
		
		sessions = quiz.quizsession_set.order('-datetime')
		#for session in sessions:
		#	session.datestr = session.datetime.strftime("%d/%m/%Y %H:%M:%s")
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizstats.html')
		self.response.out.write(template.render(path, dict(sessions=sessions)))

class QuizResultViewHandler(webapp.RequestHandler):
	@requireusertype('Quizzer')
	def post(self):
		key_name = self.request.get('quizsession')
		quizsession = db.get(db.Key(key_name))
		
		results = []
		for index, key in enumerate(quizsession.answers):
			qsa = db.get(key)
			results.append(qsa)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/quizresult.html')
		self.response.out.write(template.render(path, dict(results=results)))

class TestQuestionsHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def get(self):
		question = "Lorem ipsum est ad kasd meliore, at vim facilis eloquentiam, ex est elit utamur dissentiet. Ne usu tollit laoreet, fabulas posidonium duo no. Cum quaeque consequuntur at. Qui ei eius interesset. Novum consectetuer vel eu, has admodum inciderint te."
		answer = "100"
		for category in CATEGORIES:
			for i in range(100):
				q = Question(questiontype=1, question="Question %s "%i + question, answer=answer, category=category[0])
				q.put()

def main():
	application = webapp.WSGIApplication([('/', MainHandler),
	                                      ('/logout', LogoutHandler),
	                                      ('/managequestions', ManageQuestionHandler),
	                                      ('/savequestion', SaveQuestionHandler),
	                                      ('/getquestions', GetQuestionsHandler),
	                                      ('/questionview', QuestionViewHandler),
	                                      ('/editquestion', EditQuestionHandler),
	                                      ('/deletequestions', DeleteQuestionsHandler),
	                                      ('/myquizzes', MyQuizzesHandler),
	                                      ('/generatequizform', GenerateQuizFormHandler),
	                                      ('/generatequiz', GenerateQuizHandler),
	                                      ('/listquiz', ListQuizHandler),
	                                      ('/quiz', QuizHandler),
	                                      ('/quizquestionview', QuizQuestionViewHandler),
	                                      ('/quizquestionanswer', QuizQuestionAnswerHandler),
	                                      ('/quizend', QuizEndHandler),
	                                      ('/startquiz', StartQuizHandler),
	                                      ('/quizstats', QuizStatisticsHandler),
	                                      ('/quizresult', QuizResultViewHandler),
	                                      ('/testquestions', TestQuestionsHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
