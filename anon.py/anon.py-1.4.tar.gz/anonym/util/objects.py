class UserProfileList:
    def __init__(self, responseData: list):
        self.uid = []
        self.nickname = []
        self.login = []
        for user in responseData:
            self.uid.append(user["id"])
            self.nickname.append(user["name"])
            self.login.append(user["login"])