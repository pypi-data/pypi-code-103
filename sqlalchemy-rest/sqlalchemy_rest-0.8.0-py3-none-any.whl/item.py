from abc import abstractmethod
from typing import Any

from sqlalchemy.exc import IntegrityError

from .abc import AbstractRESTView
from .typing import ResponseType

__all__ = [
    'AbstractItemRESTView',
]


class AbstractItemRESTView(AbstractRESTView):
    """
    Базовый view для работы с item
    """

    def __init__(
        self,
        *args,  # pylint: disable=unused-argument  # noqa
        **kwargs,  # pylint: disable=unused-argument  # noqa
    ) -> None:
        super().__init__()
        self._item: Any = None

    @property
    @abstractmethod
    def _url_match_data(self) -> Any: ...

    def v_item(
        self,
        *args,  # pylint: disable=unused-argument  # noqa
        **kwargs,  # pylint: disable=unused-argument  # noqa
    ) -> None:
        item_id = self._url_match_data.get('id')
        if not item_id:
            self._add_error('Неверно указан идентификатор ресурса.')
            return

        self._item = self._db_cls.byid(item_id)
        if not self._item:
            self._add_error('Запрашиваемая запись не найдена.')

    @abstractmethod
    def _item_transform(self) -> Any: ...

    @property
    @abstractmethod
    def _request_json_data(self) -> Any: ...

    def _extract_item_data(self, label: str) -> Any:
        """
        Извлечение отправленных в запросе данных

        :param label: ключ для получения данных из присланного json-объекта
        :return:
        """
        data = self._request_json_data[label]
        if not isinstance(data, dict):
            raise TypeError()
        return data

    def get(self) -> ResponseType:
        """
        Получение item из БД

        :return:
        """
        return self._render({
            self._item_label: self._item_transform(),
        })

    def put(self) -> ResponseType:
        """

        Редактирование item в БД
        :return:
        """
        try:
            self._item.edit(
                **self._extract_item_data(self._item_label),
            )

        except IntegrityError:
            self._add_error('Запись с такими параметрами уже существует.')
            return self._render_error()

        except (ValueError, KeyError, TypeError):
            self._add_error('Неверный формат переданных данных.')
            return self._render_error()

        return self.get()

    def collection_post(self) -> ResponseType:

        try:
            self._item = self._db_cls.create(
                **self._extract_item_data(self._item_from_collection_label),
            )
        except IntegrityError:
            self._add_error('Запись с такими параметрами уже существует.')
            return self._render_error()

        except (ValueError, KeyError, TypeError):
            self._add_error('Неверный формат переданных данных.')
            return self._render_error()

        return self._render({
            self._item_from_collection_label: self._item_transform(),
        })

    def delete(self) -> ResponseType:
        """
        Удаление записи из БД

        :return:
        """
        try:
            self._item.delete()

        except IOError:
            self._add_error('Данную запись удалить нельзя.')
            return self._render_error()

        return self._render(None)
