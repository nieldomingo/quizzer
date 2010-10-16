import urllib

urlbase = 'http://chart.apis.google.com/chart'

def piechart(data, labels, size='300x150', color='0000FF'):
	params = {}
	params['cht'] = 'p'
	params['chs'] = size
	params['chco'] = color
	params['chd'] = 't:' + ','.join([str(o) for o in data])
	params['chl'] = '|'.join(labels)
	maxval = max(data)
	params['chds'] = '0,%s'%maxval
	
	src = urlbase + '?' + urllib.urlencode(params)
	
	return src