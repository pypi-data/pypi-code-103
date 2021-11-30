from statuspageio.errors import ConfigurationError


class PageService:
    """
    :class:`statuspageio.PageService` is used by :class:`statuspageio.Client` to make
    actions related to Page resource.

    Normally you won't instantiate this class directly.
    """

    OPTS_KEYS_TO_PERSIST = ['name', 'url', 'notifications_from_email', ]

    def __init__(self, http_client, page_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.container = 'page'
        self.page_id = page_id

    @property
    def http_client(self):
        return self.__http_client

    def get(self):
        """
        Get page details

        Gets page information
        If the specified page does not exist, the request will return an error


        :calls: ``get pages/{page_id}.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """
        _, _, page = self.http_client.get(f'/pages/{self.page_id}.json')

        return page

    def update(self, **kwargs):
        """
        Update page details

        Updates page information
        If the specified page does not exist, the request will return an error


        :calls: ``patch pages/{page_id}.json``
        :param dict **kwargs:  component attributes to update.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        OPTS_KEYS_TO_PERSIST = [
            'name',
            'url',
            'notifications_from_email',
            'time_zone',
            'city',
            'state',
            'country',
            'subdomain',
            'domain',
            'layout',
            'allow_email_subscribers',
            'allow_incident_subscribers',
            'allow_page_subscribers',
            'allow_sms_subscribers',
            'hero_cover_url',
            'transactional_logo_url',
            'css_body_background_color',
            'css_font_color',
            'css_light_font_color',
            'css_greens',
            'css_oranges',
            'css_reds',
            'css_yellows']

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        page = self.http_client.patch(
            f'/pages/{self.page_id}.json',
            container=self.container,
            body=attributes,
        )

        return page


class ComponentsService:
    """
    :class:`statuspageio.ComponentsService` is used by :class:`statuspageio.Client` to make
    actions related to Components resource.

    Normally you won't instantiate this class directly.
    """

    OPTS_KEYS_TO_PERSIST = ['name', 'description', 'group_id', 'status', 'showcase']

    def __init__(self, http_client, page_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.page_id = page_id
        self.container = 'component'

    @property
    def http_client(self):
        return self.__http_client

    def get(self, component_id):
        """
        Get component details

        Gets component information
        If the specified component does not exist, the request will return an error


        :calls: ``get components/{component_id}.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """
        _, _, page = self.http_client.get(f'/pages/{self.page_id}/components/{component_id}')
        return page

    def list(self):
        """
        List components

        Lists components and their information
        If the specified contact does not exist, the request will return an error


        :calls: ``get pages/{page_id}/components/{component_id}.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, components = self.http_client.get(f'/pages/{self.page_id}/components.json')
        return components

    def create(self, **kwargs):
        """
        Create a component

        Creates component
        If the specified contact does not exist, the request will return an error


        :calls: ``post pages/{page_id}/components.json``
        :param dict **kwargs:  component attributes to update.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in self.OPTS_KEYS_TO_PERSIST)

        _, _, component = self.http_client.post(
            f'/pages/{self.page_id}/components.json',
            container=self.container,
            body=attributes,
        )

        return component

    def delete(self, component_id):
        """
        Delete a component

        Deletes a component
        If the specified contact does not exist, the request will return an error


        :calls: ``delete pages/{page_id}/components/{component_id}.json``
        :param int component_id: Unique identifier of a component.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        status_code, _, _ = self.http_client.delete(
            f"/pages/{self.page_id}/components/{component_id}.json",
            component_id=component_id,
        )
        return status_code

    def update(self, component_id, **kwargs):
        """
        Update a component

        Updates component information
        If the specified contact does not exist, the request will return an error


        :calls: ``patch pages/{page_id}/components/{component_id}.json``
        :param int component_id: Unique identifier of a component.
        :param dict **kwargs:  component attributes to update.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        if not kwargs:
            raise Exception('attributes for Contact are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in self.OPTS_KEYS_TO_PERSIST)

        _, _, component = self.http_client.patch(
            f"/pages/{self.page_id}/components/{component_id}.json",
            container=self.container,
            body=attributes,
        )
        return component


class ComponentGroupsService:
    """
    :class:`statuspageio.ComponentGroupsService` is used by :class:`statuspageio.Client` to make
    actions related to Component Groups resource.

    Normally you won't instantiate this class directly.
    """

    OPTS_KEYS_TO_PERSIST = ['name', 'description', 'status']

    def __init__(self, http_client, page_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.page_id = page_id
        self.container = 'component_group'

    @property
    def http_client(self):
        return self.__http_client

    def list(self):
        """
        List all component groups

        :calls: ``get pages/{page_id}/component-groups.json``
        :return: Dictionary that support attribute-style access and represents updated Component Groups resource.
        :rtype: dict
        """

        _, _, component_groups = self.http_client.get(f'/pages/{self.page_id}/component-groups.json')
        return component_groups

    def create(self, name, components, description=None):
        """
        Create a component group

        :calls: ``post pages/{page_id}/component-groups.json``
        :param dict **kwargs:  component group attributes to create.
        :return: Dictionary that support attribute-style access and represents updated Component Group resource.
        :rtype: dict
        """
        body = {
            'description': description,
            'component_group': {
                'components': components,
                'name': name,
            }
        }

        _, _, component_group = self.http_client.post(
            f'/pages/{self.page_id}/component-groups.json',
            raw=True,
            body=body,
        )
        return component_group

    def delete(self, component_group_id):
        """
        Remove a incident

        :calls: ``delete pages/{page_id}/component-groups.json``
        :return: status code
        :rtype: int
        """
        status_code, _, _ = self.http_client.delete(f"/pages/{self.page_id}/component-groups/{component_group_id}.json")
        return status_code


class IncidentsService:
    """
    :class:`statuspageio.IncidentsService` is used by :class:`statuspageio.Client` to make
    actions related to Incidents resource.

    Normally you won't instantiate this class directly.
    """

    OPTS_KEYS_TO_PERSIST = ['name', 'description', 'group_id', 'status']

    def __init__(self, http_client, page_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.page_id = page_id
        self.container = 'incident'

    @property
    def http_client(self):
        return self.__http_client

    def list(self):
        """
        List all incidents

        :calls: ``get pages/{page_id}/incidents.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, incidents = self.http_client.get(f'/pages/{self.page_id}/incidents.json')
        return incidents

    def list_unresolved(self):
        """
        List unresolved incidents

        :calls: ``get pages/{page_id}/incidents/unresolved.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, incidents = self.http_client.get(f'/pages/{self.page_id}/incidents/unresolved.json')
        return incidents

    def list_scheduled(self):
        """
        List scheduled incidents

        :calls: ``get pages/{page_id}/incidents/scheduled.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """
        _, _, incidents = self.http_client.get(f'/pages/{self.page_id}/incidents/scheduled.json')
        return incidents

    def create(self, **kwargs):
        """
        Create a incident

        :calls: ``post pages/{page_id}/incidents.json``
        :param dict **kwargs:  incident attributes to update.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        OPTS_KEYS_TO_PERSIST = [
            'name',
            'status',
            'body',
            'wants_twitter_update',
            'impact_override',
            'component_ids',
        ]

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, component = self.http_client.post(
            f'/pages/{self.page_id}/incidents.json',
            container=self.container,
            body=attributes,
        )

        return component

    def create_scheduled(self, **kwargs):
        """
        Create a scheduled incident

        :calls: ``post pages/{page_id}/incidents.json``
        :param dict **kwargs:  incident attributes to update.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        OPTS_KEYS_TO_PERSIST = [
            'name',
            'status',
            'scheduled_for',
            'scheduled_until',
            'message',
            'wants_twitter_update',
            'scheduled_remind_prior',
            'scheduled_auto_in_progress',
            'scheduled_auto_completed',
            'impact_override',
            'component_ids',
        ]
        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, incident = self.http_client.post(
            f'/pages/{self.page_id}/incidents.json',
            container=self.container,
            body=attributes,
        )
        return incident

    def delete(self, incident_id):
        """
        Remove a incident

        :calls: ``delete pages/{page_id}/incidents.json``
        :return: status code
        :rtype: int
        """

        status_code, _, _ = self.http_client.delete(f"/pages/{self.page_id}/incidents/{incident_id}.json")
        return status_code

    def update(self, incident_id, **kwargs):
        """
        Update a incident

        Updates incident information

        NOTE: if either of status or message is modified, a new incident update will be generated.
        You should update both of these attributes at the same time to avoid two separate incident
        updates being generated.
        :param dict **kwargs:  incident attributes to update.
        :calls: ``patch /pages/[page_id]/incidents/[incident_id].json``
        :return: Status code
        :rtype: string

        """
        OPTS_KEYS_TO_PERSIST = [
            'name',
            'status',
            'body',
            'wants_twitter_update',
            'impact_override',
            'component_ids',
        ]

        if not kwargs:
            raise Exception('attributes for Incident are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, component = self.http_client.patch(
            f"/pages/{self.page_id}/incidents/{incident_id}.json",
            container=self.container,
            body=attributes,
        )
        return component

    def update_previous(self, incident_id, incident_update_id, **kwargs):
        """
        Update a previous incident update

        :param dict **kwargs:  incident attributes to update.
        :calls: ``patch /pages/[page_id]/incidents/[incident_id]/incident_updates/[incident_update_id]``
        :return: Status code
        :rtype: string

        """
        OPTS_KEYS_TO_PERSIST = [
            'body',
            'wants_twitter_update',
            'deliver_notifications',
        ]

        if not kwargs:
            raise Exception('attributes for Incident Update are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, component = self.http_client.patch(
            f"/pages/{self.page_id}/incidents/{incident_id}/incident_updates/{incident_update_id}",
            container='incident_update',
            body=attributes,
        )
        return component


class SubscribersService:
    """
    :class:`statuspageio.SubscribersService` is used by :class:`statuspageio.Client` to make
    actions related to Subscriber resource.

    Normally you won't instantiate this class directly.
    """

    OPTS_KEYS_TO_PERSIST = ['name', 'description', 'group_id', 'status']

    def __init__(self, http_client, page_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.page_id = page_id
        self.container = 'subscriber'

    @property
    def http_client(self):
        return self.__http_client

    def list(self):
        """
        List subscribers

        Lists all of the current subscribers
        :calls: ``get /pages/[page_id]/subscribers.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, subscribers = self.http_client.get(f'/pages/{self.page_id}/subscribers.json')
        return subscribers

    def create(self, **kwargs):
        """
        Create a subscriber

        :calls: ``post pages/{page_id}/subscribers.json``
        :param dict **kwargs:  subscriber attributes to update.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        OPTS_KEYS_TO_PERSIST = [
            'email',
            'phone_number',
            'phone_country',
            'endpoint',
            'skip_confirmation_notification',
            'page_access_user']

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, subscriber = self.http_client.post(
            f'/pages/{self.page_id}/subscribers.json',
            container=self.container,
            body=attributes,
        )

        return subscriber

    def delete(self, subscriber_id=None):
        """
        Create a subscriber

        :calls: ``delete pages/{page_id}/subscribers.json``
        :param subscriber_id
        :return: status code
        :rtype: int
        """

        status_code, _, _ = self.http_client.delete(f"/pages/{self.page_id}/subscribers/{subscriber_id}.json")
        return status_code


class MetricsService:
    """
    :class:`statuspageio.MetricsService` is used by :class:`statuspageio.Client` to make
    actions related to Metrics resource.

    Normally you won't instantiate this class directly.
    """

    def __init__(self, http_client, page_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.page_id = page_id
        self.container = 'metric'

    @property
    def http_client(self):
        return self.__http_client

    def list_available(self):
        """
        List available metric providers
        :calls: ``get /metrics_providers.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, providers = self.http_client.get('/metrics_providers.json')
        return providers

    def list_linked(self):
        """
        List linked metric providers
        :calls: ``get /pages/[page_id]/metrics_providers.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        _, _, providers = self.http_client.get(f'/pages/{self.page_id}/metrics_providers.json')
        return providers

    def list_metrics_for_provider(self, provider_id=None):
        """
        List metrics for a linked metric provider
        :params provider_id This is the ID from the provider you are looking up
        :calls: ``/pages/{page_id}/metrics_providers/{metrics_provider_id}/metrics.json``
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """
        _, _, metrics = self.http_client.get(f'/pages/{self.page_id}/metrics_providers/{provider_id}/metrics.json')
        return metrics

    def create(self, provider_id=None, **kwargs):
        """
        Create a custom metric

        :calls: ``post /pages/[page_id]/metrics_providers/[metrics_provider_id]/metrics.json``
        :param provider_id: The id of the custom provider or 'self' from the available providers list
        :param dict **kwargs:  metic attributes to create.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        OPTS_KEYS_TO_PERSIST = [
            'name',
            'suffix',
            'display',
            'tooltip_description',
            'y_axis_min',
            'y_axis_max',
            'decimal_places']

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, metric = self.http_client.post(
            f'/pages/{self.page_id}/metrics_providers/{provider_id}/metrics.json',
            container=self.container,
            body=attributes,
        )

        return metric

    def submit_data(self, metric_id=None, **kwargs):
        """
        Create a custom metric

        :calls: ``post /pages/{page_id}/metrics/{metric_id}/data.json``
        :param metric_id: The id of the custom metric.
        :param dict **kwargs:  metic attributes to create.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        OPTS_KEYS_TO_PERSIST = ['timestamp', 'value']

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, metric = self.http_client.post(
            f'/pages/{self.page_id}/metrics/{metric_id}/data.json',
            container='data',
            body=attributes,
        )

        return metric

    def delete_all_data(self, metric_id=None):
        """
        Delete All Metric Data

        :calls: ``delete /pages/[page_id]/metrics/[metric_id]/data.json``
        :param metric_id: The id of the custom metric.
        :return: Dictionary that support attribute-style access and represents updated Component resource.
        :rtype: dict
        """

        metric, _, _, = self.http_client.delete(f"/pages/{self.page_id}/metrics/{metric_id}/data.json")
        return metric

    def delete(self, metric_id=None):
        """
        Delete Custom Metric

        :calls: ``delete /pages/[page_id]/metrics/[metric_id].json``
        :param metric_id: The id of the custom metric.
        :return: status code.
        :rtype: int
        """

        _, _, metric = self.http_client.delete(f"/pages/{self.page_id}/metrics/{metric_id}.json")
        return metric


class UsersService:
    """
    :class:`statuspageio.UsersService` is used by :class:`statuspageio.Client` to make
    actions related to Users resource.

    Normally you won't instantiate this class directly.
    """
    def __init__(self, http_client, organization_id):
        """
        :param :class:`statuspageio.HttpClient` http_client: Pre configured high-level http client.
        """

        self.__http_client = http_client
        self.organization_id = organization_id
        self.container = 'user'

    @property
    def http_client(self):
        if not self.organization_id:
            raise ConfigurationError(
                'No organization_id provided.'
                'You are unable to manage users. Set your organization_id during client initialization using: '
                '"statuspageio.Client(organization_id= <YOUR_PERSONAL_page_id>)"')

        return self.__http_client

    def list(self):
        """
        List all users
        :calls: ``get organizations/[organization_id]/users.json``
        :return: Dictionary that support attribute-style access and represents User resource.
        :rtype: dict
        """
        _, _, users = self.http_client.get(
            f'/organizations/{self.organization_id}/users.json',
            container=self.container,
        )
        return users

    def create(self, **kwargs):
        """
        Create a user

        :calls: ``post /organizations/[organization_id]/users.json``
        :param dict **kwargs:  Users attributes to create.
        :return: Dictionary that support attribute-style access and represents updated User resource.
        :rtype: dict
        """
        OPTS_KEYS_TO_PERSIST = ['email', 'password', 'first_name', 'last_name']

        if not kwargs:
            raise Exception('attributes are missing')

        attributes = dict((k, v) for k, v in kwargs.items()
                          if k in OPTS_KEYS_TO_PERSIST)

        _, _, user = self.http_client.post(
            f'/organizations/{self.organization_id}/users.json',
            container=self.container,
            body=attributes,
        )

        return user

    def delete(self, user_id=None):
        """
        Delete a User

        :calls: ``delete organizations/[organization_id]/users/[user_id].json``
        :param user_id: The id of the user to delete.
        :return: status code.
        :rtype: int
        """
        _, _, user = self.http_client.delete(f"/organizations/{self.organization_id}/users/{user_id}.json")
        return user
