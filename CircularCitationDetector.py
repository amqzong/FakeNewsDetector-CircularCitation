# CircularCitationDetector.py
# Amanda Zong

# Description: Analyzes the references of a given website and reports how trustworthy 
# it is. The detector works its way through generations of references and identifies each 
# reference chain as an independent branch or a loop that connects to another branch.
# If it finds a reference that cites the original input website, a serious error is
# reported with the message:
# 'Circular citation was detected back to original url - untrustworthy!'

# To Run: In the command line, run "python3 CircularCitationDetector.py 
# [target_url] [MAX_GEN]"

# Input arguments:
# target_url: The url to be checked.
# MAX_GEN: The maximum generation of references the detector will open and check. If
# MAX_GEN is 1, the detector will only open the input url and check its references. If
# MAX_GEN is 2, the detector will furthermore open the references of the input url
# and check the references to each of those references.

# Definitions:
# Loop: A reference that is touched by two independent chains of references forms
# a loop.
# Branch: A chain of references that ends at a unique leaf (reference).
# Miscellaneous refs: Online refs that do not start with the http or https protocol.
# Circular citation: A descendant reference of the original url that 
# cites the original url as one of its own references.
# Generation: A direct reference of the target url belongs to generation 2. A direct
# reference of a gen-2 reference belongs to generation 3, and so on and so forth.
# Source: A unique website home. i.e. https://www.nytimes.com/apples-are-great and 
# https://www.nytimes.com/cake-is-better are unique references, but have the same source,
# https://www.nytimes.com

# To do:
# - Problems with footer: 
# https://www.nytimes.com/2012/10/14/magazine/buffalo-mozzarella-craig-ramini.html?pagewanted=all,
# https://www.eater.com/2017/7/27/16021832/pizza-dipping-sauce-papa-johns-garlic-dominos-sauce

# Timing:
# About 5^MAX_GEN seconds

from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import queue
import requests

import sys

def main():
	try:
		target_url = sys.argv[1]
		MAX_GEN = int(float(sys.argv[2]))

		# max bound set in consideration of time the program takes to run
		GEN_MIN = 1
		GEN_MAX = 4

		if (MAX_GEN < GEN_MIN or MAX_GEN > GEN_MAX):
			raise MaxGenOutOfBoundsException()

		# initializes data object
		stats = URLRefData()

		stats.q.put(target_url)
		stats.gen[target_url] = GEN_MIN

		stats = classifyURL(stats, MAX_GEN)

		print(f'Number of loops: {stats.loops}')
		print(f'Number of branches: {stats.branches}')
		print(f'Number of independent sources: {len(stats.sources)}')

		print(f'Number of faulty links: {stats.faultyRefs}')
		print(f'Number of miscellaneous links: {stats.miscRefs}')

	except CircRefError:
		print('Circular citation was detected back to original url - untrustworthy!')

	except MaxGenOutOfBoundsException:
		print(f'MAX_GEN should be between {GEN_MIN} and {GEN_MAX}, inclusive.')

	except IndexError:
		print(f'Please specify a value for MAX_GEN between {GEN_MIN} \
			and {GEN_MAX}, inclusive.')

	except Exception:
		print('Input arguments are incorrectly formatted.')

def classifyURL(stats, MAX_GEN):
	# controls the queue of references to go through

	# end if there are no more references
	if (stats.q.empty()):
		return stats

	url = stats.q.get()
	print(f'Opening page: {url}')

	# end if the generation of references is beyond MAX_GEN
	if (stats.gen[url] > MAX_GEN):
		return stats

	# classifies the url as a Wikipedia reference or a general reference,
	# and passes it to the appropriate method
	parsed_url = urlparse(url)
	try:
		if (parsed_url.netloc == 'en.wikipedia.org'):
			return getRefsWiki(url, stats, MAX_GEN)
		else:
			return getRefsGeneral(url, stats, MAX_GEN)

	except CircRefError:
		raise

def getRefsWiki(url, stats, MAX_GEN):
	# scrapes references from a Wikipedia url

	try:
		page = urlopen(url)
		stats.webRefs[url] = 1
		soup = BeautifulSoup(page, 'html.parser')
	except:
		stats.faultyRefs += 1

	try:
		lastGen = stats.gen[url]
		lastCountBranches = stats.branches
		stats.tmp_descendants = {}

		# print('References to: ')
		ref = soup.find('ol', attrs = {'class':'references'})
		for i in range(0,len(ref.find_all('li'))):
			cit = ref.find_all('li')[i].find_all('span')[1]
			if (cit.find('cite', attrs = {'class':'citation web'}) is not None):
				new_url = cit.find('a')['href']

				# passes each descendant reference to method processRef
				stats = processRef(new_url, url, lastGen, stats)

		if (stats.branches > lastCountBranches):
			stats.branches -= 1 # if there are children branches, they would
			# have been counted in processRef so don't count ancestor branch

	except CircRefError:
		raise

	except Exception:
		# print('No references found for website.')
		pass
	
	return classifyURL(stats, MAX_GEN)

def getRefsGeneral(url, stats, MAX_GEN):
	# scrapes references from a non-Wikipedia url

	try:
		page = urlopen(url)
		stats.webRefs[url] = 1
		soup = BeautifulSoup(page, 'html.parser')
	except:
		stats.faultyRefs += 1

	#try:
	lastGen = stats.gen[url]
	lastCountBranches = stats.branches
	stats.tmp_descendants = {}

	# print('References to: ')

	try:
		# looks for ref links in body of text
		body = soup.find_all('p')
		for p in body:
			#print(p)
			#print(validText(p.get_text(strip=True)))
			if (p.get_text() is not None and validText(p.get_text(strip=True))):
				stats = processDescendantRefs(p, url, lastGen, stats)

		# looks for ref links section
		for element in soup.find_all(class_ = True):
			for value in element['class']:
				ind = 0
				while (ind < len(stats.BUZZWORDS) and stats.BUZZWORDS[ind] not in value):
					ind += 1

				if (ind < len(stats.BUZZWORDS)):
					#print("Ref class? " + value)
					for sec in soup.find_all('div', attrs = {'class':value}):
						#print(sec)
						stats = processDescendantRefs(sec, url, lastGen, stats)

		for element in soup.find_all(id_ = True):
			for value in element['id']:
				ind = 0
				while (ind < len(stats.BUZZWORDS) and stats.BUZZWORDS[ind] not in value):
					ind += 1

				if (ind < len(stats.BUZZWORDS)):
					#print("Ref class? " + value)
					for sec in soup.find_all('div', attrs = {'id':value}):
						#print(sec)
						stats = processDescendantRefs(sec, url, lastGen, stats)

		if (stats.branches > lastCountBranches):
			stats.branches -= 1 # prevent overcounting of branches

	except CircRefError:
		raise

	except Exception:
		# print('No references found for website.')
		pass

	return classifyURL(stats, MAX_GEN)
	
def processDescendantRefs(sec, ancestor, lastGen, stats):
	try:
		for link in sec.find_all('a', href = True):
			new_url = link['href']

			stats = processRef(new_url, ancestor, lastGen, stats)

		return stats
	except CircRefError:
		raise

def processRef(url, ancestor, lastGen, stats):
	# checks whether the url is a valid reference: if so, adds to queue

	try:
		# if url.split('http') > 1 and the first item in the list is not empty, 
		# it is a page in an archive, should append previous url netloc to the 
		# begnning of the reference
		if (urlparse(url).scheme == ''):
			if (url.split('http')[0] != ''):
				sourceScheme = 'http'
			else:
				sourceScheme = 'https'
			if (len(url.split(sourceScheme)) > 1):
				url = urlparse(ancestor).scheme + "://" + urlparse(ancestor).netloc + url
				source_url = sourceScheme + url.split(sourceScheme)[-1]
		else:
			source_url = urlparse(url).netloc

		# print(url)

		# if this reference was already cited by the same ancestor, ignore reference
		if url in stats.tmp_descendants:
			print('Reference was already counted in this url.')
			return stats
		else:
			stats.tmp_descendants[url] = 1

		# if reference is a pdf, ignore reference
		h = requests.head(url)
		if 'application/pdf' in h.headers.get('content-type'):
			# print('Ignored pdf ref.')
			stats.miscRefs += 1
			return stats

		# if reference contains red herring words, ignore reference
		ind = 0
		validRef = True
		while (validRef and ind < len(stats.REDHERRINGS)):
			if stats.REDHERRINGS[ind] in url:
				validRef = False
			ind += 1

		if (not validRef):
			# print('Found a red herring link.')
			return stats

		# if reference does not start with recognized protocol, ignore reference
		if (urlparse(url).scheme == ''):
			# no http or https found in the url
			# print('Website does not start with recognized protocol.')
			stats.miscRefs += 1

		# if reference was already cited not by this ancestor but in a different branch,
		# a loop has been detected
		elif (url in stats.webRefs):
			if (stats.gen[url] == GEN_MIN):
				raise CircRefError('Circular Reference') 

			# print('URL ALREADY EXISTED.')
			stats.webRefs[url] += 1
			stats.loops += 1

		# if reference is valid and has not been already cited, add to queue
		else:
			if (source_url not in stats.sources):
				stats.sources[source_url] = 1
			else:
				stats.sources[source_url] += 1

			stats.webRefs[url] = 1
			stats.q.put(url)
			stats.gen[url] = lastGen + 1
			stats.branches += 1

	except:
		# print('Exception occurred: Faulty ref.')
		return stats

	return stats

def validText(s):
	# Checks whether this paragraph contains article content based on:
	# string size, number of spaces per string length, number of punctuation marks
	# per string length

	MIN_CHAR_PER_WORD = 4
	MAX_CHAR_PER_WORD = 10
	MIN_WORDS_PER_SENT = 10
	MAX_WORDS_PER_SENT = 30

	MIN_CHAR_PER_SENT = MIN_CHAR_PER_WORD * MIN_WORDS_PER_SENT
	MAX_CHAR_PER_SENT = MAX_CHAR_PER_WORD * MAX_WORDS_PER_SENT

	numPunc = s.count('.') + s.count('?') + s.count('!')

	# print(f'Number of spaces is {s.count(" ")}')
	# print(f'Number of punc is {numPunc}')
	# print(f'Length of string is {len(s)}.')
	# print(f'Avg chars per word  is {len(s)/s.count(" ")}')
	# print(f'Average char per sentence is {len(s)/numPunc}.')

	if (s.count(' ') == 0 or
		numPunc == 0 or
		len(s)/s.count(' ')< MIN_CHAR_PER_WORD or
		len(s)/s.count(' ')> MAX_CHAR_PER_WORD or
		len(s)/numPunc < MIN_CHAR_PER_SENT or
		len(s)/numPunc > MAX_CHAR_PER_SENT):
		return False

	return True

class URLRefData(object):
	# Stores data about the references of a target url

	def __init__(self):
		self.webRefs = {} # stores unique urls
		self.sources = {} # stores unique sources
		self.gen = {} 
		# matches a unique url with its generation number in relation to the original url
		self.q = queue.Queue()
		# queue of references not yet traversed

		self.loops = 0
		self.branches = 0
		self.faultyRefs = 0
		self.miscRefs = 0

		self.tmp_descendants = {}

		# will search for any BUZZWORDS in getRefsGeneral to find refs 
		# will disregard reference if it contains any REDHERRINGS in the url
		self.BUZZWORDS = ['bibliography', 'citation', 'cited', 'reference']
		self.REDHERRINGS = ['aboutus', 'author', 'subscribe', 'subscription', 'terms']

class CircRefError(Exception):
	pass

class MaxGenOutOfBoundsException(Exception):
	pass

if __name__ == '__main__':
    main()