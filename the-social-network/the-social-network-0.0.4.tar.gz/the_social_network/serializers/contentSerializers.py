from typing import OrderedDict

from django.apps import apps
from django.db.models import QuerySet
from rest_framework import serializers

from ..models import Account, Statement, Hashtag, Reaction, HashtagTagging
from ..serializers.authenticationSerializers import UserPublicSerializer


class HashtagSerializer(serializers.ModelSerializer):
    """
    This serializer can be used to serialize hashtags.
    """

    class Meta:
        model = Hashtag
        fields = ("id", "tag",)


class TrendingHashtagSerializer(HashtagSerializer):
    """
    This serializer is for the serialization of trending hashtags.
    In addition to the serialization of the hashtags this serializer adds the usage and participants.
    This serializer needs an context. The context must include:
        - counted: Dict with the hashtag id as key and the usage as value.
        - calling_user: Id of the calling user.
    """
    count = serializers.SerializerMethodField('_count')
    participants = serializers.SerializerMethodField('_participants')

    def _count(self, obj: Hashtag) -> int:
        """
        This method adds the precalculated usage of the hashtag.
        :param obj: The current hashtag.
        :return: The amount of usage of the specific hashtag.
        """
        return self.context["counted"][obj.id]

    def _participants(self, obj: Hashtag) -> OrderedDict:
        """
        This method takes all usage of the hashtag in combination ith an statements and returns the authors.
        Therefore one can get the participants of an conversation regarding this hashtag.
        The calling account is excluded from the results.
        :param obj: The current hashtag.
        :return: The participants of an hashtag with out the requesting account.
        """
        tagged: QuerySet[HashtagTagging] = HashtagTagging.objects.filter(hashtag=obj.id)
        tagged = tagged.exclude(statement__author=self.context["calling_user"])

        authors: QuerySet[Account] = Account.objects.filter(
            user__id__in=tagged.values_list('statement__author', flat=True).distinct()
        )
        serializer: AccountSerializer = AccountSerializer(instance=authors, many=True)
        return serializer.data

    class Meta:
        model = Hashtag
        fields = HashtagSerializer.Meta.fields + ('count', 'participants')


class AccountSerializer(serializers.ModelSerializer):
    """
    This serializer serializes the accounts and their data.
    It can be used to serialize accounts.
    Todo: Replace the account mentioning with users to remove this dependencies.
    """
    user = UserPublicSerializer()

    class Meta:
        model = apps.get_model("the_social_network", "Account")
        fields = ('user', 'image',)


class SimpleStatementSerializer(serializers.ModelSerializer):
    """
    This serializer serializes the statements and their content.
    It can be used to serialize content of a statement.
    """
    author = AccountSerializer()
    tagged = serializers.ListField(source='get_hashtags', child=HashtagSerializer())
    mentioned = serializers.ListField(source='get_mentioning', child=AccountSerializer())

    class Meta:
        model = Statement
        fields = ('id', 'author', 'content', 'tagged', 'mentioned', 'created')


class ReactionSerializer(serializers.ModelSerializer):
    """
    This serializer is for reactions.
    It will return the serialized reaction and shows the id, vote and the child statement.
    """
    child = SimpleStatementSerializer()
    parent = SimpleStatementSerializer()

    class Meta:
        model = Reaction
        fields = ('id', 'vote', 'child', 'parent')


class StatementSerializer(SimpleStatementSerializer):
    """
    This is more then the simple statement serializer.
    With this serializer one can also get information regarding the connection to the parent.
    Todo: Is there a way to combine each statement with parent and child information and shorten the frontend?
    """
    relation_to_parent = serializers.ListField(source='get_reaction_to_parent', child=ReactionSerializer())

    class Meta:
        model = Statement
        fields = SimpleStatementSerializer.Meta.fields + ('relation_to_parent',)


class StatementObservationSerializer(StatementSerializer):
    """
    This serializer is for the statement observation.
    Therefore the reactions are extended in the fields.
    """
    reactions = serializers.ListField(source='get_reactions', child=ReactionSerializer())

    class Meta:
        model = Statement
        fields = StatementSerializer.Meta.fields + ('reactions',)
