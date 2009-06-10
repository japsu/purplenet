class Config(object):
	def __getattr__(self, name):
		print name
		return None
	
