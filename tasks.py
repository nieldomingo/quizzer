#!/usr/bin/env python

from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
import datetime

from models import *
from config import *
from timezones import phtz
from timezones import utctz
	
class MainHandler(webapp.RequestHandler):
	def get(self):
		self.response.out.write("Hello")
		
def update_dailysummary(key, correct, duration, category, anskey):
	ds = db.get(key)
	if ds:
		ds.avgduration = (ds.avgduration * ds.answeredcount + duration) / (ds.answeredcount + 1)
		ds.answeredcount += 1
		if correct:
			ds.correctcount += 1
		ds.put()

		q = DailySummaryCategoryCount.all().ancestor(ds).filter('category =', category)
		if q.count():
			dsc = q.fetch(1)[0]
			dsc.avgduration = (dsc.avgduration * dsc.answeredcount + duration) / (dsc.answeredcount + 1)
			dsc.answeredcount += 1
			if correct:
				dsc.correctcount += 1
			dsc.put()
		else:
			dsc = DailySummaryCategoryCount(parent=ds)
			dsc.category = category
			dsc.answeredcount = 1
			dsc.avgduration = float(duration)
			if correct:
				dsc.correctcount = 1
			else:
				dsc.correctcount = 0
			dsc.put()
			
		dsm = DailySummaryMarker(parent=ds)
		dsm.session = db.Key(anskey)
		dsm.category = category
		dsm.put()

class SummarizeDayHandler(webapp.RequestHandler):
	def post(self):
		cursor = self.request.get('cursor')
		year = int(self.request.get('year'))
		month = int(self.request.get('month'))
		day = int(self.request.get('day'))
		gen = int(self.request.get('gen'))
		
		dt = datetime.datetime(year=year, month=month, day=day, tzinfo=phtz).astimezone(utctz)
		
		query = AnswerSession.all()
		query.filter("datetime >=", dt)
		query.filter("datetime <", dt + datetime.timedelta(hours=24))
		
		if cursor:
			query.with_cursor(cursor)
			
		anssession = query.fetch(3)
		
		if len(anssession) == 3:
			try:
				taskqueue.Task(url='/tasks/summarizeday', params={'cursor': query.cursor(),
								'year': str(year), 'month': str(month), 'day': str(day),
								'gen': gen + 1}, name='%s-%s-%s-%s'%(year, month, day, gen + 1)).add()
			except taskqueue.TaskAlreadyExistsError:
				pass
		
		for ans in anssession:
			q = DailySummary.all()		
			q.filter('year =', year)
			q.filter('month =', month)
			q.filter('day =', day)
			q.filter('quizzer =', ans.quizzer)
			
			if q.count():
				ds = q.fetch(1)[0]
			else:
				ds = DailySummary()
				ds.quizzer = ans.quizzer
				ds.year = year
				ds.month = month
				ds.day = day
				ds.put()
			
			q2 = DailySummaryMarker.all().ancestor(ds).filter('session =', ans)
			if not q2.count():
				db.run_in_transaction(update_dailysummary, ds.key(), ans.correct, ans.duration, ans.question.category, str(ans.key()))
			
		
class SummarizeDailyHandler(webapp.RequestHandler):
	def get(self):
		dtnow = datetime.datetime.now(phtz)
		dtprev = datetime.datetime(dtnow.year, dtnow.month, dtnow.day, tzinfo=phtz) - datetime.timedelta(days=1)
		
		taskqueue.Task(url='/tasks/summarizeday', params={'year': str(dtprev.year), 'month': str(dtprev.month),
						'day': str(dtprev.day), 'gen': '1'}, name="%s-%s-%s-%s"%(dtprev.year, dtprev.month, dtprev.day, 1)).add()

def main():
	application = webapp.WSGIApplication([('/tasks/', MainHandler),
										('/tasks/summarizedaily', SummarizeDailyHandler),
										('/tasks/summarizeday', SummarizeDayHandler),
										],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()