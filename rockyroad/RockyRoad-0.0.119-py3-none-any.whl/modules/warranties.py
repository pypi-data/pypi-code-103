from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Warranties(Consumer):
    """Inteface to Warranties resource for the RockyRoad API."""

    from .warranty_rates import Rates
    from .warranty_registrations import Warranty_Registrations
    from .warranty_failure_modes import Failure_Modes

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def registrations(self):
        return self.Warranty_Registrations(self)

    def creditRequests(self):
        return self.__Credit_Requests(self)

    def rates(self):
        return self.Rates(self)

    def failureModes(self):
        return self.Failure_Modes(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Credit_Requests(Consumer):
        """Inteface to Warranties Credit Requests resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def logs(self):
            return self.__Logs(self)

        def summaries(self):
            return self.__Summaries(self)

        @returns.json
        @get("warranties/credit-requests")
        def list(
            self,
            uid: Query(type=str) = None,
            dealer_account: Query(type=str) = None,
            claimReference: Query(type=str) = None,
        ):
            """This call will return detailed warranty credit request information for the specified criteria."""

        @returns.json
        @delete("warranties/credit-requests")
        def delete(self, uid: Query(type=str)):
            """This call will delete the warranty credit request for the specified uid."""

        @returns.json
        @json
        @post("warranties/credit-requests")
        def insert(self, creditRequest: Body):
            """This call will create a warranty credit request with the specified parameters."""

        @returns.json
        @json
        @patch("warranties/credit-requests")
        def update(self, creditRequest: Body):
            """This call will update the warranty credit request with the specified parameters."""

        @returns.json
        @multipart
        @post("warranties/credit-requests/add-files")
        def addFile(self, uid: Query(type=str), file: Part):
            """This call will a upload file for a warranty credit request with the specified uid."""

        @get("warranties/credit-requests/download-files")
        def downloadFile(
            self,
            uid: Query(type=str),
            filename: Query(type=str),
        ):
            """This call will download the file associated with the warranty credit request with the specified uid."""

        @returns.json
        @get("warranties/credit-requests/list-files")
        def listFiles(
            self,
            uid: Query(type=str),
        ):
            """This call will return a list of the files associated with the warranty credit request for the specified uid."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Logs(Consumer):
            """Inteface to Warranties Credit Requests Logs resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @get("warranties/credit-requests/logs")
            def list(
                self,
                warranty_log_uid: Query(type=str) = None,
                warranty_credit_request_uid: Query(type=str) = None,
            ):
                """This call will return log information for the specified criteria."""

            @returns.json
            @delete("warranties/credit-requests/logs")
            def delete(self, uid: Query(type=str)):
                """This call will delete the log information for the specified uid."""

            @returns.json
            @json
            @post("warranties/credit-requests/logs")
            def insert(self, warranty_log: Body):
                """This call will create log information with the specified parameters."""

            @returns.json
            @json
            @patch("warranties/credit-requests/logs")
            def update(self, log: Body):
                """This call will update the log information with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Summaries(Consumer):
            """Inteface to Warranties Credit Requests Summaries resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @get("warranties/credit-requests/summaries")
            def list(
                self,
                dealer_account: Query(type=str) = None,
                dealer_code: Query(type=str) = None,
                dealer_uid: Query(type=str) = None,
            ):
                """This call will return a summary of warranty information."""
