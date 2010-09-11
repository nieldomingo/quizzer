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
import json
import cgi
import urllib

CATEGORIES = [(1, 'Math'), (2, 'Engineering Science'), (3, 'Electrical Engineering')]

class Question(db.Model):
	author = db.UserProperty(auto_current_user_add=True)
	questiontype = db.IntegerProperty()
	question = db.TextProperty()
	answer = db.StringProperty()
	datetime = db.DateTimeProperty(auto_now_add=True)
	category = db.IntegerProperty()

class MainHandler(webapp.RequestHandler):
	def get(self):
		self.response.out.write('Hello world!')
		
class ManageQuestionHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'manage_questions.html')
		self.response.out.write(template.render(path, {}))

class SaveQuestionHandler(webapp.RequestHandler):
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
	def get(self):
		questions = db.GqlQuery("SELECT * FROM Question")
		
		qlist = []
		for q in questions:
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
		
		path = os.path.join(os.path.dirname(__file__), 'questionslist.html')
		self.response.out.write(template.render(path, dict(questions=qlist)))

class QuestionViewHandler(webapp.RequestHandler):
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		
		category = dict(CATEGORIES)[question.category]
		path = os.path.join(os.path.dirname(__file__), 'questionview.html')
		self.response.out.write(template.render(path, dict(question=question, category=category)))
		
class EditQuestionHandler(webapp.RequestHandler):
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
		self.response.out.write(template.render(path, dict(question=question, categories=CATEGORIES)))
			
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
		self.response.out.write(template.render(path, dict(categories=CATEGORIES)))
		
class DeleteQuestionsHandler(webapp.RequestHandler):
	def post(self):
		keys = self.request.get('keys')
		for key_name in keys.split(','):
			question = db.get(db.Key(key_name))
			question.delete();
			
class TestQuestionsHandler(webapp.RequestHandler):
	def get(self):
		question = "Lorem ipsum est ad kasd meliore, at vim facilis eloquentiam, ex est elit utamur dissentiet. Ne usu tollit laoreet, fabulas posidonium duo no. Cum quaeque consequuntur at. Qui ei eius interesset. Novum consectetuer vel eu, has admodum inciderint te."
		answer = "100"
		for category in CATEGORIES:
			for i in range(100):
				q = Question(questiontype=1, question=question, answer=answer, category=category[0])
				q.put()

def main():
	application = webapp.WSGIApplication([('/', MainHandler),
	                                      ('/managequestions', ManageQuestionHandler),
	                                      ('/savequestion', SaveQuestionHandler),
	                                      ('/getquestions', GetQuestionsHandler),
	                                      ('/questionview', QuestionViewHandler),
	                                      ('/editquestion', EditQuestionHandler),
	                                      ('/deletequestions', DeleteQuestionsHandler),
	                                      ('/testquestions', TestQuestionsHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
