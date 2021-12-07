import logging
from typing import List, Optional, Tuple
import re

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.apps import apps

logger = logging.getLogger(__name__)


class Statement(models.Model):
    """
    This model represents an statement of an specific account.
    """
    author = models.ForeignKey('the_social_network.Account', on_delete=models.CASCADE)
    content = models.CharField(max_length=120, blank=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # Add an hashtag between statements and hashtags  over the tagging model
    tagged = models.ManyToManyField('Hashtag',
                                    blank=True,
                                    through='HashtagTagging',
                                    symmetrical=False,
                                    related_name='tags',
                                    default=None)
    mentioned = models.ManyToManyField('the_social_network.Account',
                                       blank=True,
                                       through='AccountTagging',
                                       symmetrical=False,
                                       related_name='mentions',
                                       default=None)
    reactions = models.ManyToManyField('self',
                                       blank=True,
                                       through='Reaction',
                                       symmetrical=False,
                                       related_name='reaction_of',
                                       default=None)

    def __str__(self):
        return "{author} says: {content}".format(author=self.author.user.username, content=self.content)

    class Meta:
        ordering = ('-created',)

    def save(self, *args, **kwargs) -> None:
        """
        This method adds hashtags relations after the statement is saved.
        Save is ran after update or create.

        :param args: Not used.
        :param kwargs: Not used.
        :return: None
        """
        super(Statement, self).save(*args, **kwargs)
        # resolve hashtags after saving the statement
        used_hashtags: List[str] = self.__extract_hashtags()
        for used_hashtag in used_hashtags:
            result: Tuple[Hashtag, bool] = Hashtag.objects.get_or_create(tag=used_hashtag)
            hashtag: Hashtag = result[0]
            self.add_hashtag(hashtag=hashtag)
        used_mentions: List[str] = self.__extract_mentioning()
        # resolve mentions after saving the statement
        for used_mention in used_mentions:
            account: 'the_social_network.Account' = apps.get_model("the_social_network", "Account").objects.filter(
                user__username=used_mention).first()
            if account:
                self.add_mentioning(account=account)

    def add_reaction(self, reaction_statement: 'Statement', vote: int) -> Tuple['Reaction', bool]:
        """
        This method adds an reaction to the calling statement.
        :param reaction_statement:  The statement to be added as an reaction.
        :param vote: The vote of the reaction regarding the parent element. (Like 1, Dislike 0)
        :return: The reaction as well as the status if the reaction was already existing.
        """
        reaction, created = Reaction.objects.get_or_create(
            parent=self,
            child=reaction_statement,
            vote=vote
        )
        return reaction, created

    def remove_as_reaction(self) -> bool:
        """
        This method removes the calling statement as an reaction for the parent.
        :return: Status if the reaction was deleted or not.
        """
        deleted, _ = Reaction.objects.filter(child=self).delete()
        return deleted

    def get_reactions(self) -> List['Reaction']:
        """
        This method returns all reaction of the calling statement.
        :return: List of all reactions to the calling statement
        """
        return list(Reaction.objects.filter(parent=self))

    def get_reaction_to_parent(self) -> Optional[List['Reaction']]:
        """
        This method returns the reaction relation to the parent if this statement is used as an reaction.
        :return: Reaction to the parent if there is one. Else none.
        """
        reaction: List[Reaction] = Reaction.objects.filter(child=self)
        if len(reaction) == 0:
            return None
        # todo: is there a way to use the instance and not a list in the reaction serialize, if so, also change frontend
        return reaction

    def get_parent(self) -> Optional['Statement']:
        """
        This method is for getting the parent if of an statement if this statement is an reaction.
        :return: The parent statement of the reaction. If there is no parent then None is returned.
        """
        parents: List['Statement'] = self.reaction_of.all()
        if len(parents) == 0:
            return None
        return parents[0]

    def __extract_hashtags(self) -> List[str]:
        """
        This method extracts the hashtag of the content.
        Hashtags are alpha numeric words.

        :return: List of all hashtags used in the content of the statement.
        """
        return re.findall(r"#(\w+)", self.content)

    def add_hashtag(self, hashtag: 'Hashtag'):
        """
        This method is for adding an hashtag to the corresponding statement.
        :param hashtag: The hashtag to be added.
        :return: True if the hashtag was created, false otherwise.
        """
        tagging, created = HashtagTagging.objects.get_or_create(statement=self, hashtag=hashtag)
        return created

    def get_hashtags(self) -> List['Hashtag']:
        """
        This method is to get all hashtags of the calling statement.

        :return: List of all hashtags of the calling statement.
        """
        return list(self.tagged.all())

    def remove_hashtag(self, hashtag: 'Hashtag'):
        """
        This method is used to delete an specific hashtag for the calling statement.

        :param hashtag: The hashtag to be deleted.
        :return: True if the hashtag was deleted, false else.
        """
        deleted: bool = HashtagTagging.objects.filter(
            statement=self,
            hashtag=hashtag
        ).delete()
        return deleted

    def __extract_mentioning(self) -> List['the_social_network.Account']:
        """
        This method extracts the mentions of accounts in the calling statement.
        Accounts names are alpha numeric words.

        :return: List of all accounts mentioned in the calling statement.
        """
        return re.findall(r"@(\w+)", self.content)

    def add_mentioning(self, account: 'the_social_network.Account'):
        """
        This method is for adding an mention of an account to the corresponding statement.
        :param account: The account to be mentioned.
        :return: True if the mention was created, false otherwise.
        """
        mentioning, created = AccountTagging.objects.get_or_create(statement=self, account=account)
        return created

    def get_mentioning(self) -> List['the_social_network.Account']:
        """
        This method is to get all accounts mentioned by the calling statement.

        :return: List of all accounts mentioned by the calling statement.
        """
        return list(self.mentioned.all())

    def remove_mentioning(self, account: 'the_social_network.Account'):
        """
        This method is used to delete an specific mentioning of an account for the calling statement.

        :param account: The account to be unmentioned.
        :return: True if the hashtag was deleted, false else.
        """
        deleted: bool = AccountTagging.objects.filter(
            statement=self,
            account=account
        ).delete()
        return deleted





class Hashtag(models.Model):
    """
    This model represents an hashtag which can be added to specific contents.
    """
    tag = models.CharField(max_length=30, blank=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "#{tag}".format(tag=self.tag)


class Tagging(models.Model):
    """
    This model represents the relation between any type of content and an hashtag
    """
    # What is the corresponding statement?
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)
    # When was this tagging created?
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # The default manager
    objects = models.Manager()

    class Meta:
        abstract = True


class HashtagTagging(Tagging):
    """
    This model is to represent the tagging of an statement with an hashtag.
    """
    # Which hashtag should be tagged?
    hashtag = models.ForeignKey(Hashtag, related_name='hashtag', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{statement} tagged with {hashtag}".format(statement=self.statement, hashtag=self.hashtag)


class AccountTagging(Tagging):
    """
    This model is to represent the mention of an account within an statement.
    """
    # Which account should be mentioned?
    account = models.ForeignKey('the_social_network.Account', related_name='account', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{statement} mentioned {account}".format(statement=self.statement, account=self.account)


class Reaction(models.Model):
    # Who is the parent element of the reaction
    parent = models.ForeignKey(Statement, related_name='parent', on_delete=models.CASCADE)
    # Who is the reaction to the parent
    child = models.ForeignKey(Statement, related_name='child', on_delete=models.CASCADE)
    # When was this reaction created?
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # The relation must have an clear vote
    vote = models.PositiveSmallIntegerField(
        choices=[
            (1, "like"),
            (2, "dislike")
        ],
        default=1
    )
    # The default manager
    objects = models.Manager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{child_author} {reaction}s >>{parent_content}<< of {parent_author} because >>{child_content}<<".format(
            child_author=self.child.author.user.username,
            child_content=self.child.content,
            reaction=self.get_vote_display(),
            parent_content=self.parent.content,
            parent_author=self.parent.author.user.username,
        )

class Account(models.Model):
    """
    This model is for handling user accounts.
    Therefore all data regarding an user is stored in this model.
    The account is separated from the user since the default user model is used.
    """
    # Link the account to an user
    user: User = models.OneToOneField(to=User,
                                      on_delete=models.CASCADE,
                                      primary_key=True)
    # Add an relationship between accounts over the relationship model
    related_to = models.ManyToManyField('self',
                                        blank=True,
                                        through='Relationship',
                                        symmetrical=False,
                                        related_name='related_by',
                                        default=None)
    # This is the image of the account
    image = models.ImageField(upload_to='account/images',
                              default='account/default/Argunaut.png')

    biography = models.CharField(blank=False,
                                 max_length=1000,
                                 default="Hey there, nice to meet you!".format(user))

    # The default manager
    objects = models.Manager()

    def __str__(self):
        return "{username}".format(username=self.user.username)

    def add_relationship(self, account: 'Account') -> bool:
        """
        This method adds an relationship for an instance.

        :param account: Who should be added to an relation with the instance.
        :return: True if the relationship was created, false otherwise.
        """
        relationship, created = Relationship.objects.get_or_create(
            from_account=self,
            to_account=account)
        return created

    def remove_relationship(self, account: 'Account'):
        """
        This method deletes the relationship to an other Account.

        :param account: The user with whom the relationship is to be terminated.
        :return: True if the relationship was deleted, false otherwise.
        """
        deleted: bool = Relationship.objects.filter(
            from_account=self,
            to_account=account).delete()
        return deleted

    def get_related_to(self) -> List['Account']:
        """
        This method returns all accounts related to the calling instance of this method.
        Therefore this returns accounts the calling accounts relates to.

        :return: All related accounts of the calling instance.
        """
        return list(self.related_to.filter(to_account__from_account=self))

    def get_related_by(self) -> List['Account']:
        """
        This method returns all accounts who relates with the calling account.
        
        :return: All accounts who relates to the calling account.
        """
        return list(self.related_by.filter(from_account__to_account=self))

    def get_statements(self) -> List['Statement']:
        """
        This method returns all all statements made by the calling account.

        :return: All statements made by the calling account.
        """
        return list(self.statement_set.all())

    def add_statement(self, content: str) -> Statement:
        """
        This methods add a statement for the calling account.

        :param content: The content of the statement.
        :return: The added statement.
        """
        statement: Statement = Statement(author=self, content=content)
        self.statement_set.add(statement, bulk=False)
        return statement

    def update_image(self, new_image: InMemoryUploadedFile):
        """
        This method overwrites the image of an account.
        If the account uses the default image the image will not be deleted.
        :param new_image: The new image to be added for the account.
        :return: Nothing
        """
        if self.image != "account/default/Argunaut.png":
            self.image.delete(save=True)
        self.image = new_image
        self.save()

    def update_biography(self, new_biography: str):
        """
        This method overwrites the biography of an account if it is not none.
        :param new_biography: The new biography to be added for the account.
        :return: Nothing
        """
        if new_biography and self.biography != new_biography:
            self.biography = new_biography
            self.save()


class Relationship(models.Model):
    """
    This model handles relations between users.
    By using this model it is possible to create more detailed relationships.
    """
    # Who wants to have an relation?
    from_account = models.ForeignKey(Account, related_name='from_account', on_delete=models.CASCADE)
    # To whom should a relationship be established?
    to_account = models.ForeignKey(Account, related_name='to_account', on_delete=models.CASCADE)
    # When was this relation created?
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # The default manager
    objects = models.Manager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "{from_user} related to {to_user}".format(from_user=self.from_account, to_user=self.to_account)