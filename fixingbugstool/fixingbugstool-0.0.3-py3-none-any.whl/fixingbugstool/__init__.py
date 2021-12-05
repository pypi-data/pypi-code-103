import webbrowser

allsrc={'reddit':'https://www.reddit.com/search?q=python {}', 
'stackoverflow':'http://stackoverflow.com/search?q=[python] {}', 
'codeproject': 'https://www.codeproject.com/search.aspx?q=python {}&doctypeid=4', 
'stackexchange': 'https://stackexchange.com/search?q=python {}', 
'quora': 'https://www.quora.com/search?q=python {}'}

source=allsrc['stackoverflow']

def track(code):
	"""Track bugs and find solutions"""
	global source
	try:
		code()
	except Exception as e:
		webbrowser.open(source.format(str(e)))
		
def changesrc(src):
	'''change the source for the tracker'''
	global source
	try:
		source=allsrc[src]
	except:
		print("An error occurred, couldn't change the source.")
	
def sources():
	"""view all available sources"""
	global allsrc
	return list(allsrc.keys())