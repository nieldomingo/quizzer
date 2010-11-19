import datetime

class PHTZ(datetime.tzinfo):
	"""
	Philippine Timezone
	"""
	
	def utcoffset(self, dt):
		return datetime.timedelta(hours=8)
		
	def tzname(self, dt):
		return "+8:00"
		
	def dst(self, dt):
		return datetime.timedelta(0)
		
phtz = PHTZ()

class UTC(datetime.tzinfo):
	
	def utcoffset(self, dt):
		return datetime.timedelta(0)
		
	def tzname(self, dt):
		return "UTC"
		
	def dst(self, dt):
		return datetime.timedelta(0)
		
utctz = UTC()