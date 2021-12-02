"""
   SDC Query helper module
"""
import copy
import inspect
import os
import json
from datetime import datetime
import boto3
from sqlalchemy import create_engine, and_, literal
from sqlalchemy.orm import sessionmaker, undefer, Query
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import with_expression
import sdc_helpers.utils as utils
import sdc_helpers.decorators as decorators
from sdc_helpers.models.audit import Audit
from sdc_helpers.models.client import Client
from sdc_helpers.models.model import Model
from sdc_helpers.models.process import Process
from sdc_helpers.models.service import Service
from sdc_helpers.models.subscription import Subscription
from sdc_helpers.redis_helper import RedisHelper


class QueryHelper:
    """
        Query helper class
    """
    # pylint: disable=too-few-public-methods, singleton-comparison, no-member

    session = None
    redis_helper = None
    mysql_date_format = '%Y-%m-%d %H:%M:%S'
    query_helper_caller = None
    process_id = None

    def __init__(self, **kwargs):
        """
            Init a new QueryHelper obj
            kwargs:
                rds_config (dict) : config arguments for mysql connector
                redis_config (dict) : config arguments for redis connector
        """
        caller_locals = inspect.currentframe().f_back.f_locals
        if caller_locals.get('self') is not None:
            caller_module = caller_locals['self'].__module__
            caller_class = caller_locals['self'].__class__.__name__
        else:
            caller_module = caller_locals.get('__module__')
            caller_class = caller_locals.get('__qualname__')

        self.query_helper_caller = caller_module

        if caller_class is not None:
            self.query_helper_caller = '{caller_module}.{caller_class}'.format(
                caller_module=caller_module,
                caller_class=caller_class
            )

        # get rds config
        rds_config = kwargs.get('rds_config', {})
        rds_host = rds_config.get('host', None)
        rds_user = rds_config.get('username', None)
        rds_password = rds_config.get('password', None)
        rds_port = rds_config.get('port', None)
        rds_db = rds_config.get('db', None)

        # get redis config
        redis_config = kwargs.get('redis_config', {})
        redis_host = redis_config.get('host', None)
        redis_port = redis_config.get('port', None)
        redis_db = redis_config.get('db', None)
        # temporary fix - these should be passed at init time
        if rds_host is None:
            rds_host = os.getenv('RDS_HOST', 'localhost')
        # temporary fix - these should be passed at init time
        if rds_user is None:
            rds_user = os.getenv('RDS_USERNAME', 'root')
        # temporary fix - these should be passed at init time
        if rds_password is None:
            rds_password = os.getenv('RDS_PASSWORD')
        # temporary fix - these should be passed at init time
        if rds_port is None:
            rds_port = int(os.getenv('RDS_PORT', '3306'))
        # temporary fix - these should be passed at init time
        if rds_db is None:
            rds_db = os.getenv('RDS_DB_NAME', 'sdc')

        user_password = rds_user
        if rds_password is not None:
            user_password = '{user}:{password}'.format(
                user=rds_user,
                password=rds_password
            )

        engine = create_engine(
            'mysql+pymysql://{user_password}@{host}:{port}/{db}'.format(
                user_password=user_password,
                host=rds_host,
                port=rds_port,
                db=rds_db
            )
        )

        self.session = sessionmaker(bind=engine)()

        # instantiate a redis helper
        self.redis_helper = RedisHelper(host=redis_host, port=redis_port, db=redis_db)

    def __del__(self):
        self.session.close()
        del self.redis_helper

    def get_query(
            self,
            model_class,
            for_update: bool = False,
            no_wait: bool = False
    ) -> Query:
        """
            Get a query for a model class

            args:
                model_class: The model class to query on
                for_update (bool): Reserve the model for exclusive use until
                                   commit or session is closed - Default False
                no_wait (bool): Don't wait around for a model if it is locked
            return:
                query (Query) : Return a SQLAlchemy Query object

        """
        # Check that the supplied class has an ancestor which is our base Model
        if Model not in model_class.__mro__:
            raise Exception('Please supply a SQLAlchemy model class to build a query')

        query = self.session.query(model_class).options(
            with_expression(
                model_class.for_update,
                literal(for_update)
            )
        )

        if for_update:
            query = query.with_for_update(nowait=no_wait)

        return query

    @decorators.query_exception_handler()
    def get_clients(self) -> list:
        """
            Get all the clients from the database

        return:
            clients (list) : Returns a list of all active Client models from the database

        """
        clients = self.get_query(Client).filter(
            Client.deleted_at == None
        ).all()

        return clients

    @decorators.query_exception_handler()
    def get_client(
            self,
            *,
            from_cache: bool = True,
            **kwargs
    ) -> Client:
        """
            Get the specified client from cache or database

            args:
                from_cache (bool): Retrieve the client from cache - Default True
                kwargs (dict):
                    api_key_id (str): The AWS API Gateway API Key Id
                    client_id (int): ID of the client in the database

            return:
                client (Client) : Returns the specified Client model

        """
        api_key_id = kwargs.get('api_key_id')
        client_id = kwargs.get('client_id')

        if not api_key_id and not client_id:
            raise Exception('ClientError: api_key_id or id is required for this function')

        if api_key_id and client_id:
            raise Exception(
                'ClientError: Only one of api_key_id or id should be specified for this function'
            )

        if api_key_id:
            client_redis_key = 'client-{api_key_id}'.format(api_key_id=api_key_id)
        else:
            client_redis_key = 'client-{client_id}'.format(client_id=client_id)

        client_redis = self.redis_helper.redis_get(key=client_redis_key)

        if (
                not from_cache or
                not client_redis
        ):
            query = self.get_query(Client)

            if api_key_id:
                client = boto3.client('apigateway')
                api_key = client.get_api_key(apiKey=api_key_id)

                if 'tags' not in api_key or 'client_code' not in api_key['tags']:
                    raise Exception(
                        ('ClientError: client_code not set up for this API key. '
                         'Please contact support'
                        )
                    )

                client = query.filter(
                    and_(
                        Client.code == utils.dict_query(
                            dictionary=api_key,
                            path='tags.client_code'
                        ),
                        Client.deleted_at == None
                    )
                ).first()
            else:
                client = query.filter(
                    and_(
                        Client.id == client_id,
                        Client.deleted_at == None
                    )
                ).first()

            if client is not None:
                self.redis_helper.redis_set(
                    key=client_redis_key,
                    value=json.dumps(client.to_dict(), default=str)
                )
        else:
            client_dict = json.loads(client_redis)
            client = Client(**client_dict)

        return client

    @decorators.query_exception_handler()
    def get_services(self) -> list:
        """
            Get all the services from the database

        return:
            services (list) : Returns a list of all active Service models from the database

        """
        services = self.get_query(Service).filter(
            Service.deleted_at == None
        ).all()

        return services

    @decorators.query_exception_handler()
    def get_service(self, *, slug: str, from_cache: bool = True) -> Service:
        """
            Get the specified service from cache or database

            args:
                slug (str): slug of the service in the database
                from_cache (bool): Retrieve the service from cache - Default True

            return:
                service (Service) : Returns the specified Service model

        """
        service_redis_key = 'service-{slug}'.format(slug=slug)
        service_redis = self.redis_helper.redis_get(key=service_redis_key)

        if (
                not from_cache or
                not service_redis
        ):
            service = self.get_query(Service).filter(
                and_(
                    Service.slug == slug,
                    Service.deleted_at == None
                )
            ).first()

            if service:
                self.redis_helper.redis_set(
                    key=service_redis_key,
                    value=json.dumps(service.to_dict(), default=str)
                )
        else:
            service_dict = json.loads(service_redis)
            service = Service(**service_dict)

        return service

    @decorators.query_exception_handler()
    def get_subscription(
            self,
            *,
            client_id: int,
            service_id: int,
            from_cache: bool = True,
            for_update: bool = False
    ) -> Subscription:
        """
            Get the specified subscription from cache or database

            args:
                client_id (id): client_id of the subscription in the database
                service_id (id): service_id of the subscription in the database
                from_cache (bool): Retrieve the subscription from cache - Default True
                for_update (bool): Reserve the subscription for exclusive use until
                                   commit or session is closed - Default False

            return:
                subscription (Subscription) : Returns the specified Subscription model

        """
        subscription_redis_key = (
            'subscription-{client_id}-{service_id}'.format(
                client_id=client_id,
                service_id=service_id
            )
        )
        subscription_redis = self.redis_helper.redis_get(
            key=subscription_redis_key
        )

        if (
                not from_cache or
                not subscription_redis
        ):
            query = self.get_query(Subscription, for_update).filter(
                and_(
                    Subscription.client_id == client_id,
                    Subscription.service_id == service_id,
                    Subscription.deleted_at == None
                )
            )

            subscription = query.first()

            if subscription:
                self.redis_helper.redis_set(
                    key=subscription_redis_key,
                    value=json.dumps(subscription.to_dict(), default=str)
                )
        else:
            subscription_dict = json.loads(subscription_redis)
            subscription = Subscription(**subscription_dict)

        return subscription

    @decorators.query_exception_handler()
    def get_subscriptions(self, *, service_id: int) -> list:
        """
            Get all the specified service's subscriptions from the database

            args:
                service_id (id): service_id of the subscription in the database

            return:
                subscriptions (list) : Returns the specified service's Subscription models

        """
        return self.get_query(Subscription, for_update=True).filter(
            and_(
                Subscription.service_id == service_id,
                Subscription.deleted_at == None
            )
        ).options(
            undefer('properties')
        ).all()

    @decorators.query_exception_handler()
    def get_process(self, *, slug: str, from_cache: bool = True) -> Process:
        """
            Get the specified process from cache or database

            args:
                slug (str): slug of the process in the database
                from_cache (bool): Retrieve the process from cache - Default True

            return:
                process (Process) : Returns the specified Process model

        """
        process_redis_key = 'process-{slug}'.format(slug=slug)
        process_redis = self.redis_helper.redis_get(key=process_redis_key)

        if (
                not from_cache or
                not process_redis
        ):
            process = self.get_query(Process).filter(
                and_(
                    Process.slug == slug,
                    Process.deleted_at == None
                )
            ).first()

            if process:
                self.redis_helper.redis_set(
                    key=process_redis_key,
                    value=json.dumps(process.to_dict(), default=str)
                )
        else:
            process_dict = json.loads(process_redis)
            process = Process(**process_dict)

        return process

    @decorators.query_exception_handler()
    def update(self, *, model: Model, audit: bool = True):
        """
            Commit the model's changes to the database

            Note:
                If any other changes have been made to other models, those would
                be committed too. It is the developer's responsibility to ensure
                that their workflow doesn't run into this issue

            args:
                model (Model): The model being updated
                audit (bool): Whether to create an audit for the update or not
        """
        if not model.for_update:
            raise Exception('ServerError: Cannot update a read only model')

        if hasattr(model, 'properties'):
            # If properties have only been partially modified,
            # e.g `subscription.properties['node1'][0][node2] = value`,
            # the properties attribute is not marked as dirty and we
            # need to mark it as such to cause an update in the database
            flag_modified(model, 'properties')

        now = datetime.strftime(
            datetime.now(),
            self.mysql_date_format
        )

        old_values = {}
        new_values = {}

        ignore_attributes = ['updated_at']

        original = set(utils.flatten_dict(model.original).items())
        new = set(utils.flatten_dict(model.to_dict()).items())

        for key, value in original.difference(new):
            if key in ignore_attributes:
                continue
            old_values[key] = value

        for key, value in new.difference(original):
            if key in ignore_attributes:
                continue
            new_values[key] = value

        if bool(old_values) or bool(new_values):
            if audit:
                if self.process_id is None:
                    raise Exception('Server Error: Process not set in QueryHelper for audits')

                fields = {
                    'user_type': 'Sdc\\Models\\Process',
                    'user_id': self.process_id,
                    'event': 'updated',
                    'auditable_type': 'Sdc\\Models\\{class_name}'.format(
                        class_name=model.__class__.__name__
                    ),
                    'auditable_id': model.id,
                    'old_values': old_values,
                    'new_values': new_values,
                    'created_at': now,
                    'updated_at': now
                }

                audit = Audit(**fields)
                self.session.add(audit)

            model.updated_at = now

            if hasattr(model, 'updated_by') and self.query_helper_caller is not None:
                model.updated_by = self.query_helper_caller

            self.session.commit()
            model.original = copy.deepcopy(model.to_dict())
