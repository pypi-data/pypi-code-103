import contextlib

from platform_services_lib.lib.context.urls import dataset_urls
from platform_services_lib.lib.services.dlc_attributes_dict import AttributesDict


class SampleDataModel:
    def __init__(self, parent):
        self._parent = parent
        self._client = parent._client

    def schema(self):
        """
        Returns the schema data and first rows of sample data.

        :returns: attributes dictionary
        """
        response = self._client.session.get(
            dataset_urls.v2_sample_data_schema.format(id=self._parent.id)
        )

        return AttributesDict(**response.json()['data']['attributes'])

    @contextlib.contextmanager
    def file(self):
        """
        Get the sample data.
        The response type varies depending on whether the dataset is setup to return a static
        preview or a live preview.
        If the preview type is a static preview, then this function provides a file like object
        containing sample data.

        Example usage for static preview of a .parquet format file:

        .. code-block:: python

            >>> import pandas
            >>> import dli

            >>> client = dli.connect()

            >>> dataset = client.datasets.get('some-dataset-short-code')

            >>> with dataset.sample_data.file() as f:
            >>>    dataframe = pandas.read_parquet(f)

        Example usage for static preview of a .csv format file:

        .. code-block:: python

            >>> import pandas
            >>> import dli

            >>> client = dli.connect()

            >>> dataset = client.datasets.get('some-dataset-short-code')

            >>> with dataset.sample_data.file() as f:
            >>>    dataframe = pandas.read_csv(f)

        Else if the preview type is a live preview, then this function provides a HTTP response
        that needs to be wrapped for pandas to be able to read

        Example usage for live preview of a .parquet format file:

        .. code-block:: python

            >>> import pandas
            >>> import dli
            >>> import io

            >>> client = dli.connect()

            >>> dataset = client.datasets.get('some-dataset-short-code')

            >>> with dataset.sample_data.file() as f:
            >>>     dataframe = pd.read_parquet(io.BytesIO(f.read()))

        Example usage for live preview of a .parquet format file:

        .. code-block:: python

            >>> import pandas
            >>> import dli
            >>> import io

            >>> client = dli.connect()

            >>> dataset = client.datasets.get('some-dataset-short-code')

            >>> with dataset.sample_data.file() as f:
            >>>     dataframe = pd.read_csv(io.BytesIO(f.read()))
        """
        response = self._client.session.get(
            dataset_urls.v2_sample_data_file.format(id=self._parent.id),
            stream=True
        )
        # otherwise you get raw secure
        response.raw.decode_content = True
        yield response.raw
        response.close()

