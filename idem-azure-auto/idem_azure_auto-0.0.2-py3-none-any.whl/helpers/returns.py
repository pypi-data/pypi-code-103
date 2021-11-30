import dict_tools.differ as differ


class StateReturn(dict):
    """
    Convenience class to manage POP state returns.
    """

    def __init__(
        self,
        name=None,
        result=None,
        comment=None,
        old_obj=None,
        new_obj=None,
        error=None,
    ):
        """
        Initialize an object of this class.
        :param name: The name of the state (e.g. from a SLS file).
        :param result: True if the state call works, False otherwise.
        :param comment: Any relevant comments to the state execution.
        For example a 200 code from an HTTP call or a mere readable comment.
        :param old_obj: For state changes, the object's state
        (e.g., dict of values).
        prior to any state change request executions.
        :param new_obj: For state changes, the new object's state after any
        state change request executions.
        """
        super().__init__(
            [
                ("name", name),
                ("result", result),
                ("comment", comment),
                ("changes", None),
            ]
        )
        if old_obj or new_obj:
            self["changes"] = differ.deep_diff(
                old_obj if old_obj else dict(), new_obj if new_obj else dict()
            )
        if error:
            comment += " " + str(error)
        if comment:
            self["comment"] = comment
