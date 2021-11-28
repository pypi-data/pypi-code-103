import aiohttp

#classes
class get:
	
	def __init__(self,api):
		self.api = api
	
	#List of posts in a thread
	async def posts(self, thread_id, page_of_post_id="", post_ids="", page="", limit="", order=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?posts/&thread_id={thread_id}&page_of_post_id={page_of_post_id}&post_ids={post_ids}&page={page}&limit={limit}&order={order}", headers=headers)
			return await response.json()
	
	#Return last post
	async def last_post(self, thread_id):
		async with aiohttp.ClientSession() as session:
			result = self.posts(thread_id)['thread']['links']['last_post']
			response = await session.get(result)
			return await response.json()
	
	#Get section threads
	#через data не работает
	async def threads(self, forum_id="", thread_ids="", creator_user_id="", sticky="", thread_prefix_id="", thread_tag_id="", page="", limit="", order="", thread_create_date="", thread_update_date=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?threads/&forum_id={forum_id}&thread_ids={thread_ids}&creator_user_id={creator_user_id}&sticky={sticky}&thread_prefix_id={thread_prefix_id}&thread_tag_id={thread_tag_id}&page={page}&limit={limit}&order={order}&thread_create_date={thread_create_date}&thread_update_date={thread_update_date}", headers=headers)
			return await response.json()
	
	#Find user
	async def findUser(self, username="", user_email=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?users/find&username={username}&user_email={user_email}")
			return await response.json()
	
	#Get profile posts
	async def profilePosts(self, userid, page="", limit=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?users/{userid}/timeline", data={'page': page, 'limit': limit}, headers=headers)
	
	#Get conversations
	async def conversations(self, page="", limit=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?conversations/&page={page}&limit={limit}",headers=headers)
			return await response.json() 
	
	#Detail information of a thread
	async def threadInfo(self, page="", limit=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?threads/2430762",headers=headers)
			return await response.json() 
	
	#List of messages in a conversation
	async def conversation(self, conversation_id, page="", limit="", order="", before="", after=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?conversation-messages/",data={'conversation_id': conversation_id, 'limit': limit, 'page': page, 'order': order, 'before': before,'after': after},headers=headers)
			return await response.json() 
		
	#List of notifications
	async def notifications(self):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url="https://lolz.guru/api/index.php?notifications",headers=headers)
			return await response.json() 
	
	#List of all pages in the system
	async def pages(self, parent_page_id="", order=""):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url="https://lolz.guru/api/index.php?pages",headers=headers)
			return await response.json()
	
	#Detail information of a page
	async def pagesById(self, page_id):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?pages/{page_id}", headers=headers)
			return await response.json()

class post:
	
	def __init__(self,api):
		self.api = api
	
	#Create a new post
	async def post(self, thread_id, post_body, quote_post_id=""):
		async with aiohttp.ClientSession() as session:
			response = await session.post(url="https://lolz.guru/api/index.php?posts",data={'thread_id': thread_id, 'post_body': post_body, 'quote_post_id': quote_post_id},headers=headers)
			return await response.json()
	
	#Like post
	async def like(self, post_id):
		async with aiohttp.ClientSession() as session:
			response = await session.post(url=f"https://lolz.guru/api/index.php?posts/{post_id}/likes",headers=headers)
			return await response.json()
	
	#Profile post
	async def profilePost(self, userid, post_body, status=""):
		async with aiohttp.ClientSession() as session:
			response = await session.post(url=f"https://lolz.guru/api/index.php?users/{userid}/timeline",data={'post_body': post_body, 'status': status},headers=headers)
			return await response.json()
	
	#Sub
	async def sub(self, userid):
		async with aiohttp.ClientSession() as session:
			response = await session.post(url=f"https://lolz.guru/api/index.php?users/{userid}/followers",headers=headers)
			return await response.json()
	
	#Create a new conversation message
	async def conversation(self, conversation_id, message_body):
		async with aiohttp.ClientSession() as session:
			response = await session.post(url=f"https://lolz.guru/api/index.php?conversation-messages/&conversation_id={conversation_id}&message_body={message_body}",headers=headers)
			return await response.json()
	
	#Like a profile post
	async def likeProfilePost(self, post_id):
		async with aiohttp.ClientSession() as session:
			response = await session.post(url=f"https://lolz.guru/api/index.php?profile-posts/{post_id}/likes",headers=headers)
			return await response.json()

class delete:
	
	def __init__(self,api):
		self.api = api
	
	#Unlike post
	async def like(self, post_id):
		async with aiohttp.ClientSession() as session:
			response = await session.delete(url=f"https://lolz.guru/api/index.php?posts/{post_id}/likes",headers=headers)
			return await response.json()
	
	#Delete post
	async def post(self, post_id, reason=""):
		async with aiohttp.ClientSession() as session:
			response = await session.delete(url=f"https://lolz.guru/api/index.php?posts/{post_id}/",data={'reason': reason},headers=headers)
			return await response.json()
	
	#Delete post
	async def thread(self, thread_id, reason=""):
		async with aiohttp.ClientSession() as session:
			response = await session.delete(url=f"https://lolz.guru/api/index.php?threads/{thread_id}/&reason={reason}",headers=headers)
			return await response.json()
		
	#Delete sub
	async def sub(self, userid):
		async with aiohttp.ClientSession() as session:
			response = await session.delete(url=f"https://lolz.guru/api/index.php?users/{userid}/followers",headers=headers)
			return await response.json()
	
	#Delete a profile post
	async def profilePost(self, post_id, reason=""):
		async with aiohttp.ClientSession() as session:
			response = await session.delete(url=f"https://lolz.guru/api/index.php?profile-posts/{post_id}/&reason={reason}",headers=headers)
			return await response.json()

	#Unlike a profile post
	async def likeProfilePost(self, post_id):
		async with aiohttp.ClientSession() as session:
			response = await session.delete(url=f"https://lolz.guru/api/index.php?profile-posts/{post_id}/likes",headers=headers)
			return await response.json()

class put:
	
	def __init__(self,api):
		self.api = api
	
	#Edit message
	async def editMessage(self, message_id, message_body):
		async with aiohttp.ClientSession() as session:
			response = await session.put(url=f"https://lolz.guru/api/index.php?conversation-messages/{message_id}/&message_body={message_body}",headers=headers)
	
	#Edit a profile post
	async def profilePost(self, post_id, post_body):
		async with aiohttp.ClientSession() as session:
			response = await session.put(url=f"https://lolz.guru/api/index.php?profile-posts/{post_id}/",data={'post_body': post_body},headers=headers)

class api:
	def __init__(self, api):
		self.api = api #set api
		self.get = get(self.api)
		self.post = post(self.api)
		self.delete = delete(self.api)
		self.put = put(self.api)
		global headers
		headers = {'Authorization': f'Bearer {self.api}','Cookie': 'xf_logged_in=1'}
	
	async def getMe(self):
		async with aiohttp.ClientSession() as session:
			response = await session.get(url=f"https://lolz.guru/api/index.php?users/me",headers=headers)
			return await response.json()