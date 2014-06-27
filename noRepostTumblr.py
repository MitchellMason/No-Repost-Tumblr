#!/usr/bin/python
#written with python version 2.7.5
print ("importing libraries")
import yaml
import os
import urlparse #needed for efficient url parsing in pytumblr
import code #standard code ops
import oauth2 as oauth #for tumblr authentication
import webbrowser #to control your web brower to open tabs
import pytumblr #obvious
from   UserString import MutableString #for string concatenation
import tempfile #for the temporary html file we make for results
print ("imported libraries successfully.")

#htmlFile
#Used to write out results to an html file and display them
class htmlFile:
	outfile = -1 #To be made into file output
	lines = []  #To be written to file
	candidates = []
	maybes = []
	blog = ""
	#constructor
	def __init__(self, blogName):
		self.outfile = tempfile.NamedTemporaryFile(delete=False, suffix = ".html")
		self.blog = blogName
	#Add a candidate post
	def addCandidate(self, url, postTitle, notes):
		tup = url, postTitle, notes
		self.candidates.append(tup)
	#Add a maybe-candidate post
	def addMaybe(self, url, postTitle, notes):
		tup = url, postTitle, notes
		self.maybes.append(tup)
	#write the post to a file and open it in a webbrowser
	def open(self):
		#add line headers
		self.lines.append("<html>")
		self.lines.append("<title>Results</title>")
		self.lines.append("<h1>Results for " + self.blog + "</h1>")
		self.lines.append("<h2>Candidates</h2>")
		self.lines.append("<table border=\"2\" style=\"width:300px\">")
		self.lines.append("<tr>")
		self.lines.append("     <th>URL:</th>")
		self.lines.append("    <th>Notes:</th>")
		self.lines.append("</tr>")
		
		#add candidates to file
		for post in self.candidates:
			self.lines.append("<tr>")
			self.lines.append("<td><a href = " + post[0] + " target=\"_blank\">"+post[1]+"</a></td>")
			self.lines.append("<td>" + post[2] + "</td>")
			self.lines.append("</tr>")
		
		self.lines.append("</table>")
		self.lines.append("<br>")
		self.lines.append("<h2>Maybe candidates</h2>")
		self.lines.append("<table border=\"2\" style=\"width:300px\">")
		self.lines.append("<tr>")
		self.lines.append("     <th>URL:</th>")
		self.lines.append("    <th>Notes:</th>")
		self.lines.append("</tr>")
		
		#add the break between candidates and maybes
		for post in self.maybes:
			self.lines.append("<tr>")
			self.lines.append("<td><a href = " + post[0] + " target=\"_blank\">"+post[1]+"</a></td>")
			self.lines.append("<td>" + post[2] + "</td>")
			self.lines.append("</tr>")
		
		self.lines.append("</tr>")
		self.lines.append("</table>")
		self.lines.append("</html>")
		
		#Throw it to the HD
		for line in self.lines:
			print >> self.outfile, line

		#finish up
		self.outfile.flush()
		#Open in the web browser
		webbrowser.open_new_tab("file://" + self.outfile.name) #works in safari so far
#end htmlFile

#new_oauth uses the o_auth module to get tumblr access
def new_oauth(yaml_path):
    '''
	Return the consumer and oauth tokens with three-legged OAuth process and
	save in a yaml file in the user's home directory.
	'''
	
    print 'Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps'
    consumer_key = raw_input('Paste the consumer key here: ')
    consumer_secret = raw_input('Paste the consumer secret here: ')
	
    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'
	
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
	
    # Get request token
    resp, content = client.request(request_token_url, "POST")
    request_token =  urlparse.parse_qs(content)
	
    # Redirect to authentication page
    print '\nPlease go here and authorize:\n%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'][0])
    redirect_response = raw_input('Allow then paste the full redirect URL here:\n')
	
    # Retrieve oauth verifier
    url = urlparse.urlparse(redirect_response)
    query_dict = urlparse.parse_qs(url.query)
    oauth_verifier = query_dict['oauth_verifier'][0]
	
    # Request access token
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'][0])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)
	
    resp, content = client.request(access_token_url, "POST")
    access_token = urlparse.parse_qs(content)
	
    tokens = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'oauth_token': access_token['oauth_token'][0],
        'oauth_token_secret': access_token['oauth_token_secret'][0]
    }
	
    yaml_file = open(yaml_path, 'w+')
    yaml.dump(tokens, yaml_file, indent=2)
    yaml_file.close()
	
    return tokens

#Prompt the user for parameters for target blog and settings
def promptUser(client):
	totalBlogs = client.following()['total_blogs']
	loopOffset = 0
	blogs = []
	print("Getting the blogs you have subscribed to")
	blogPromptPrintFormat = "{0:<" + str(len(str(totalBlogs))) + "} | {1:<}"
	
	while loopOffset < totalBlogs:
		blogs += client.following(offset = loopOffset)['blogs']
		loopOffset += 21

	#Allow the user to choose a target blog by number
	for blog in blogs:
		print(blogPromptPrintFormat.format(blogs.index(blog) + 1,blog['url']))
	blogIndex = -1 #to be assigned...
	try:
		blogIndex = int(raw_input("Select target blog index (number only):"))-1
		print("You have chosen " + blogs[blogIndex]['url'])
	
	except(IndexError):
		while blogIndex > 0 and blogIndex < totalBlogs:
			blogIndex = int(raw_input("Incorrect index. Please select 0-" + (totalBlogs - 1) + ":"))
	
	finally:	
		return blogs[blogIndex]

#Using the target blog object, find original content
def scrapeForOriginality(target):
	#Get the width and height of the console (for prettiness)
	(height,width) = os.popen('stty size', 'r').read().split()
	width  = int(width)
	height = int(height)
	
	candidates = [] #We know the blogger uploaded this
	maybes = [] #posts where ownership can't be determined
	html = htmlFile(target['name'])
	
	targetPhotoPosts = client.posts(target['name'],'photo',limit = 1)['total_posts'] #all of the photos we have to look through.
	print("Total photo posts to sort through: " + str(targetPhotoPosts))
	if targetPhotoPosts == 0:
		print("Nothing to sort through")
		return
	#index | url | notes count | isCandidate
	printFormat = "{0:<"+str(max(len(str(targetPhotoPosts)),len("index")))+"} | {1:<35} | {2:<7} | {3:^9} | {4}" 
	totalCandidates = 0
	loopOffset = 0
	i=0
	
	outfile = open(tempfile.gettempdir() + target['name'],'w')
	#write the headers for outfile	
	printOffset = len(printFormat.format("1","2","3","4",""))+3 #length of other stuff to print on line. Used in progress category
	while(loopOffset < targetPhotoPosts):
		try:
			loopTempList = client.posts(target['name'],'photo',limit=50,offset=loopOffset,reblog_info='true')['posts']
		except(KeyError):
			print("API Error...")
			continue
		for x in range(len(loopTempList)):
			#Intermittenly print the column headers
			if x % 50 == 0:
				print("_") * width
				print(printFormat.format("index","URL","notes","candidate","progress"))
			
			charsToPrint  = multiplyChar("=",int((float(x+loopOffset+1) / targetPhotoPosts) * (width-printOffset)))
			spacesToPrint = multiplyChar(" ",width - len(charsToPrint) - printOffset)
			candidacyResult = getCandidacy(loopTempList[x],target['name'])	
			
			print(printFormat.format(
			x+loopOffset + 1, 									#index(with a start of 1)
			loopTempList[x]['short_url'],		 				#url
			getNotesCount(loopTempList[x]), 					#notes
			candidacyResult,							 		#Candidacy
			"[" + charsToPrint + ">" + spacesToPrint + "]"	 	#Progress bar
			))
			
			#candidate!
			if candidacyResult == "***":
				html.addCandidate(loopTempList[x]['short_url'], loopTempList[x]['date'], getNotesCount(loopTempList[x]))
			elif candidacyResult == "??":
				html.addMaybe(str(loopTempList[x]['short_url']), loopTempList[x]['date'], str(getNotesCount(loopTempList[x])))
		loopOffset += 50
	html.open()
#end scrapeForOriginality

#multiplyChar
#returns a string appended to itself n times
def multiplyChar(char, n):
	retVal = MutableString()
	I=0
	if n == 0:
		return ""
	elif n < 0:
		return char
	for i in range(n):
		retVal += char
	return retVal
#end multiplyChar

#Gets the note count if availible, or '???'
#getNotesCount
def getNotesCount(post):
	try:
		return str(post['note_count'])
	except(KeyError):
		return "???"
#end getNotesCount

#getCandidacy
#determines the cadidacy of a post based on the bloggerName
def getCandidacy(post, bloggerName):
	try:
		if(post['reblogged_root_name'] == bloggerName):
			return "***"
		else:
			return "x"
	#this means we didn't get the info from a bad API call
	except(KeyError):
		notesCount = getNotesCount(post)
		if notesCount == "???":
			return "????"
		else:
			return "??"
		notes = [] #find way to get notes!/
#end getCandidacy

#Main
if __name__ == '__main__':
    yaml_path = os.path.expanduser('~') + '/.tumblr'	
    if not os.path.exists(yaml_path):
        tokens = new_oauth(yaml_path)
    else:
        yaml_file = open(yaml_path, "r")
        tokens = yaml.safe_load(yaml_file)
        yaml_file.close()
	client = pytumblr.TumblrRestClient(tokens['consumer_key'],tokens['consumer_secret'],tokens['oauth_token'],tokens['oauth_token_secret'])
	print('Client successfully created')
	blog = promptUser(client)
	scrapeForOriginality(blog)	
	print("Done. Thank you!")
#end Main
