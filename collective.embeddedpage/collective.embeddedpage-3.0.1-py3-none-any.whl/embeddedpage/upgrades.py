from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility


OLD_BEHAVIORS = [
    "plone.app.content.interfaces.INameFromTitle",
    "plone.app.dexterity.behaviors.discussion.IAllowDiscussion",
    "plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation",
    "plone.app.dexterity.behaviors.id.IShortName",
    "plone.app.contenttypes.behaviors.richtext.IRichTextBehavior",
    "plone.app.relationfield.behavior.IRelatedItems",
    "plone.app.versioningbehavior.behaviors.IVersionable",
    "plone.app.contenttypes.behaviors.tableofcontents.ITableOfContents",
    "plone.app.lockingbehavior.behaviors.ILocking",
]


def migrate_behaviors(context):
    # Migrate FTI
    fti = queryUtility(IDexterityFTI, name="EmbeddedPage")
    behavior_list = [a for a in fti.behaviors if a not in OLD_BEHAVIORS]
    fti.behaviors = behavior_list
    context.runImportStepFromProfile("collective.embeddedpage:default", "typeinfo")
