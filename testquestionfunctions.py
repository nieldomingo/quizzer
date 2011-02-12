#!/usr/bin/env python

from models import *

def makeQuestion(category, subcategory, categoryname, index):
	question = "Lorem ipsum est ad kasd meliore, at vim facilis eloquentiam, ex est elit utamur dissentiet. Ne usu tollit laoreet, fabulas posidonium duo no. Cum quaeque consequuntur at. Qui ei eius interesset. Novum consectetuer vel eu, has admodum inciderint te."
	answer = "100"
	q = Question(questiontype=1, question='%s %s'%(categoryname, index) + question, answer=answer, category=category, subcategory=subcategory)
	q.put()