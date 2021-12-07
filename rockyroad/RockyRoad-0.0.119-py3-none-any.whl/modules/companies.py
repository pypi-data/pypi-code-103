from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Companies(Consumer):
    """Inteface to Companies resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def branches(self):
        return self.__Branches(self)

    def subscribers(self):
        return self.__Subscribers(self)

    @returns.json
    @get("companies")
    def list(
        self,
        uid: Query(type=str) = None,
        company_code: Query(type=str) = None,
        company_name: Query(type=str) = None,
        company_account: Query(type=str) = None,
        company_account_uid: Query(type=str) = None,
    ):
        """This call will return detailed information for all companies or for those for the specified criteria."""

    @returns.json
    @delete("companies")
    def delete(self, uid: Query(type=str)):
        """This call will delete the company for the specified uid."""

    @returns.json
    @json
    @post("companies")
    def insert(self, company: Body):
        """This call will create a company with the specified parameters."""

    @returns.json
    @json
    @patch("companies")
    def update(self, company: Body):
        """This call will update the company with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Subscribers(Consumer):
        """Inteface to company Subscribers resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("companies/subscribers")
        def list(
            self,
            company_uid: Query(type=str) = None,
        ):
            """This call will return detailed information for all company subscribers or for those for the specified criteria."""

        @returns.json
        @delete("companies/subscribers")
        def delete(
            self,
            company_uid: Query(type=str),
            subscriber_uid: Query(type=str),
        ):
            """This call will delete the company subscriber for the specified uid."""

        @returns.json
        @json
        @post("companies/subscribers")
        def insert(self, company_subscriber: Body):
            """This call will create a company subscriber with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Branches(Consumer):
        """Inteface to company Branches resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def subscribers(self):
            return self.__Subscribers(self)

        @returns.json
        @get("companies/branches")
        def list(
            self,
            uid: Query(type=str) = None,
            company_code: Query(type=str) = None,
            branch_name: Query(type=str) = None,
            branch_code: Query(type=str) = None,
            company_uid: Query(type=str) = None,
            company_account: Query(type=str) = None,
            company_account_uid: Query(type=str) = None,
            include_machines: Query(type=bool) = None,
        ):
            """This call will return detailed information for all company branches or for those for the specified criteria."""

        @returns.json
        @delete("companies/branches")
        def delete(self, uid: Query(type=str)):
            """This call will delete the company branch for the specified uid."""

        @returns.json
        @json
        @post("companies/branches")
        def insert(self, companyBranch: Body):
            """This call will create a company branch  with the specified parameters."""

        @returns.json
        @json
        @patch("companies/branches")
        def update(self, companyBranch: Body):
            """This call will update the company branch  with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Subscribers(Consumer):
            """Inteface to company Branch Subscribers resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @get("companies/branches/subscribers")
            def list(
                self,
                company_code: Query(type=str) = None,
                company_branch_uid: Query(type=str) = None,
            ):
                """This call will return detailed information for all company branch subscribers or for those for the specified criteria."""

            @returns.json
            @delete("companies/branches/subscribers")
            def delete(
                self,
                company_branch_uid: Query(type=str),
                subscriber_uid: Query(type=str),
            ):
                """This call will delete the company branch subscriber for the specified uid."""

            @returns.json
            @json
            @post("companies/branches/subscribers")
            def insert(self, company_branch_subscriber: Body):
                """This call will create a company branch subscriber with the specified parameters."""