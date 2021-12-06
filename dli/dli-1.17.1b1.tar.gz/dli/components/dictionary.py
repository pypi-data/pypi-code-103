from dli.models.dictionary_model import DictionaryModel

from platform_services_lib.lib.context.urls import dataset_urls


class Dictionary:

    def register_dictionary(
        self,
        dataset_id,
        version,
        valid_as_of,
        fields,
        **kwargs
    ):
        """
        Registers dictionary metadata for a dataset.

        :param str dataset_id: Id of the dataset for the dictionary.
        :param str version: A user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: The date as of which the dictionary is active.
                               Expected format is YYYY-MM-DD. Must be unique.
        :param list[dict] fields: Non empty list of `Field` as described below.
        :param list[dict] partitions: Optional. Non empty list of `Partition` as described below.
        :param str description: Optional. Description for the dictionary.

        :returns: The registered dictionary

        Types
        =====

        Dictionary Field:

        .. code-block:: python

            {
                name	        string  - required
                type	        string  - required
                nullable        boolean - required
                metadata	dictionary
                description	string
                sample_value	string
                short_name	string
                is_derived	boolean
                validation	string
                comment	        string
            }

        Partition:

        .. code-block:: python

            {
                name: string,
                type: string
            }

        - **Sample**

        .. code-block:: python

                my_dictionary_fields = [
                            {
                                'name': 'field_1',
                                'type': 'String',
                                'nullable': False
                            },
                            {
                                'name': 'field_2',
                                'type': 'Double',
                                'nullable': False
                            },
                            {
                                'name': 'field_3',
                                'type': 'Int',
                                'nullable': True,
                                'metadata': {
                                    'some_key': 'some_value'
                                }
                            },
                        ]
                my_dictionary_partitions = [
                    {
                        'name': 'field_1',
                        'type': 'String'
                    }
                ]

                my_dictionary = client.register_dictionary(
                    "my-dataset-id",
                    version='1a',
                    valid_as_of='2018-10-31',
                    fields=my_dictionary_fields,
                    partitions=my_dictionary_partitions,
                    description="My dictionary description"
                )
        """
        payload = {
            'dataset_id': dataset_id,
            'version': version,
            'valid_as_of': valid_as_of,
            'fields': fields,
        }

        payload.update(**kwargs)

        response = self.session.post(
            dataset_urls.dictionary_index, json={'data': {'attributes': payload}}
        )

        return DictionaryModel(response.json()['data'], client=self)

    def get_dictionary(self, dataset_id, version=None):
        """
        Looks up dictionary for a dataset by version. In case version is not specified this will fetch dictionary version having the latest valid_as_of date.
        Throws exception if no dictionary is registered for the dataset.

        :param str dataset_id: The id of the dataset under which the dictionary is registered.
        :param str version: Optional. The version of the dictionary.

        :returns: The dictionary.

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                # Fetch dictionary version '1a'
                dictionary = client.get_dictionary('my_dataset_id', version='1a')

                # Fetch the dictionary with the latest valid_as_of date
                latest_dictionary = client.get_dictionary('my_dataset_id')

        """

        if version:
            schema = self.session.get(
                dataset_urls.v2_schema_instance_version.format(
                    id=dataset_id,
                    version=version
                )
            )
        else:
            schema = self.session.get(
                dataset_urls.dictionary_by_dataset_lastest.format(
                    id=dataset_id
                )
            )
        json = schema.json()['data']
        return DictionaryModel(json, client=self)

    def get_dictionaries(self, dataset_id, count=100):
        """
        Returns a list of all dictionaries registered under the dataset. The list is sorted by dictionary valid_as_of date in descending order.

        :param str dataset_id: The id of the dataset.
        :param int count: Optional count of dictionaries to be returned. Defaults to 100.

        :returns: List of all dictionaries registered under the dataset sorted by valid_as_of date in descending order.

        - **Sample**

        .. code-block:: python

                my_dictionaries = client.get_dictionaries("my_dataset_id", count=10)
        """
        response = self.session.get(
            dataset_urls.dictionary_by_dataset.format(id=dataset_id)
        )

        return [
            DictionaryModel(d, client=self) for d in
            response.json()['data']
        ][:count]  # todo - will kill this silly count stuff ASAP

    def delete_dictionary(self, dataset_id, version):
        """

        Marks a dictionary version for a dataset as deleted.

        :param str dataset_id: The id of the dataset under which the dictionary is registered.
        :param str version: The version of the dictionary.

        :returns: None

        - **Sample**

        .. code-block:: python

                # Delete dictionary version '1a'

                client = dli.connect()
                client.delete_dictionary(dataset_id='my_dataset_id', version='1a')

        """
        schema = self.get_dictionary(dataset_id, version)
        self.session.delete(
            dataset_urls.dictionary_instance.format(id=schema.id)
        )

    def edit_dictionary(
        self,
        dataset_id,
        version,
        new_version=None,
        **kwargs
    ):
        """
        Updates dictionary metadata for a dataset.
        If a field is passed as ``None`` then the field will not be updated.

        :param str dataset_id: Id of the dataset for the dictionary_instance.
        :param str version: Version of the dictionary being updated.
        :param str new_version: Optional. New version if to be updated. This is a user assigned version name/number. It should be unique within the dataset.
        :param str valid_as_of: Optional. The date as of which the dictionary is active.
                               Expected format is YYYY-MM-DD.
        :param list[dict] fields: Optional. If provided, a non empty list of `Field` as described below.
        :param list[dict] partitions: Optional. If provided, a non empty list of `Partition` as described below.
        :param str description: Optional. Description for the dictionary.

        .. code-block:: python

                # Field:
                {
                    "name": "field_a", 			# name of the column.
                    "nullable": True,  			# defaulted to True - A boolean indicating whether the field is nullable or not.
                    "metadata": None			# optional dictionary with metadata for this column.
                }

                # Partition:
                {
                    "name": "key1",
                    "type": "String"
                }

        :returns: The updated dictionary.
        :rtype: dli.models.dictionary_model.DictionaryModel

        - **Sample**

        .. code-block:: python

                # Updating description and valid_as_of date for my dictionary
                client = dli.connect()
                my_updated_schema = client.edit_dictionary(
                    "my-dataset-id",
                    '1a',
                    valid_as_of='2018-11-05',
                    description="My updated dictionary description"
                )
        """
        schema = self.get_dictionary(dataset_id, version)
        payload = dict(**kwargs)

        if new_version is not None:
            payload['version'] = new_version

        response = self.session.patch(
            dataset_urls.dictionary_instance.format(id=schema.id),
            json={'data': {'attributes': payload}}
        )

        return DictionaryModel(response.json()['data'], client=self)