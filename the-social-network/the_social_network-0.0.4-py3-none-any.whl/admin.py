from django.contrib import admin

from .models import *


class RelationshipInline(admin.StackedInline):
    """
    This is the stackable inline representation of the relationships.
    It will use the from_account as an foreign key.
    It will not display any more then relationships then necessary (extra = 0)
    """
    model = Relationship
    fk_name = 'from_account'
    extra = 0


class StatementsInline(admin.StackedInline):
    """
    This is the stackable inline representation of the statements.
    It will not display any more then statements then necessary (extra = 0)
    """
    model = Statement
    extra = 0


class AccountAdmin(admin.ModelAdmin):
    """
    This is the admin for the accounts.
    This will add the relationships of an account to admin interface.
    This will add content of an account to admin interface.
    """
    inlines = [RelationshipInline, StatementsInline]


class StatementHashtagInline(admin.StackedInline):
    """
    This is the stackable representation of the tagging of an statement with an hashtag.
    """
    model = HashtagTagging
    fk_name = 'statement'
    extra = 0


class StatementAccountInline(admin.StackedInline):
    """
    This is the stackable representation of the mentioning of an account within an statement.
    """
    model = AccountTagging
    fk_name = 'statement'
    extra = 0


class StatementReactionInline(admin.StackedInline):
    """
    This is the stackable representation of the reaction relation between statements.
    """
    model = Reaction
    fk_name = 'parent'
    extra = 0


class StatementAdmin(admin.ModelAdmin):
    """
    This ist the admin for the statements.
    It will add the tagging of statements with hashtags to the admin interface.
    """
    inlines = [StatementHashtagInline,
               StatementAccountInline, StatementReactionInline]


admin.site.register(Account, AccountAdmin)
admin.site.register(Relationship)

admin.site.register(Hashtag)
admin.site.register(HashtagTagging)
admin.site.register(AccountTagging)
admin.site.register(Reaction)
admin.site.register(Statement, StatementAdmin)
