import unittest
from hein_control.mixin.reg import InstanceRegistry
from hein_control.action.basic import Action


class Extra(InstanceRegistry):
    """extra class to validate segregation"""
    pass


def test():
    return True


xtra = Extra()
action = Action(test)


class TestRegistry(unittest.TestCase):
    def test_double_registry(self):
        """ensures double registry of actions is not allowed
        todo move this to test_actions
        """
        self.assertRaises(
            ValueError,
            Action,
            test
        )

    def test_retrieval(self):
        """test general retrieval methods"""
        # retrieve decision instance
        first = Action.registered_actions[0]

        # attempt various ways of retrieving instance
        Action.class_instance_by_id(first._uuid)
        InstanceRegistry.get_instance_by_uuid(first._uuid)
        InstanceRegistry.get_instance_by_uuid(first.uuid)

    def test_cross_retrieval(self):
        """tests for retrieval by uuid from other classes"""
        first = Action.class_registry[0]
        Extra.search_class_for_id(
            first._uuid,
            'Action'
        )

    def test_segregation(self):
        """tests that registries are separated"""
        actions = Action.registered_actions
        self.assertFalse(
            all([isinstance(action, Extra) for action in actions])
        )
