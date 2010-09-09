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

class Question(db.Model):
	author = db.UserProperty(auto_current_user_add=True)
	questiontype = db.IntegerProperty()
	question = db.TextProperty()
	answer = db.StringProperty()
	datetime = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):
	def get(self):
		self.response.out.write('Hello world!')
		
class ManageQuestionHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'manage_questions.html')
		self.response.out.write(template.render(path, {}))

class SaveQuestionHandler(webapp.RequestHandler):
	def get(self):
		questiontype = self.request.get('questiontype')
		question = self.request.get('question')
		answer = self.request.get('answer')
		key = self.request.get('key')
		
		if not key:
			q = Question(questiontype=int(questiontype), question=question, answer=answer)
			
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
			qlist.append(d)
		
		path = os.path.join(os.path.dirname(__file__), 'questionslist.html')
		self.response.out.write(template.render(path, dict(questions=qlist)))

class QuestionViewHandler(webapp.RequestHandler):
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		
		path = os.path.join(os.path.dirname(__file__), 'questionview.html')
		self.response.out.write(template.render(path, dict(question=question)))
		
class EditQuestionHandler(webapp.RequestHandler):
	def post(self):
		key_name = self.request.get('key')
		question = db.get(db.Key(key_name))
		path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
		self.response.out.write(template.render(path, dict(question=question)))
			
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'editquestion.html')
		self.response.out.write(template.render(path, dict()))

def main():
	application = webapp.WSGIApplication([('/', MainHandler),
	                                      ('/managequestions', ManageQuestionHandler),
	                                      ('/savequestion', SaveQuestionHandler),
	                                      ('/getquestions', GetQuestionsHandler),
	                                      ('/questionview', QuestionViewHandler),
	                                      ('/editquestion', EditQuestionHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
