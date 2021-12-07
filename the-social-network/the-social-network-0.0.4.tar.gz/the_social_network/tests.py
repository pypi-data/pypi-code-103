from typing import List

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from .models import Account, Statement, Hashtag, Reaction

class TestAccounts(TestCase):

    def setUp(self):
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.user_beate = User.objects.create_user(username="Beate", email="Rote@Beate.de", password="Rote")

        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)
        self.account_beate: Account = Account.objects.create(user=self.user_beate)

    def clear_up_users(self, users: 'list[User]'):
        for user in users:
            user.delete()
            try:
                user_exists = User.objects.get(username=user.username)
            except Exception as exception:
                user_exists = None
            self.assertIsNone(user_exists)
        # check if the accounts are also removed if the user is deleted
        for user in users:
            try:
                account_exists = Account.objects.get(user=user)
            except Exception as exception:
                account_exists = None
            self.assertIsNone(account_exists)

    def tearDown(self):
        self.clear_up_users([self.user_beate, self.user_bernd])

    def test_account_can_follow_accounts(self):
        self.assertIsNotNone(self.account_bernd)
        self.assertIsNotNone(self.account_beate)
        self.assertFalse(self.account_bernd.related_to.all().exists())
        self.assertFalse(self.account_beate.related_to.all().exists())

        created: bool = self.account_beate.add_relationship(self.account_bernd)
        self.assertTrue(created)
        # Beate should have an relationship to Bernd
        beates_relations = self.account_beate.related_to.all()
        self.assertEqual(beates_relations[0], self.account_bernd)
        # But Bernd should not have an relationship to Beate
        self.assertFalse(self.account_bernd.related_to.all().exists())

    def test_account_can_unfollow_accounts(self):
        self.test_account_can_follow_accounts()
        deleted: bool = self.account_beate.remove_relationship(self.account_bernd)
        # Beate can delete her relationships
        self.assertTrue(deleted)
        self.assertFalse(self.account_beate.related_to.all().exists())

    def test_accounts_provide_related_accounts(self):
        self.test_account_can_follow_accounts()
        related_accounts_of_beate: List[Account] = self.account_beate.get_related_to()
        related_accounts_of_bernd: List[Account] = self.account_bernd.get_related_to()
        # there are results for the relationships for beate but not for bernd
        self.assertIsNotNone(related_accounts_of_beate)
        self.assertIsNotNone(related_accounts_of_bernd)
        self.assertEqual(related_accounts_of_bernd, [])
        # Beate has relation to Bernd
        self.assertEqual(related_accounts_of_beate[0], self.account_bernd)

    def test_accounts_can_provides_accounts_who_relates_with_them(self):
        self.test_account_can_follow_accounts()
        accounts_relating_to_beate: List[Account] = self.account_beate.get_related_by()
        accounts_relating_to_bernd: List[Account] = self.account_bernd.get_related_by()
        # Beate only relates to Bernd
        self.assertEqual([], accounts_relating_to_beate)
        self.assertNotEqual([], accounts_relating_to_bernd)


class TestGetAccount(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.user_beate = User.objects.create_user(username="Beate", email="Rote@Beate.de", password="Rote")
        self.token_bernd = Token.objects.create(user=self.user_bernd)
        self.token_beate = Token.objects.create(user=self.user_beate)

        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)
        self.account_beate: Account = Account.objects.create(user=self.user_beate)

    def test_own_account_provides_own_data(self):

        created: bool = self.account_beate.add_relationship(self.account_bernd)
        self.assertTrue(created)
        # Beate should have an relationship to Bernd
        beates_relations = self.account_beate.related_to.all()
        self.assertEqual(beates_relations[0], self.account_bernd)
        # But Bernd should not have an relationship to Beate
        self.assertFalse(self.account_bernd.related_to.all().exists())

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/accounts/show/own/")

        # public information about beate
        self.assertEqual(response.data[0]["user"]["username"], self.user_beate.username)
        self.assertEqual(response.data[0]["user"]["id"], self.user_beate.id)

        # public information about the account she is relates to
        self.assertEqual(response.data[0]["related_to"][0]["user"]["username"], self.user_bernd.username)
        self.assertEqual(response.data[0]["related_to"][0]["user"]["id"], self.user_bernd.id)

        # public information about the account who relates to her
        self.assertEqual(response.data[0]["related_by"], [])

        # what do we know about bernd
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_bernd))
        response: Response = self.client.get(path="/accounts/show/own/")

        # public information about bernd
        self.assertEqual(response.data[0]["user"]["username"], self.user_bernd.username)
        self.assertEqual(response.data[0]["user"]["id"], self.user_bernd.id)

        # public information about the accounts who relates to Bernd
        self.assertEqual(response.data[0]["related_by"][0]["user"]["username"], self.user_beate.username)
        self.assertEqual(response.data[0]["related_by"][0]["user"]["id"], self.user_beate.id)

        # public information about the account Bernd relates to
        self.assertEqual(response.data[0]["related_to"], [])

        # Bernd adds an statement
        self.account_bernd.add_statement("I like Beate")
        # what do we know about Bernd
        response: Response = self.client.get(path="/accounts/show/{}/".format(self.user_bernd.id))
        self.assertEqual(response.data[0]["statements"][0]["content"], "I like Beate")

    def test_account_provide_public_data(self):
        created: bool = self.account_beate.add_relationship(self.account_bernd)
        self.assertTrue(created)
        # Beate should have an relationship to Bernd
        beates_relations = self.account_beate.related_to.all()
        self.assertEqual(beates_relations[0], self.account_bernd)
        # But Bernd should not have an relationship to Beate
        self.assertFalse(self.account_bernd.related_to.all().exists())

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_bernd))
        response: Response = self.client.get(path="/accounts/show/{}/".format(self.user_beate.id))

        # public information about beate
        self.assertEqual(response.data[0]["user"]["username"], self.user_beate.username)
        self.assertEqual(response.data[0]["user"]["id"], self.user_beate.id)

        # public information about the account she is relates to
        self.assertEqual(response.data[0]["related_to"][0]["user"]["username"], self.user_bernd.username)
        self.assertEqual(response.data[0]["related_to"][0]["user"]["id"], self.user_bernd.id)
        self.assertFalse(response.data[0]["is_friend"])

        # what do we know about bernd
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/accounts/show/{}/".format(self.user_bernd.id))

        # public information about bernd
        self.assertEqual(response.data[0]["user"]["username"], self.user_bernd.username)
        self.assertEqual(response.data[0]["user"]["id"], self.user_bernd.id)

        # public information about the account Bernd relates to
        self.assertEqual(response.data[0]["related_to"], [])
        self.assertTrue(response.data[0]["is_friend"])

        # Bernd adds an statement
        self.account_bernd.add_statement("I like Beate")
        # what do we know about Bernd
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/accounts/show/{}/".format(self.user_bernd.id))
        self.assertEqual(response.data[0]["statements"][0]["content"], "I like Beate")

    def clear_up_users(self, users: 'list[User]'):
        for user in users:
            user.delete()
            try:
                user_exists = User.objects.get(username=user.username)
            except Exception as exception:
                user_exists = None
            self.assertIsNone(user_exists)
        # check if the accounts are also removed if the user is deleted
        for user in users:
            try:
                account_exists = Account.objects.get(user=user)
            except Exception as exception:
                account_exists = None
            self.assertIsNone(account_exists)

    def tearDown(self):
        self.clear_up_users([self.user_beate, self.user_bernd])


class TestObtainingAToken(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="Rudiger", email="Rudiger@Dog.com", password="Rudiger")
        self.user.save()

    def tearDown(self):
        self.user.delete()
        try:
            user = User.objects.get(username="Rudiger")
        except Exception as exception:
            user = None
        self.assertIsNone(user)

    def test_valid_user_obtains_token(self):
        response: Response = self.client.post(path="/authentication/obtain/", data={
            "username": "Rudiger",
            "password": "Rudiger"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("token" in response.data.keys())
        self.assertIsNotNone(response.data["token"])

    def test_invalid_user_does_not_obtains_token(self):
        response: Response = self.client.post(path="/authentication/obtain/", data={
            "username": "Klaus",
            "password": "Klaus"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestValidateAToken(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="Rudiger", email="Rudiger@Dog.com", password="Rudiger")
        self.user_token = Token.objects.create(user=self.user)

    def tearDown(self):
        self.user.delete()
        try:
            user = User.objects.get(username="Rudiger")
        except Exception as exception:
            user = None
        self.assertIsNone(user)

    def test_invalid_user_cant_validate_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'Invalid Token')
        response: Response = self.client.get(path="/authentication/validate/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_valid_user_can_validate_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_token))
        response: Response = self.client.get(path="/authentication/validate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestRegistration(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_everything_is_missing(self):
        response: Response = self.client.post(path="/authentication/register/", data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0].code, "required")
        self.assertEqual(response.data["password"][0].code, "required")
        self.assertEqual(response.data["email"][0].code, "required")

    def test_everything_is_empty(self):
        response: Response = self.client.post(path="/authentication/register/", data={
            "username": "",
            "email": "",
            "password": ""
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0].code, "blank")
        self.assertEqual(response.data["password"][0].code, "blank")
        self.assertEqual(response.data["email"][0].code, "blank")

    def test_user_and_email_already_exists(self):
        user = User.objects.create_user(username="Peter", password="password", email="e@mail.de")

        response: Response = self.client.post(path="/authentication/register/", data={
            "username": "Peter",
            "password": "password",
            "email": "e@mail.de"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0].code, "unique")
        self.assertEqual(response.data["email"][0].code, "unique")

    def test_username_is_not_alphanumeric(self):
        response: Response = self.client.post(path="/authentication/register/", data={
            "username": "NoWay%&/\/8)(?=!"'``´',
            "password": "password",
            "email": "e@mail.de"
        })
        self.assertEqual(response.data["username"][0].code, "invalid")

    def test_register_valid_user(self):
        response: Response = self.client.post(path="/authentication/register/", data={
            "username": "another_user100",
            "password": "another_password",
            "email": "another_e@mail.de"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        token_user: User = Token.objects.get(key=response.data["token"]).user
        user: User = User.objects.get(username="another_user100")
        account: Account = Account.objects.get(user=user)
        self.assertIsNotNone(account)
        self.assertEqual(account.user, user)
        self.assertEqual(token_user, user)


class TestLogin(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="Bernd", email="Bernd@Brot.com", password="Brot")
        self.user.save()

    def test_valid_user_can_login(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Bernd", "password": "Brot"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user: User = Token.objects.get(key=response.data["token"]).user
        self.assertEqual(self.user, user)
        user: User = authenticate(username="Bernd", password="Brot")
        self.assertIsNotNone(user)

    def test_token_gets_refreshed_after_new_login(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Bernd", "password": "Brot"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token_old: Token = Token.objects.get(key=response.data["token"])
        self.assertIsNotNone(token_old)

        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Bernd", "password": "Brot"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token_new: Token = Token.objects.get(key=response.data["token"])
        self.assertIsNotNone(token_new)

        self.assertNotEqual(token_old, token_new)

    def test_user_can_not_login_with_wrong_username(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Berndy", "password": "Brot"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0].code, "invalid")

    def test_user_can_not_login_with_wrong_password(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Bernd", "password": "Brötchen"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0].code, "invalid")

    def test_user_can_not_login_without_username(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "password": "Brot"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0].code, "required")

    def test_user_can_not_login_with_empty_username(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "", "password": "Brot"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0].code, "blank")

    def test_user_can_not_login_without_password(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Bernd"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0].code, "required")

    def test_user_can_not_login_with_empty_password(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Bernd", "password": ""
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0].code, "blank")

    def tearDown(self):
        self.user.delete()
        try:
            user = User.objects.get(username="Bernd")
        except Exception as exception:
            user = None
        self.assertIsNone(user)


class TestLogout(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="Beate", email="Rote@Beate.com", password="Rote")
        self.user.save()

    def test_valid_user_can_logout(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Beate", "password": "Rote"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token: Token = Token.objects.get(key=response.data["token"])
        user: User = token.user
        self.assertEqual(self.user, user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
        response: Response = self.client.post(path="/authentication/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token: Token = Token.objects.filter(user=user).first()
        self.assertIsNone(token)

    def test_valid_user_can_not_logout_twice(self):
        response: Response = self.client.post(path="/authentication/login/", data={
            "username": "Beate", "password": "Rote"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user: User = Token.objects.get(key=response.data["token"]).user
        token: Token = Token.objects.get(key=response.data["token"])
        self.assertEqual(self.user, user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
        response: Response = self.client.post(path="/authentication/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token: Token = Token.objects.filter(user=user).first()
        self.assertIsNone(token)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
        response: Response = self.client.post(path="/authentication/logout/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        self.user.delete()
        try:
            user = User.objects.get(username="Rote")
        except Exception as exception:
            user = None
        self.assertIsNone(user)


class TestStatement(TestCase):
    def setUp(self):
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)

        self.user_beate = User.objects.create_user(username="Beate", email="Rote@Beate.de", password="Beate")
        self.account_beate: Account = Account.objects.create(user=self.user_beate)

        self.statement: Statement = Statement.objects.create(author=self.account_bernd, content="I like Beate")
        self.statement_with_hashtags_and_mentioning: Statement = Statement.objects.create(author=self.account_bernd,
                                                                                          content="I like #eating the #/&%! whopper #Burger_King2020 with @Beate @NoOne")
        self.hashtag: Hashtag = Hashtag.objects.create(tag="Burger_King2020")

    def test_statement_can_mention_account(self):
        created = self.statement.add_mentioning(self.account_beate)
        self.assertTrue(created)
        mentions = self.statement.get_mentioning()
        self.assertNotEqual(mentions, [])
        self.assertEqual(mentions[0], self.account_beate)
        deleted = self.statement.remove_mentioning(self.account_beate)
        self.assertTrue(deleted)
        mentions = self.statement.get_mentioning()
        self.assertEqual(mentions, [])

    def test_account_has_statement_from_database(self):
        statements: List[Statement] = self.account_bernd.get_statements()
        self.assertNotEqual(statements, [])
        self.assertEqual(statements[1], self.statement)

    def test_account_can_add_statement(self):
        self.account_bernd.add_statement("I <3 burgers")
        self.assertEqual(len(self.account_bernd.get_statements()), 3)
        self.assertEqual(self.account_bernd.get_statements()[0].content, "I <3 burgers")

    def test_statement_resolves_hashtags(self):
        hashtags = self.statement_with_hashtags_and_mentioning.get_hashtags()
        self.assertEqual(len(hashtags), 2)
        self.assertEqual(hashtags[0].tag, "eating")
        self.assertEqual(hashtags[1].tag, "Burger_King2020")

    def test_statement_resolves_mentions(self):
        mentions = self.statement_with_hashtags_and_mentioning.get_mentioning()
        self.assertNotEqual(mentions, [])
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0], self.account_beate)

    def test_statement_can_add_hashtag(self):
        created = self.statement.add_hashtag(self.hashtag)
        self.assertTrue(created)

        hashtags = self.statement.get_hashtags()
        self.assertNotEqual(hashtags, [])
        self.assertEqual(self.hashtag, hashtags[0])

        deleted = self.statement.remove_hashtag(self.hashtag)
        self.assertTrue(deleted)

        hashtags = self.statement.get_hashtags()
        self.assertEqual(hashtags, [])

    def test_statement_can_add_reaction(self):
        created = self.statement.add_reaction(self.statement_with_hashtags_and_mentioning, 1)
        self.assertTrue(created)
        reactions: List[Reaction] = self.statement.get_reactions()
        self.assertEqual(len(reactions), 1)
        reaction: Reaction = reactions[0]
        self.assertEqual(reaction.get_vote_display(), "like")
        self.assertEqual(reaction.child, self.statement_with_hashtags_and_mentioning)
        deleted = self.statement_with_hashtags_and_mentioning.remove_as_reaction()
        self.assertTrue(deleted)

    def tearDown(self):
        self.user_bernd.delete()
        try:
            user_exists = User.objects.get(username=self.user_bernd.username)
        except Exception as exception:
            user_exists = None
        self.assertIsNone(user_exists)
        # check if bernds account is deleted
        try:
            account_exists = Account.objects.get(user=self.user_bernd)
        except Exception as exception:
            account_exists = None
        self.assertIsNone(account_exists)
        # check if bernds statements are deleted
        try:
            statements_exists = Statement.objects.get(user=self.user_bernd)
        except Exception as exception:
            statements_exists = None
        self.assertIsNone(statements_exists)
        try:
            hashtag_exists = Statement.objects.get(user=self.hashtag)
        except Exception as exception:
            hashtag_exists = None
        self.assertIsNone(hashtag_exists)


class TestGetStatement(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)
        self.token_bernd = Token.objects.create(user=self.user_bernd)
        self.statement_1: Statement = Statement.objects.create(author=self.account_bernd, content="I like @Bernd #Foo")
        self.statement_2: Statement = Statement.objects.create(author=self.account_bernd, content="I like Beate")

    def test_statement_provides_data(self):
        self.statement_1.add_reaction(self.statement_2, 2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_bernd))
        response: Response = self.client.get(path="/contents/statements/get/{id}/".format(id=self.statement_1.id))
        self.assertEqual(response.data[0]["id"], self.statement_1.id)
        self.assertEqual(len(response.data[0]["mentioned"]), 1)
        self.assertEqual(len(response.data[0]["tagged"]), 1)
        self.assertEqual(len(response.data[0]["reactions"]), 1)
        reaction = response.data[0]["reactions"][0]
        self.assertEqual(reaction["vote"], 2)
        self.assertEqual(reaction["child"]["id"], self.statement_2.id)
        self.assertEqual(self.statement_2.get_parent(), self.statement_1)
        self.assertIsNone(self.statement_1.get_parent())
        self.assertEqual(self.statement_2.get_reaction_to_parent()[0].vote, 2)

    def test_statements_with_hashtags_can_be_provided(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_bernd))
        response: Response = self.client.get(path="/contents/statements/with/hashtag/?q=Foo")
        self.assertTrue(len(response.data) != 0)

        self.assertEqual(response.data[0]["id"], self.statement_1.id)


class TestGetStatementFeed(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)

        self.user_beate = User.objects.create_user(username="Beate", email="Rote@Beate.de", password="Beate")
        self.account_beate: Account = Account.objects.create(user=self.user_beate)
        self.account_beate.add_relationship(self.account_bernd)
        self.token_beate = Token.objects.create(user=self.user_beate)

        self.statement_1: Statement = Statement.objects.create(author=self.account_bernd, content="I like @Bernd #Foo")
        self.statement_2: Statement = Statement.objects.create(author=self.account_bernd, content="I like Beate")
        self.statement_3: Statement = Statement.objects.create(author=self.account_beate, content="I like Bernd")
        self.statement_1.add_reaction(self.statement_2, 2)

    def test_feed_contains_correct_data(self):
        self.statement_1.add_reaction(self.statement_2, 2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/statements/feed/")
        result = response.data
        self.assertTrue(len(result), 3)
        self.assertEqual(result[0].get("id"), self.statement_3.id)
        self.assertEqual(result[1].get("id"), self.statement_2.id)
        self.assertEqual(result[2].get("id"), self.statement_1.id)
        self.assertTrue(result[0].get("id") > result[1].get("id"))
        self.assertTrue(result[0].get("created") > result[1].get("created"))
        self.assertTrue(result[1].get("id") > result[2].get("id"))
        self.assertTrue(result[1].get("created") > result[2].get("created"))
        
    def test_feed_contains_correct_data_pagination(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/statements/feed/pagination/?page=1&size=3")
        result = response.data["data"]
        result_total = response.data["total"]
        self.assertTrue(len(result), 3)
        self.assertTrue(result_total, 3)
        self.assertEqual(result[0].get("id"), self.statement_3.id)
        self.assertEqual(result[1].get("id"), self.statement_2.id)
        self.assertEqual(result[2].get("id"), self.statement_1.id)
        self.assertTrue(result[0].get("id") > result[1].get("id"))
        self.assertTrue(result[0].get("created") > result[1].get("created"))
        self.assertTrue(result[1].get("id") > result[2].get("id"))
        self.assertTrue(result[1].get("created") > result[2].get("created"))
    
    def test_feed_load_over_size_pagination(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/statements/feed/pagination/?page=1&size=4")
        result = response.data["data"]
        result_total = response.data["total"]
        self.assertTrue(len(result), 3)
        self.assertTrue(result_total, 3)
        
    def test_feed_load_under_size_pagination(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/statements/feed/pagination/?page=1&size=2")
        result = response.data["data"]
        result_total = response.data["total"]
        self.assertTrue(len(result), 2)
        self.assertTrue(result_total, 3)
        
    def test_feed_contains_no_data_pagination(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/statements/feed/pagination/?page=2&size=2")
        result = response.data["data"]
        result_total = response.data["total"]
        self.assertTrue(len(result), 0)
        self.assertTrue(result_total, 3)


class TestTrendingHashtag(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)

        self.user_beate = User.objects.create_user(username="Beate", email="Rote@Beate.de", password="Beate")
        self.account_beate: Account = Account.objects.create(user=self.user_beate)
        self.token_beate = Token.objects.create(user=self.user_beate)

    def test_trending_hashtag_is_empty(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/trending/hashtag/")
        self.assertEqual(response.data, [])

    def test_trending_hashtag_not_empty(self):
        self.statement_1: Statement = Statement.objects.create(author=self.account_bernd, content="#Foo#Bar!")
        self.statement_2: Statement = Statement.objects.create(author=self.account_beate, content="#Foo #Bar#Baz")
        self.statement_3: Statement = Statement.objects.create(author=self.account_beate,
                                                               content="I like @Beate#Foo#Baz#Bizz!")
        self.statement_1.add_reaction(self.statement_3, 2)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_beate))
        response: Response = self.client.get(path="/contents/trending/hashtag/")
        self.assertEqual(response.data[0]["count"], 3)
        self.assertEqual(response.data[0]["tag"], "Foo")
        self.assertEqual(len(response.data[0]["participants"]), 1)
        self.assertEqual(response.data[0]["participants"][0]["user"]["id"], self.user_bernd.id)
        self.assertEqual(response.data[1]["count"], 2)
        self.assertEqual(response.data[1]["tag"], "Bar")
        self.assertEqual(len(response.data[1]["participants"]), 1)
        self.assertEqual(response.data[1]["participants"][0]["user"]["id"], self.user_bernd.id)
        self.assertTrue(response.data[2]["count"], 2)
        self.assertEqual(response.data[2]["tag"], "Baz")
        self.assertEqual(len(response.data[2]["participants"]), 0)


class TestSearch(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_bernd = User.objects.create_user(username="Bernd", email="Bernd@Brot.de", password="Brot")
        self.token_bernd = Token.objects.create(user=self.user_bernd)
        self.account_bernd: Account = Account.objects.create(user=self.user_bernd)
        self.hashtag: Hashtag = Hashtag.objects.create(tag="Berg")

    def clear_up_users(self, users: 'list[User]'):
        for user in users:
            user.delete()
            try:
                user_exists = User.objects.get(username=user.username)
            except Exception as exception:
                user_exists = None
            self.assertIsNone(user_exists)
        # check if the accounts are also removed if the user is deleted
        for user in users:
            try:
                account_exists = Account.objects.get(user=user)
            except Exception as exception:
                account_exists = None
            self.assertIsNone(account_exists)

    def tearDown(self):
        self.clear_up_users([self.user_bernd])
        self.hashtag.delete()

    def test_user_can_search(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_bernd))
        response: Response = self.client.get(path="/search/?q=Ber")
        self.assertEqual(len(response.data["accounts"]), 1)
        self.assertEqual(response.data["accounts"][0]["user"]["username"], self.user_bernd.username)
        self.assertEqual(len(response.data["hashtags"]), 1)
        self.assertEqual(response.data["hashtags"][0]["tag"], self.hashtag.tag)

    def test_user_can_filter_search(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token_bernd))
        response: Response = self.client.get(path="/search/?q=Ber&filter=account")
        self.assertEqual(len(response.data["accounts"]), 1)
        self.assertEqual(response.data["accounts"][0]["user"]["username"], self.user_bernd.username)
        self.assertTrue("hashtags" not in response.data.keys())
        response: Response = self.client.get(path="/search/?q=Ber&filter=hashtag")
        self.assertEqual(len(response.data["hashtags"]), 1)
        self.assertEqual(response.data["hashtags"][0]["tag"], self.hashtag.tag)
        self.assertTrue("accounts" not in response.data.keys())
