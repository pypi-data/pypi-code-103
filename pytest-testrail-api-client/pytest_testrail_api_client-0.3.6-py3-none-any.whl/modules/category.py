from pytest_testrail_api_client.modules.session import Session


class Base:

    def __init__(self, session):
        self._session: Session = session

    def _valid(self, response, return_class, key: str = None, add_session: bool = False):
        if isinstance(response, str):
            return response
        elif key:
            return return_class(response[key]) if isinstance(response[key], dict) else \
                [return_class(elem) for elem in response[key]]
        else:
            if add_session:
                return return_class(self, response) if isinstance(response, dict) else \
                    [return_class(self, elem) for elem in response]
            else:
                return return_class(response) if isinstance(response, dict) else [return_class(elem) for elem in
                                                                                  response]
