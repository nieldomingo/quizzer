#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.api import memcache

from models import *

def getsubcategories(category):
	"""
	return the subcategories for a given category
	"""
	
	subcategories = memcache.get('%s_subcategries'%category)
	if not subcategories:
		subcategories = []
		query = Subcategory.all().filter('category =', category).order('name')
		for subcat in query:
			subcategories.append((subcat.subcategory, subcat.name))
		memcache.set('%s_subcategories'%category, subcategories, 3600)
		
	return subcategories
	
def refreshsubcategories(category):
	"""
	refresh the subcategories stored in memcache for the given category
	"""
	
	subcategories = []
	query = Subcategory.all().filter('category =', category).order('name')
	for subcat in query:
		subcategories.append((subcat.name, subcat.subcategory))
	memcache.set('%s_subcategories'%category, subcategories, 3600)
	
	return subcategories