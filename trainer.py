#!/usr/bin/env python

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
from users import getUserFromKey
from users import getUser2
from config import *

from timezones import phtz
from timezones import utctz

class MainHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def get(self):
		#self.response.headers['Content-Type'] = 'application/xhtml+xml'
		path = os.path.join(os.path.dirname(__file__), 'templates/trainer/main.html')
		self.response.out.write(template.render(path, dict()))
		
class DailyHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def get(self):
		dss = DailySummary.all().filter('quizzer =', None).filter('datetime >=', datetime.datetime.now() - datetime.timedelta(days=30)).order('-datetime')
		
		dtlist = []
		for ds in dss:
			dtval = ds.datetime.strftime("%Y-%m-%d")
			dtlist.append(dtval)
		
		#self.response.headers['Content-Type'] = 'application/xhtml+xml'		
		path = os.path.join(os.path.dirname(__file__), 'templates/trainer/daily.html')
		self.response.out.write(template.render(path, dict(days=dtlist)))
		
class DailyQuizzerOptionsHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		daystr = self.request.get('day')
		dt = datetime.datetime.strptime(daystr, "%Y-%m-%d")
		
		query = DailySummary.all().filter('datetime =', dt)
		
		optionlist = []
		for ds in query:
			if ds.quizzer != None:
				quizzer = getUser2(ds.quizzer)
				optionlist.append((quizzer.key(), quizzer.fullname))
				
		optionlist = sorted(optionlist, key=lambda a: a[1])
		
		path = os.path.join(os.path.dirname(__file__), 'templates/trainer/optionquizzers.html')
		self.response.out.write(template.render(path, dict(options=optionlist)))
		
class DPercentCorrectHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		daystr = self.request.get('day')
		dt = datetime.datetime.strptime(daystr, "%Y-%m-%d")
		
		query = DailySummary.all().filter('datetime =', dt)
		
		quizzerkey = self.request.get('quizzer')
		if not quizzerkey:
			query.filter('quizzer =', None)
		else:
			query.filter('quizzer =', getUserFromKey(quizzerkey))
			
		ds = query.fetch(1)[0]
		
		d = {}
		d['cols'] = [{'id': 'label', 'label': 'label', 'type': 'string'}, {'id': 'value', 'label': 'value', 'type': 'number'}]
		rows = []
		rows.append({'c': [{'v': 'Correct'}, {'v': ds.correctcount}]})
		rows.append({'c': [{'v': 'Wrong'}, {'v': ds.answeredcount - ds.correctcount}]})
		d['rows'] = rows
		
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write(json.dumps(d))
		
class DPercentCategoryHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		daystr = self.request.get('day')
		dt = datetime.datetime.strptime(daystr, "%Y-%m-%d")
		
		query = DailySummary.all().filter('datetime =', dt)
		
		quizzerkey = self.request.get('quizzer')
		if not quizzerkey:
			query.filter('quizzer =', None)
		else:
			query.filter('quizzer =', getUserFromKey(quizzerkey))
			
		ds = query.fetch(1)[0]
		
		query = DailySummaryCategoryCount.all().ancestor(ds)
		
		d = {}
		d['cols'] = [{'id': 'label', 'label': 'label', 'type': 'string'}, {'id': 'value', 'label': 'value', 'type': 'number'}]
		rows = []
		cat = dict(CATEGORIES)
		for dsc in query:
			rows.append({'c': [{'v': cat[dsc.category]}, {'v': dsc.answeredcount}]})
		d['rows'] = rows
		
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write(json.dumps(d))
		
class DAnsweredbyCategoryHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		daystr = self.request.get('day')
		dt = datetime.datetime.strptime(daystr, "%Y-%m-%d")
		
		query = DailySummary.all().filter('datetime =', dt)
		
		quizzerkey = self.request.get('quizzer')
		if not quizzerkey:
			query.filter('quizzer =', None)
		else:
			query.filter('quizzer =', getUserFromKey(quizzerkey))
			
		ds = query.fetch(1)[0]
		
		query = DailySummaryCategoryCount.all().ancestor(ds)
		
		d = {}
		d['cols'] = [{'id': 'label', 'label': 'label', 'type': 'string'},
			{'id': 'value1', 'label': 'Answered Correctly', 'type': 'number'},
			{'id': 'value2', 'label': 'Total Answered', 'type': 'number'}]
		rows = []
		cat = dict(CATEGORIES)
		for dsc in query:
			rows.append({'c': [{'v': cat[dsc.category]}, {'v': dsc.correctcount}, {'v': dsc.answeredcount}]})
		d['rows'] = rows
		
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write(json.dumps(d))
		
class DAnswerSessionListHandler(webapp.RequestHandler):
	@requireusertype('Trainer')
	def post(self):
		daystr = self.request.get('day')
		dt = datetime.datetime.strptime(daystr, "%Y-%m-%d")
		
		query = DailySummary.all().filter('datetime =', dt)
		
		quizzerkey = self.request.get('quizzer')
		query.filter('quizzer =', getUserFromKey(quizzerkey))
		
		ds = query.fetch(1)[0]
		
		query = DailySummaryMarker.all().ancestor(ds)
		
		d = {}
		d['cols'] = [{'id': 'qkey', 'label': 'Question Key', 'type': 'string'},
			{'id': 'time', 'label': 'Time', 'type': 'timeofday'},
			{'id': 'category', 'label': 'Category', 'type': 'string'},
			{'id': 'question', 'label': 'Question', 'type': 'string'},
			{'id': 'correct', 'label': 'Correct', 'type': 'boolean'},
			{'id': 'duration', 'label': 'Duration (s)', 'type': 'number'}]
		
		cat = dict(CATEGORIES)
		rows = []
		for dsm in query:
			ans = dsm.session
			dt = ans.datetime.replace(tzinfo=utctz).astimezone(phtz)
			qstring = ans.question.question
			if len(qstring) > 60:
				qstring = qstring[:60] + '...'
			rows.append({'c': [{'v': str(ans.question.key())},
					{'v': [dt.hour, dt.minute, dt.second]},
					{'v': cat[dsm.category]},
					{'v': qstring},
					{'v': ans.correct},
					{'v': ans.duration}
				]})
				
		d['rows'] = rows
		
		self.response.headers['Content-Type'] = 'text/json'
		self.response.out.write(json.dumps(d))
		
def main():
	application = webapp.WSGIApplication([('/trainer/', MainHandler),
										('/trainer/daily/', DailyHandler),
										('/trainer/daily/percentcorrect', DPercentCorrectHandler),
										('/trainer/daily/percentcategory', DPercentCategoryHandler),
										('/trainer/daily/answerbycategory', DAnsweredbyCategoryHandler),
										('/trainer/daily/quizzeroptions', DailyQuizzerOptionsHandler),
										('/trainer/daily/sessionlist', DAnswerSessionListHandler),
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()