# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import rer.immersivereader


class RerImmersivereaderLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=rer.immersivereader)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'rer.immersivereader:default')


RER_IMMERSIVEREADER_FIXTURE = RerImmersivereaderLayer()


RER_IMMERSIVEREADER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(RER_IMMERSIVEREADER_FIXTURE,),
    name='RerImmersivereaderLayer:IntegrationTesting',
)


RER_IMMERSIVEREADER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(RER_IMMERSIVEREADER_FIXTURE,),
    name='RerImmersivereaderLayer:FunctionalTesting',
)


RER_IMMERSIVEREADER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        RER_IMMERSIVEREADER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='RerImmersivereaderLayer:AcceptanceTesting',
)
