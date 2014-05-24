#!/usr/bin/python
 
import pytumblr
import yaml
import os
import urlparse
import code
import oauth2 as oauth
import webbrowser

print 'imported libraries successfully.'

#<Taken from demo project>
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

if __name__ == '__main__':
    yaml_path = os.path.expanduser('~') + '/.tumblr'
	
    if not os.path.exists(yaml_path):
        tokens = new_oauth(yaml_path)
    else:
        yaml_file = open(yaml_path, "r")
        tokens = yaml.safe_load(yaml_file)
        yaml_file.close()
	
    client = pytumblr.TumblrRestClient(
									   tokens['consumer_key'],
									   tokens['consumer_secret'],
									   tokens['oauth_token'],
									   tokens['oauth_token_secret']
									   )
#</Taken from demo project>								   
    print 'pytumblr client created.'

#Now that we're up and running, it's time to start getting our information

#get all of the blogs followed by the client 
#We can only get 20 at a time, as per the API, so we need to loop it all in
totalBlogs = client.following()['total_blogs']
loopOffset = 0
blogs = []
print("Getting blogs followed")
while loopOffset < totalBlogs:
	blogs += client.following(offset = loopOffset)['blogs']
	loopOffset += 20

#Notify the user which index maps to which blog
for x in range(len(blogs)):
	print(str(x) + ": " + blogs[x]['url'])

try:
	blogIndex = int(raw_input("Select target blog index (number only):"))
	target = blogs[blogIndex]
	targetName = str(blogs[blogIndex]['name'])

except(IndexError):
	while True:
		blogIndex = int(raw_input("Incorrect index. Please select 0-" + str(len(blogs) - 1) + ":"))
		if blogIndex > 0 and blogIndex < len(blogs):
			break #They got it right

#TODO make more efficient
#redefine target and targetName in case they weren't defined by user error
target = blogs[blogIndex]
targetName = str(blogs[blogIndex]['name'])

print 'Target blog is ' + target['url']
targetPhotoPosts = client.posts(target['name'],'photo', limit = 50)

print 'total posts to sort through: ', targetPhotoPosts['total_posts']
allPhotoPosts = []
targetPhotoPosts = targetPhotoPosts['total_posts'] #all of the photos we have to look through.
loopOffset = 0
i = 0

#Since we can only get 50 photos at a time, we need to use a loop.
while(loopOffset < targetPhotoPosts):
	try:
		tempList = client.posts(target['name'],'photo', limit = 50, offset = loopOffset, reblog_info = 'true')['posts']
		for post in tempList:
			print 'post ', i ,' id:',post['id']
			i+=1
		allPhotoPosts += tempList
		loopOffset += 50
	except(KeyError):
		#Do nothing, try again
		print("Another go!")

print 'length: ', len(allPhotoPosts)

totalCandidates = 0
i=0
writeFile = raw_input("Do you want to write a file of the results? ('y'/'n')") == "y"
if writeFile:
	outfile = open(raw_input("what's the name you want?:") + ".txt",'w')
else:
	outfile = open(os.devnull,'w')

openAllInBrowser = raw_input("Do you want to view all results (including questionable ownership posts) in the browser? ('y'/'n')") == "y"
if openAllInBrowser:
	openCandidatesInBrowser = False
else:
	openCandidatesInBrowser = raw_input("\tWhat about positive results in browser?") == "y"

for post in allPhotoPosts:
	try:
		temp = post['reblogged_root_name'] #fails if ownership cannot be determined
		if(temp == targetName):
			try:
				print i, ': Candidate: ',post['short_url'], ' notes count: ', post['note_count']
			except(KeyError):
				print i, ': Candidate: ',post['short_url'], ' notes count:?'
			
			if writeFile:
				print >> outfile, post['post_url']
			if (openAllInBrowser or openCandidatesInBrowser):
				webbrowser.open_new_tab(post['image_permalink'])
			elif openCandidatesInBrower:
				webbrowser.open_new_tab(post['image_permalink'])
			totalCandidates += 1
			i+=1
	except(KeyError):
		try:
			print i, ': No Owner: ',post['short_url'], ' notes count: ', post['note_count']
		except(KeyError):
			print i, ': No Owner: ',post['short_url'], ' notes count: ?'
		if writeFile:
			print >> outfile, post['post_url']
		if openAllInBrowser:
			webbrowser.open_new_tab(post['image_permalink'])	
		i+=1

print 'Total candidates: ', totalCandidates
outfile.close()
