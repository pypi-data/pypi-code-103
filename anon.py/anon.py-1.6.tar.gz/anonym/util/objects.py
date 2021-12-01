class UserProfileList:
    def __init__(self, responseData: list):
        self.uid = []
        self.nickname = []
        self.login = []
        for user in responseData:
            self.uid.append(user["id"])
            self.nickname.append(user["name"])
            self.login.append(user["login"])


class PostList:
    def __init__(self, responseData: list):
        self.id = []
        self.viewCount = []
        self.text = []
        self.authorName = []
        self.authorId = []
        for post in responseData:
            self.id.append(post["id"])
            self.viewCount.append(post["postviews"]["count"])
            self.text.append(post["text"])
            self.authorName.append(post["owner_name"])
            self.authorId.append(post["owner_id"])