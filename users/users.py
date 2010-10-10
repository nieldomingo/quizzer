#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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

USERTYPES = {3: 'Quizzer', 2: 'Trainer', 1: 'Encoder'}
USERTYPES2CODE = dict([(y, x) for x, y in USERTYPES.items()])

class Unauthorized(Exception):
	pass

class Users(db.Model):
	fullname = db.StringProperty()
	user = db.UserProperty()
	usertype = db.IntegerProperty()
	
def requireusertype(*args, **kw):
	usertypes = args
	
	def _requireusertype(function):
	
		def __requireusertype(*args, **kw):
			self = args[0]
			user = users.get_current_user()
			if not user:
				self.redirect(users.create_login_url(self.request.uri))
			else:
				query = Users.all()
				query.filter('user =', user)
				suser = query.fetch(1)
				if not suser:
					self.response.out.write('Unauthorized: You are not registered as a user of this site.')
				else:
					usertypeslist = [USERTYPES2CODE[o] for o in usertypes] 
					if suser[0].usertype in usertypeslist:
						function(*args, **kw)
					else:
						self.response.out.write("Unauthorized: You don't have enough privileges to access this part of the site")
						
		return __requireusertype
		
	return _requireusertype

class MainUsersHandler(webapp.RequestHandler):
    def get(self):
    	users = Users.all()
    	users.order('fullname')
    	
    	lusers = []
    	for user in users:
    		d = {}
    		d['fullname'] = user.fullname
    		d['email'] = user.user.email()
    		d['type'] = USERTYPES[int(user.usertype)]
    		d['key'] = user.key()
    		lusers.append(d)
    
    	path = os.path.join(os.path.dirname(__file__), 'users.html')
    	self.response.out.write(template.render(path, dict(users=lusers)))
    	
class AddUserHandler(webapp.RequestHandler):
    def get(self):
    	path = os.path.join(os.path.dirname(__file__), 'adduser.html')
    	self.response.out.write(template.render(path, {}))
    	
    def post(self):
    	fullname = self.request.get('fullname')
    	email = self.request.get('email')
    	usertype = self.request.get('usertype')
    	
    	if email and usertype and fullname:
    		user = users.User(email=email)
    		u = Users(user=user, usertype=int(usertype), fullname=fullname)
    		u.put()
    		
    	self.redirect('./')
    	
class EditUserHandler(webapp.RequestHandler):
    def get(self):
    	key = self.request.get('key')
    	user = db.get(db.Key(key))
    	path = os.path.join(os.path.dirname(__file__), 'edituser.html')
    	self.response.out.write(template.render(path, dict(usertypes=USERTYPES.items(), user=user)))
    	
    def post(self):
    	key = self.request.get('key')
    	user = db.get(db.Key(key))
    	fullname = self.request.get('fullname')
    	usertype = self.request.get('usertype')
    	
    	if usertype and fullname:
    		user.usertype = int(usertype)
    		user.fullname = fullname
    		user.put()
    		
    	self.redirect('./')
    	
class DeleteUserHandler(webapp.RequestHandler):
    def get(self):
    	key = self.request.get('key')
    	user = db.get(db.Key(key))
    	
    	user.delete()
    	
    	self.redirect('./')

def main():
	application = webapp.WSGIApplication([('/users/', MainUsersHandler),
										  ('/users/adduser', AddUserHandler),
										  ('/users/edituser', EditUserHandler),
										  ('/users/deleteuser', DeleteUserHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()