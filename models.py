from google.appengine.ext import db

class Question(db.Model):
	author = db.UserProperty(auto_current_user_add=True)
	questiontype = db.IntegerProperty()
	question = db.TextProperty()
	answer = db.StringProperty()
	datetime = db.DateTimeProperty(auto_now_add=True)
	category = db.IntegerProperty()
	
class Quiz(db.Model):
	title = db.StringProperty()
	quiztype = db.IntegerProperty()
	quizzer = db.UserProperty()
	author = db.UserProperty(auto_current_user_add=True)
	datetime = db.DateTimeProperty(auto_now_add=True)
	questions = db.ListProperty(db.Key)
	completed = db.BooleanProperty(default=False)
	
class QuizSession(db.Model):
	quiz = db.ReferenceProperty(Quiz)
	datetime = db.DateTimeProperty(auto_now_add=True)
	quizzer = db.UserProperty(auto_current_user_add=True)
	answers = db.ListProperty(db.Key)
	completed = db.BooleanProperty(default=False)
	percentscore = db.IntegerProperty()

class QuizSessionAnswer(db.Model):
	quizzer = db.UserProperty(auto_current_user_add=True)
	answer = db.StringProperty()
	correct = db.BooleanProperty(default=False)
	duration = db.IntegerProperty()