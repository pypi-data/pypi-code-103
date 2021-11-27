from rdflib.term import URIRef
from rdflib.namespace import Namespace

from .. import BASE_CONTEXT
from ..context import Context
from ..context_dataobject import ContextDataObject


class VariableIdentifierMixin(object):
    '''
    A mix-in class that takes its identifier from its 'maker'
    passed in at initialization.
    '''
    def __init__(self, maker=None, **kwargs):
        '''
        Parameters
        ----------
        maker : object
            An object with an `identifier` attribute
        maker.identifier : rdflib.term.URIRef
            A URI that will serve as the identifier for the `VariableIdentifierMixin`
        '''
        if maker is not None:
            conf = kwargs.pop('conf', maker.conf)
            super(VariableIdentifierMixin, self).__init__(conf=conf, **kwargs)
        else:
            super(VariableIdentifierMixin, self).__init__(**kwargs)
        self.maker = maker

    @property
    def identifier(self):
        return self.identifier_helper()

    @identifier.setter
    def identifier(self, a):
        pass

    def identifier_helper(self):
        if self.maker is not None:
            return self.maker.identifier
        else:
            return super(VariableIdentifierMixin, self).identifier


class VariableIdentifierContext(VariableIdentifierMixin, Context):
    '''
    A Context that gets its identifier and its configuration from its 'maker'
    passed in at initialization
    '''

    @property
    def rdf_object(self):
        if self._rdf_object is None:
            self._rdf_object = VariableIdentifierContextDataObject.contextualize(self.context)(maker=self)

        return self._rdf_object.contextualize(self.context)


class VariableIdentifierContextDataObject(VariableIdentifierMixin, ContextDataObject):
    '''
    A ContextDataObject that gets its identifier and its configuration from its 'maker'
    passed in at initialization
    '''

    class_context = BASE_CONTEXT

    rdf_type = URIRef('http://openworm.org/schema/Context#variable')
    rdf_namespace = Namespace(rdf_type + '#')

    def defined_augment(self):
        return self.maker is not None and self.maker.identifier is not None
