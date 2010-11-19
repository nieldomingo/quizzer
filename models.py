from google.appengine.ext import db
from google.appengine.ext import search
from google.appengine.api import users

class QuestionIndex(db.Model):
	#quizzers = db.ListProperty(users.User)
	datetime = db.DateTimeProperty(auto_now_add=True)
	category = db.IntegerProperty()
	active = db.BooleanProperty(default=True)
	questiontype = db.IntegerProperty(default=1)
	timesanswered = db.IntegerProperty(default=0)
	timescorrect = db.IntegerProperty(default=0)
	timeswrong = db.IntegerProperty(default=0)

class Question(search.SearchableModel):
	#author = db.UserProperty(auto_current_user_add=True) # for removal
	questiontype = db.IntegerProperty(default=1)
	question = db.TextProperty()
	diagram = db.TextProperty()
	answer = db.StringProperty()
	datetime = db.DateTimeProperty(auto_now_add=True)
	category = db.IntegerProperty()
	active = db.BooleanProperty(default=True)
	#timesanswered = db.IntegerProperty(default=0) # for removal
	index = db.ReferenceProperty(QuestionIndex)
	choices = db.StringListProperty()
	
	@classmethod
	def SearchableProperties(cls):
		return [['question']]
		
	def put(self, **kwargs):
		search.SearchableModel.put(self, **kwargs)
		if not self.index:
			qi = QuestionIndex(parent=self,
								quizzers=[],
								datetime=self.datetime,
								category=self.category,
								active=self.active,
								questiontype=self.questiontype)
			qi.put()
			self.index = qi
			search.SearchableModel.put(self, **kwargs)
		else:
			self.index.category = self.category
			self.index.active = self.active
			self.index.questiontype = self.questiontype
			self.index.put()

class AnswerSession(db.Model):
	datetime = db.DateTimeProperty(auto_now_add=True)
	quizzer = db.UserProperty(auto_current_user_add=True)
	answer = db.StringProperty()
	correct = db.BooleanProperty(default=False)
	duration = db.IntegerProperty()
	question = db.ReferenceProperty(Question)
	
class QuestionQuizzerStats(db.Model):
	quizzer = db.UserProperty(auto_current_user_add=True)
	category = db.IntegerProperty()
	questiondatetime = db.DateTimeProperty(auto_now_add=True)
	questiontype = db.IntegerProperty(default=1)
	timesanswered = db.IntegerProperty(default=0)
	timescorrect = db.IntegerProperty(default=0)
	timeswrong = db.IntegerProperty(default=0)
	aduration = db.FloatProperty()
	answered = db.BooleanProperty(default=False)
	answeredcorrectly = db.BooleanProperty(default=False)
	
class DailySummary(db.Model):
	quizzer = db.UserProperty()
	answeredcount = db.IntegerProperty(default=0)
	correctcount = db.IntegerProperty(default=0)
	avgduration = db.FloatProperty(default=0.0)
	year = db.IntegerProperty()
	month = db.IntegerProperty()
	day = db.IntegerProperty()
	
class DailySummaryMarker(db.Model):
	category = db.IntegerProperty()
	session = db.ReferenceProperty(AnswerSession)
	
class DailySummaryCategoryCount(db.Model):
	category = db.IntegerProperty()
	answeredcount = db.IntegerProperty(default=0)
	correctcount = db.IntegerProperty(default=0)
	avgduration = db.FloatProperty()
	
def increment_timesanswered(key):
	q = db.get(key)
	q.timesanswered += 1
	q.put()
	
def increment_timescorrect(key):
	q = db.get(key)
	q.timescorrect += 1
	q.put()
	
def increment_timeswrong(key):
	q = db.get(key)
	q.timeswrong += 1
	q.put()
	
def update_questionquizzer(key, iscorrect, duration):
	q = db.get(key)
	if iscorrect:
		q.timescorrect += 1
		q.answeredcorrectly = True
	else:
		q.timeswrong += 1
	
	if q.aduration != None:
		q.aduration = (q.aduration * q.timesanswered + duration) / (q.timesanswered + 1)
	else:
		q.aduration = float(duration)
	
	q.timesanswered += 1
	q.answered = True
	
	q.put()