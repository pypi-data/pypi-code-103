from django.conf import settings


class Settings:
    @property
    def FLAVIUS_ENDPOINT_DEV(self):
        return getattr(settings, "FLAVIUS_ENDPOINT_DEV", 'http://localhost/ipos/')

    @property
    def FLAVIUS_ENDPOINT(self):
        return getattr(settings, "FLAVIUS_ENDPOINT", 'http://localhost/ipos/')

    @property
    def FLAVIUS_API_REGI(self):
        return getattr(settings, "FLAVIUS_API_REGI", 'api')

    @property
    def FLAVIUS_API_STAFF(self):
        return getattr(settings, "FLAVIUS_API_STAFF", 'api')

    @property
    def FLAVIUS_API_BACKDATA_SEARCH(self):
        return getattr(settings, "FLAVIUS_API_BACKDATA_SEARCH", 'api/backdata_search.php')

    @property
    def FLAVIUS_API_DTO_LIST(self):
        return getattr(settings, "FLAVIUS_API_DTO_LIST", 'api/dto_list.php')

    @property
    def FLAVIUS_API_ITEM_SEARCH(self):
        return getattr(settings, "FLAVIUS_API_ITEM_SEARCH", 'api/item_search.php')

    @property
    def FLAVIUS_API_ITEM_CREATE(self):
        return getattr(settings, "FLAVIUS_API_ITEM_CREATE", 'api/item_create.php')

    @property
    def FLAVIUS_API_ITEM_EDIT(self):
        return getattr(settings, "FLAVIUS_API_ITEM_EDIT", 'api/item_edit.php')

    @property
    def FLAVIUS_API_ENVIRONMENT_SEARCH(self):
        return getattr(settings, "FLAVIUS_API_ENVIRONMENT_SEARCH", 'api/environment_fetch.php')

    @property
    def FLAVIUS_API_ENVIRONMENT_SET(self):
        return getattr(settings, "FLAVIUS_API_ENVIRONMENT_SET", 'api/environment_set_value.php')

    @property
    def FLAVIUS_API_SORT_SEARCH(self):
        return getattr(settings, "FLAVIUS_API_SORT_SEARCH", 'api/sort_fetch_list.php')

    @property
    def FLAVIUS_API_DTO_FETCH(self):
        return getattr(settings, "FLAVIUS_API_DTO_FETCH", 'api/dto_fetch.php')

    @property
    def FLAVIUS_API_HEADER_FETCH(self):
        return getattr(settings, "FLAVIUS_API_HEADER_FETCH", 'api/header_fetch.php')

    @property
    def FLAVIUS_API_DATA_CREATE(self):
        return getattr(settings, "FLAVIUS_API_DATA_CREATE", 'api/data_add.php')

    @property
    def FLAVIUS_API_DATA_UPDATE(self):
        return getattr(settings, "FLAVIUS_API_DATA_UPDATE", 'api/data_modify.php')

    @property
    def FLAVIUS_API_DATA_DELETE(self):
        return getattr(settings, "FLAVIUS_API_DATA_DELETE", 'api/data_delete.php')

    @property
    def FLAVIUS_API_ORDER_DECIDE(self):
        return getattr(settings, "FLAVIUS_API_DATA_DELETE", 'api/order_decide.php')

    @property
    def FLAVIUS_API_PAGE_FETCH(self):
        return getattr(settings, "FLAVIUS_API_ORDER_DECIDE", 'api/pages.php')

    @property
    def FLAVIUS_API_CREDIT_ADD(self):
        return getattr(settings, "FLAVIUS_API_PAYMENT_ADD", 'api/credit_add.php')

    @property
    def FLAVIUS_API_PAYMENT_COMPLETE(self):
        return getattr(settings, "FLAVIUS_API_PAYMENT_COMPLETE", 'api/payment_complete.php')

    @property
    def EXCLUDE_TAX(self):
        return getattr(settings, "EXCLUDE_TAX", '91100')

    @property
    def INCLUDE_TAX(self):
        return getattr(settings, "INCLUDE_TAX", '90100')

    @property
    def FLAVIUS_CRT_FILE(self):
        return getattr(settings, "FLAVIUS_CRT_FILE", None)

    @property
    def FLAVIUS_KEY_FILE(self):
        return getattr(settings, "FLAVIUS_KEY_FILE", None)


conf = Settings()
