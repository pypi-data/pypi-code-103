# coding: utf-8

"""
    API v1

    DocSpring is a service that helps you fill out and sign PDF templates.  # noqa: E501

    OpenAPI spec version: v1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class Template1(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'document_processed': 'bool',
        'expiration_interval': 'str',
        'scss': 'str',
        'document_state': 'str',
        'expire_after': 'float',
        'description': 'str',
        'slack_webhook_url': 'str',
        'demo': 'bool',
        'path': 'str',
        'header_html': 'str',
        'public_web_form': 'bool',
        'field_order': 'list[list[float]]',
        'permanent_document_url': 'str',
        'html': 'str',
        'template_type': 'str',
        'id': 'str',
        'page_dimensions': 'list[list[float]]',
        'locked': 'bool',
        'page_count': 'float',
        'encrypt_pdfs': 'bool',
        'webhook_url': 'str',
        'embed_domains': 'list[str]',
        'parent_folder_id': 'str',
        'allow_additional_properties': 'bool',
        'encrypt_pdfs_password': 'str',
        'public_submissions': 'bool',
        'shared_field_data': 'object',
        'document_md5': 'str',
        'first_template': 'bool',
        'defaults': 'Template1Defaults',
        'editable_submissions': 'bool',
        'expire_submissions': 'bool',
        'name': 'str',
        'footer_html': 'str',
        'document_parse_error': 'bool',
        'fields': 'object',
        'document_filename': 'str',
        'redirect_url': 'str',
        'document_url': 'str'
    }

    attribute_map = {
        'document_processed': 'document_processed',
        'expiration_interval': 'expiration_interval',
        'scss': 'scss',
        'document_state': 'document_state',
        'expire_after': 'expire_after',
        'description': 'description',
        'slack_webhook_url': 'slack_webhook_url',
        'demo': 'demo',
        'path': 'path',
        'header_html': 'header_html',
        'public_web_form': 'public_web_form',
        'field_order': 'field_order',
        'permanent_document_url': 'permanent_document_url',
        'html': 'html',
        'template_type': 'template_type',
        'id': 'id',
        'page_dimensions': 'page_dimensions',
        'locked': 'locked',
        'page_count': 'page_count',
        'encrypt_pdfs': 'encrypt_pdfs',
        'webhook_url': 'webhook_url',
        'embed_domains': 'embed_domains',
        'parent_folder_id': 'parent_folder_id',
        'allow_additional_properties': 'allow_additional_properties',
        'encrypt_pdfs_password': 'encrypt_pdfs_password',
        'public_submissions': 'public_submissions',
        'shared_field_data': 'shared_field_data',
        'document_md5': 'document_md5',
        'first_template': 'first_template',
        'defaults': 'defaults',
        'editable_submissions': 'editable_submissions',
        'expire_submissions': 'expire_submissions',
        'name': 'name',
        'footer_html': 'footer_html',
        'document_parse_error': 'document_parse_error',
        'fields': 'fields',
        'document_filename': 'document_filename',
        'redirect_url': 'redirect_url',
        'document_url': 'document_url'
    }

    def __init__(self, document_processed=None, expiration_interval=None, scss=None, document_state=None, expire_after=None, description=None, slack_webhook_url=None, demo=None, path=None, header_html=None, public_web_form=None, field_order=None, permanent_document_url=None, html=None, template_type=None, id=None, page_dimensions=None, locked=None, page_count=None, encrypt_pdfs=None, webhook_url=None, embed_domains=None, parent_folder_id=None, allow_additional_properties=None, encrypt_pdfs_password=None, public_submissions=None, shared_field_data=None, document_md5=None, first_template=None, defaults=None, editable_submissions=None, expire_submissions=None, name=None, footer_html=None, document_parse_error=None, fields=None, document_filename=None, redirect_url=None, document_url=None):  # noqa: E501
        """Template1 - a model defined in OpenAPI"""  # noqa: E501

        self._document_processed = None
        self._expiration_interval = None
        self._scss = None
        self._document_state = None
        self._expire_after = None
        self._description = None
        self._slack_webhook_url = None
        self._demo = None
        self._path = None
        self._header_html = None
        self._public_web_form = None
        self._field_order = None
        self._permanent_document_url = None
        self._html = None
        self._template_type = None
        self._id = None
        self._page_dimensions = None
        self._locked = None
        self._page_count = None
        self._encrypt_pdfs = None
        self._webhook_url = None
        self._embed_domains = None
        self._parent_folder_id = None
        self._allow_additional_properties = None
        self._encrypt_pdfs_password = None
        self._public_submissions = None
        self._shared_field_data = None
        self._document_md5 = None
        self._first_template = None
        self._defaults = None
        self._editable_submissions = None
        self._expire_submissions = None
        self._name = None
        self._footer_html = None
        self._document_parse_error = None
        self._fields = None
        self._document_filename = None
        self._redirect_url = None
        self._document_url = None
        self.discriminator = None

        if document_processed is not None:
            self.document_processed = document_processed
        if expiration_interval is not None:
            self.expiration_interval = expiration_interval
        self.scss = scss
        if document_state is not None:
            self.document_state = document_state
        if expire_after is not None:
            self.expire_after = expire_after
        self.description = description
        self.slack_webhook_url = slack_webhook_url
        if demo is not None:
            self.demo = demo
        if path is not None:
            self.path = path
        self.header_html = header_html
        if public_web_form is not None:
            self.public_web_form = public_web_form
        if field_order is not None:
            self.field_order = field_order
        self.permanent_document_url = permanent_document_url
        self.html = html
        if template_type is not None:
            self.template_type = template_type
        if id is not None:
            self.id = id
        self.page_dimensions = page_dimensions
        if locked is not None:
            self.locked = locked
        if page_count is not None:
            self.page_count = page_count
        if encrypt_pdfs is not None:
            self.encrypt_pdfs = encrypt_pdfs
        self.webhook_url = webhook_url
        self.embed_domains = embed_domains
        self.parent_folder_id = parent_folder_id
        if allow_additional_properties is not None:
            self.allow_additional_properties = allow_additional_properties
        self.encrypt_pdfs_password = encrypt_pdfs_password
        if public_submissions is not None:
            self.public_submissions = public_submissions
        if shared_field_data is not None:
            self.shared_field_data = shared_field_data
        self.document_md5 = document_md5
        if first_template is not None:
            self.first_template = first_template
        if defaults is not None:
            self.defaults = defaults
        if editable_submissions is not None:
            self.editable_submissions = editable_submissions
        if expire_submissions is not None:
            self.expire_submissions = expire_submissions
        self.name = name
        self.footer_html = footer_html
        if document_parse_error is not None:
            self.document_parse_error = document_parse_error
        if fields is not None:
            self.fields = fields
        self.document_filename = document_filename
        self.redirect_url = redirect_url
        self.document_url = document_url

    @property
    def document_processed(self):
        """Gets the document_processed of this Template1.  # noqa: E501


        :return: The document_processed of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._document_processed

    @document_processed.setter
    def document_processed(self, document_processed):
        """Sets the document_processed of this Template1.


        :param document_processed: The document_processed of this Template1.  # noqa: E501
        :type: bool
        """

        self._document_processed = document_processed

    @property
    def expiration_interval(self):
        """Gets the expiration_interval of this Template1.  # noqa: E501


        :return: The expiration_interval of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._expiration_interval

    @expiration_interval.setter
    def expiration_interval(self, expiration_interval):
        """Sets the expiration_interval of this Template1.


        :param expiration_interval: The expiration_interval of this Template1.  # noqa: E501
        :type: str
        """
        allowed_values = ["minutes", "hours", "days"]  # noqa: E501
        if expiration_interval not in allowed_values:
            raise ValueError(
                "Invalid value for `expiration_interval` ({0}), must be one of {1}"  # noqa: E501
                .format(expiration_interval, allowed_values)
            )

        self._expiration_interval = expiration_interval

    @property
    def scss(self):
        """Gets the scss of this Template1.  # noqa: E501


        :return: The scss of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._scss

    @scss.setter
    def scss(self, scss):
        """Sets the scss of this Template1.


        :param scss: The scss of this Template1.  # noqa: E501
        :type: str
        """

        self._scss = scss

    @property
    def document_state(self):
        """Gets the document_state of this Template1.  # noqa: E501


        :return: The document_state of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._document_state

    @document_state.setter
    def document_state(self, document_state):
        """Sets the document_state of this Template1.


        :param document_state: The document_state of this Template1.  # noqa: E501
        :type: str
        """

        self._document_state = document_state

    @property
    def expire_after(self):
        """Gets the expire_after of this Template1.  # noqa: E501


        :return: The expire_after of this Template1.  # noqa: E501
        :rtype: float
        """
        return self._expire_after

    @expire_after.setter
    def expire_after(self, expire_after):
        """Sets the expire_after of this Template1.


        :param expire_after: The expire_after of this Template1.  # noqa: E501
        :type: float
        """

        self._expire_after = expire_after

    @property
    def description(self):
        """Gets the description of this Template1.  # noqa: E501


        :return: The description of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Template1.


        :param description: The description of this Template1.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def slack_webhook_url(self):
        """Gets the slack_webhook_url of this Template1.  # noqa: E501


        :return: The slack_webhook_url of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._slack_webhook_url

    @slack_webhook_url.setter
    def slack_webhook_url(self, slack_webhook_url):
        """Sets the slack_webhook_url of this Template1.


        :param slack_webhook_url: The slack_webhook_url of this Template1.  # noqa: E501
        :type: str
        """

        self._slack_webhook_url = slack_webhook_url

    @property
    def demo(self):
        """Gets the demo of this Template1.  # noqa: E501


        :return: The demo of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._demo

    @demo.setter
    def demo(self, demo):
        """Sets the demo of this Template1.


        :param demo: The demo of this Template1.  # noqa: E501
        :type: bool
        """

        self._demo = demo

    @property
    def path(self):
        """Gets the path of this Template1.  # noqa: E501


        :return: The path of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this Template1.


        :param path: The path of this Template1.  # noqa: E501
        :type: str
        """

        self._path = path

    @property
    def header_html(self):
        """Gets the header_html of this Template1.  # noqa: E501


        :return: The header_html of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._header_html

    @header_html.setter
    def header_html(self, header_html):
        """Sets the header_html of this Template1.


        :param header_html: The header_html of this Template1.  # noqa: E501
        :type: str
        """

        self._header_html = header_html

    @property
    def public_web_form(self):
        """Gets the public_web_form of this Template1.  # noqa: E501


        :return: The public_web_form of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._public_web_form

    @public_web_form.setter
    def public_web_form(self, public_web_form):
        """Sets the public_web_form of this Template1.


        :param public_web_form: The public_web_form of this Template1.  # noqa: E501
        :type: bool
        """

        self._public_web_form = public_web_form

    @property
    def field_order(self):
        """Gets the field_order of this Template1.  # noqa: E501


        :return: The field_order of this Template1.  # noqa: E501
        :rtype: list[list[float]]
        """
        return self._field_order

    @field_order.setter
    def field_order(self, field_order):
        """Sets the field_order of this Template1.


        :param field_order: The field_order of this Template1.  # noqa: E501
        :type: list[list[float]]
        """

        self._field_order = field_order

    @property
    def permanent_document_url(self):
        """Gets the permanent_document_url of this Template1.  # noqa: E501


        :return: The permanent_document_url of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._permanent_document_url

    @permanent_document_url.setter
    def permanent_document_url(self, permanent_document_url):
        """Sets the permanent_document_url of this Template1.


        :param permanent_document_url: The permanent_document_url of this Template1.  # noqa: E501
        :type: str
        """

        self._permanent_document_url = permanent_document_url

    @property
    def html(self):
        """Gets the html of this Template1.  # noqa: E501


        :return: The html of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._html

    @html.setter
    def html(self, html):
        """Sets the html of this Template1.


        :param html: The html of this Template1.  # noqa: E501
        :type: str
        """

        self._html = html

    @property
    def template_type(self):
        """Gets the template_type of this Template1.  # noqa: E501


        :return: The template_type of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._template_type

    @template_type.setter
    def template_type(self, template_type):
        """Sets the template_type of this Template1.


        :param template_type: The template_type of this Template1.  # noqa: E501
        :type: str
        """

        self._template_type = template_type

    @property
    def id(self):
        """Gets the id of this Template1.  # noqa: E501


        :return: The id of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Template1.


        :param id: The id of this Template1.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def page_dimensions(self):
        """Gets the page_dimensions of this Template1.  # noqa: E501


        :return: The page_dimensions of this Template1.  # noqa: E501
        :rtype: list[list[float]]
        """
        return self._page_dimensions

    @page_dimensions.setter
    def page_dimensions(self, page_dimensions):
        """Sets the page_dimensions of this Template1.


        :param page_dimensions: The page_dimensions of this Template1.  # noqa: E501
        :type: list[list[float]]
        """

        self._page_dimensions = page_dimensions

    @property
    def locked(self):
        """Gets the locked of this Template1.  # noqa: E501


        :return: The locked of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._locked

    @locked.setter
    def locked(self, locked):
        """Sets the locked of this Template1.


        :param locked: The locked of this Template1.  # noqa: E501
        :type: bool
        """

        self._locked = locked

    @property
    def page_count(self):
        """Gets the page_count of this Template1.  # noqa: E501


        :return: The page_count of this Template1.  # noqa: E501
        :rtype: float
        """
        return self._page_count

    @page_count.setter
    def page_count(self, page_count):
        """Sets the page_count of this Template1.


        :param page_count: The page_count of this Template1.  # noqa: E501
        :type: float
        """

        self._page_count = page_count

    @property
    def encrypt_pdfs(self):
        """Gets the encrypt_pdfs of this Template1.  # noqa: E501


        :return: The encrypt_pdfs of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._encrypt_pdfs

    @encrypt_pdfs.setter
    def encrypt_pdfs(self, encrypt_pdfs):
        """Sets the encrypt_pdfs of this Template1.


        :param encrypt_pdfs: The encrypt_pdfs of this Template1.  # noqa: E501
        :type: bool
        """

        self._encrypt_pdfs = encrypt_pdfs

    @property
    def webhook_url(self):
        """Gets the webhook_url of this Template1.  # noqa: E501


        :return: The webhook_url of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, webhook_url):
        """Sets the webhook_url of this Template1.


        :param webhook_url: The webhook_url of this Template1.  # noqa: E501
        :type: str
        """

        self._webhook_url = webhook_url

    @property
    def embed_domains(self):
        """Gets the embed_domains of this Template1.  # noqa: E501


        :return: The embed_domains of this Template1.  # noqa: E501
        :rtype: list[str]
        """
        return self._embed_domains

    @embed_domains.setter
    def embed_domains(self, embed_domains):
        """Sets the embed_domains of this Template1.


        :param embed_domains: The embed_domains of this Template1.  # noqa: E501
        :type: list[str]
        """

        self._embed_domains = embed_domains

    @property
    def parent_folder_id(self):
        """Gets the parent_folder_id of this Template1.  # noqa: E501


        :return: The parent_folder_id of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._parent_folder_id

    @parent_folder_id.setter
    def parent_folder_id(self, parent_folder_id):
        """Sets the parent_folder_id of this Template1.


        :param parent_folder_id: The parent_folder_id of this Template1.  # noqa: E501
        :type: str
        """

        self._parent_folder_id = parent_folder_id

    @property
    def allow_additional_properties(self):
        """Gets the allow_additional_properties of this Template1.  # noqa: E501


        :return: The allow_additional_properties of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._allow_additional_properties

    @allow_additional_properties.setter
    def allow_additional_properties(self, allow_additional_properties):
        """Sets the allow_additional_properties of this Template1.


        :param allow_additional_properties: The allow_additional_properties of this Template1.  # noqa: E501
        :type: bool
        """

        self._allow_additional_properties = allow_additional_properties

    @property
    def encrypt_pdfs_password(self):
        """Gets the encrypt_pdfs_password of this Template1.  # noqa: E501


        :return: The encrypt_pdfs_password of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._encrypt_pdfs_password

    @encrypt_pdfs_password.setter
    def encrypt_pdfs_password(self, encrypt_pdfs_password):
        """Sets the encrypt_pdfs_password of this Template1.


        :param encrypt_pdfs_password: The encrypt_pdfs_password of this Template1.  # noqa: E501
        :type: str
        """

        self._encrypt_pdfs_password = encrypt_pdfs_password

    @property
    def public_submissions(self):
        """Gets the public_submissions of this Template1.  # noqa: E501


        :return: The public_submissions of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._public_submissions

    @public_submissions.setter
    def public_submissions(self, public_submissions):
        """Sets the public_submissions of this Template1.


        :param public_submissions: The public_submissions of this Template1.  # noqa: E501
        :type: bool
        """

        self._public_submissions = public_submissions

    @property
    def shared_field_data(self):
        """Gets the shared_field_data of this Template1.  # noqa: E501


        :return: The shared_field_data of this Template1.  # noqa: E501
        :rtype: object
        """
        return self._shared_field_data

    @shared_field_data.setter
    def shared_field_data(self, shared_field_data):
        """Sets the shared_field_data of this Template1.


        :param shared_field_data: The shared_field_data of this Template1.  # noqa: E501
        :type: object
        """

        self._shared_field_data = shared_field_data

    @property
    def document_md5(self):
        """Gets the document_md5 of this Template1.  # noqa: E501


        :return: The document_md5 of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._document_md5

    @document_md5.setter
    def document_md5(self, document_md5):
        """Sets the document_md5 of this Template1.


        :param document_md5: The document_md5 of this Template1.  # noqa: E501
        :type: str
        """

        self._document_md5 = document_md5

    @property
    def first_template(self):
        """Gets the first_template of this Template1.  # noqa: E501


        :return: The first_template of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._first_template

    @first_template.setter
    def first_template(self, first_template):
        """Sets the first_template of this Template1.


        :param first_template: The first_template of this Template1.  # noqa: E501
        :type: bool
        """

        self._first_template = first_template

    @property
    def defaults(self):
        """Gets the defaults of this Template1.  # noqa: E501


        :return: The defaults of this Template1.  # noqa: E501
        :rtype: Template1Defaults
        """
        return self._defaults

    @defaults.setter
    def defaults(self, defaults):
        """Sets the defaults of this Template1.


        :param defaults: The defaults of this Template1.  # noqa: E501
        :type: Template1Defaults
        """

        self._defaults = defaults

    @property
    def editable_submissions(self):
        """Gets the editable_submissions of this Template1.  # noqa: E501


        :return: The editable_submissions of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._editable_submissions

    @editable_submissions.setter
    def editable_submissions(self, editable_submissions):
        """Sets the editable_submissions of this Template1.


        :param editable_submissions: The editable_submissions of this Template1.  # noqa: E501
        :type: bool
        """

        self._editable_submissions = editable_submissions

    @property
    def expire_submissions(self):
        """Gets the expire_submissions of this Template1.  # noqa: E501


        :return: The expire_submissions of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._expire_submissions

    @expire_submissions.setter
    def expire_submissions(self, expire_submissions):
        """Sets the expire_submissions of this Template1.


        :param expire_submissions: The expire_submissions of this Template1.  # noqa: E501
        :type: bool
        """

        self._expire_submissions = expire_submissions

    @property
    def name(self):
        """Gets the name of this Template1.  # noqa: E501


        :return: The name of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Template1.


        :param name: The name of this Template1.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def footer_html(self):
        """Gets the footer_html of this Template1.  # noqa: E501


        :return: The footer_html of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._footer_html

    @footer_html.setter
    def footer_html(self, footer_html):
        """Sets the footer_html of this Template1.


        :param footer_html: The footer_html of this Template1.  # noqa: E501
        :type: str
        """

        self._footer_html = footer_html

    @property
    def document_parse_error(self):
        """Gets the document_parse_error of this Template1.  # noqa: E501


        :return: The document_parse_error of this Template1.  # noqa: E501
        :rtype: bool
        """
        return self._document_parse_error

    @document_parse_error.setter
    def document_parse_error(self, document_parse_error):
        """Sets the document_parse_error of this Template1.


        :param document_parse_error: The document_parse_error of this Template1.  # noqa: E501
        :type: bool
        """

        self._document_parse_error = document_parse_error

    @property
    def fields(self):
        """Gets the fields of this Template1.  # noqa: E501


        :return: The fields of this Template1.  # noqa: E501
        :rtype: object
        """
        return self._fields

    @fields.setter
    def fields(self, fields):
        """Sets the fields of this Template1.


        :param fields: The fields of this Template1.  # noqa: E501
        :type: object
        """

        self._fields = fields

    @property
    def document_filename(self):
        """Gets the document_filename of this Template1.  # noqa: E501


        :return: The document_filename of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._document_filename

    @document_filename.setter
    def document_filename(self, document_filename):
        """Sets the document_filename of this Template1.


        :param document_filename: The document_filename of this Template1.  # noqa: E501
        :type: str
        """

        self._document_filename = document_filename

    @property
    def redirect_url(self):
        """Gets the redirect_url of this Template1.  # noqa: E501


        :return: The redirect_url of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._redirect_url

    @redirect_url.setter
    def redirect_url(self, redirect_url):
        """Sets the redirect_url of this Template1.


        :param redirect_url: The redirect_url of this Template1.  # noqa: E501
        :type: str
        """

        self._redirect_url = redirect_url

    @property
    def document_url(self):
        """Gets the document_url of this Template1.  # noqa: E501


        :return: The document_url of this Template1.  # noqa: E501
        :rtype: str
        """
        return self._document_url

    @document_url.setter
    def document_url(self, document_url):
        """Sets the document_url of this Template1.


        :param document_url: The document_url of this Template1.  # noqa: E501
        :type: str
        """

        self._document_url = document_url

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Template1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
