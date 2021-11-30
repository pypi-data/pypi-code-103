from typing import Callable, Optional

from .news_story import NewsStory
from ...core.session import get_default
from ...tools import create_repr
from ...tools._raise_exception import raise_exception_on_error
from refinitiv.data._data.core.session import Session


__all__ = ["Definition"]


class Definition:
    """
    This class describes parameters to retrieve data for news story.

    Parameters
    ----------
    story_id : str
        News Story ID.

    closure : str, optional
        Specifies the parameter that will be merged with the request

    extended_params : dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
    >>> from refinitiv.data.content import news
    >>> definition = news.story.Definition("urn:newsml:reuters.com:20201026:nPt6BSyBh")
    """

    def __init__(
        self,
        story_id: str,
        closure: Optional[str] = None,
        extended_params: dict = None,
    ):
        self.story_id = story_id
        self.closure = closure
        self.extended_params = extended_params

    @raise_exception_on_error
    def get_data(
        self,
        session: Session = None,
        on_response: Callable = None,
    ):
        """
        Returns a response from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        NewsStory.NewsStoryResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import news
        >>> response = news.story.Definition("urn:newsml:reuters.com:20201026:nPt6BSyBh").get_data()
        """
        if session is None:
            session = get_default()
        news_headlines = NewsStory(session=session, on_response=on_response)
        response = news_headlines.get_story(
            story_id=self.story_id,
            closure=self.closure,
            extended_params=self.extended_params,
        )
        return response

    @raise_exception_on_error
    async def get_data_async(
        self,
        session: Session = None,
        on_response: Callable = None,
    ):
        """
        Returns a response asynchronously from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        NewsStory.NewsStoryResponse

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import news
        >>> response = await news.story.Definition("urn:newsml:reuters.com:20201026:nPt6BSyBh").get_data_async()
        """

        if session is None:
            session = get_default()
        news_headlines = NewsStory(session=session, on_response=on_response)
        response = await news_headlines.get_story_async(
            story_id=self.story_id,
            closure=self.closure,
            extended_params=self.extended_params,
        )
        return response

    def __repr__(self):
        return create_repr(
            self,
            middle_path="content.news.story",
            content=f"{{story_id='{self.story_id}'}}",
        )
