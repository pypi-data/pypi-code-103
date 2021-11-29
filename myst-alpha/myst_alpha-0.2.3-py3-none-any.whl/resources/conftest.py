from typing import Any, Dict, Generator

import pytest
from respx import MockRouter

import myst
from myst.auth.credentials import FakeCredentials


@pytest.fixture(scope="module", autouse=True)
def use_fake_credentials() -> None:
    myst.set_client(myst.Client(credentials=FakeCredentials()))


@pytest.fixture
def mock_api() -> Generator[MockRouter, None, None]:
    with MockRouter(base_url="https://api.myst.ai/v1alpha2/") as mock_router:
        yield mock_router


@pytest.fixture
def example_project() -> Dict[str, Any]:
    return dict(
        object="Project",
        uuid="7c1ccecc-f03b-4f33-95bf-581ee96a900e",
        create_time="2021-09-15T23:35:00Z",
        update_time=None,
        organization="f02caef7-07a4-4c47-8901-9680c2124f2e",
        organization_sharing_enabled=False,
        owner="e4769980-e154-4b10-96b7-ca9f72671843",
        title="uncontradictious-crassina-talemonger-euphroe",
        description="Some test project.",
        creator="e4769980-e154-4b10-96b7-ca9f72671843",
        deploy_status="NEW",
    )


@pytest.fixture
def example_source(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="b13ffa7b-1bf2-4ed5-bf96-8701df9e1b1c",
        create_time="2021-09-15T22:36:17Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="Source",
        title="Forecasted Weather in SF",
        description=None,
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        connector_uuid="1aeaadec-6912-422a-a4fc-5d6765391c17",
        parameters=dict(latitude=37.7948, longitude=-122.3986, fields=["relativeHumidity", "temperature"]),
    )


@pytest.fixture
def example_model(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="36cad5b7-6ea8-4e08-9546-d28218e2486f",
        create_time="2021-09-15T22:36:35Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="Model",
        title="An XGBoost Model",
        description=None,
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        connector_uuid="b78ff94a-27b1-4986-a88a-536661239bb2",
        parameters=dict(
            num_boost_round=10,
            max_depth=6,
            min_child_weight=1,
            learning_rate=0.3,
            subsample=1.0,
            colsample_bytree=1.0,
            colsample_bylevel=1.0,
            colsample_bynode=1.0,
            gamma=0.0,
            reg_alpha=0.0,
            reg_lambda=1.0,
        ),
    )


@pytest.fixture
def example_operation(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="d0f21c98-b6c5-42ba-98c8-6d336f6be4be",
        create_time="2021-09-15T22:36:30Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="Operation",
        title="3H Rolling Mean",
        description="Takes a rolling mean of the upstream series",
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        connector_uuid="e4bebd6d-d9d2-4103-8c94-95fa162eddc0",
        parameters=dict(
            rolling_window_parameters=dict(
                window_period="PT3H", min_periods=1, centered=False, aggregation_function="mean"
            ),
            differencing_parameters=None,
            shift_parameters=None,
        ),
    )


@pytest.fixture
def example_time_series(example_project: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Node",
        uuid="221c85ec-0bf1-477c-a820-ce0da7dd6f04",
        create_time="2021-09-15T22:36:42Z",
        update_time=None,
        organization="99799474-bc23-4026-ae88-89471a077b69",
        owner="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        type="TimeSeries",
        title="The thing we want to predict",
        description="This is a time series",
        project=example_project["uuid"],
        creator="fb80ae8a-dc73-45f3-9a49-ca57202b8fdf",
        deploy_status="NEW",
        sample_period="PT1H",
        cell_shape=[2, 3],
        coordinate_labels=[["x1", "x2"], ["y1", "y2", "y3"]],
        axis_labels=["x", "y"],
    )


@pytest.fixture
def example_model_input(example_model: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Edge",
        uuid="ceb01ff3-badf-4829-9322-911168d502aa",
        create_time="2021-09-15T22:36:36Z",
        update_time=None,
        type="Input",
        downstream_node=example_model["uuid"],
        upstream_node="e6af86ed-850c-484d-898e-72a53b4ffe7f",
        output_index=0,
        label_indexer=None,
        group_name="features",
    )


@pytest.fixture
def example_operation_input(example_operation: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Edge",
        uuid="8046a461-b58d-40fe-ae4a-079ff2f9c213",
        create_time="2021-09-15T22:36:31Z",
        update_time=None,
        type="Input",
        downstream_node=example_operation["uuid"],
        upstream_node="d4d750fe-f727-4073-b6d9-8c643476ac93",
        output_index=0,
        label_indexer=None,
        group_name="operands",
    )


@pytest.fixture
def example_layer(example_time_series: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        object="Edge",
        uuid="e09ee995-1aaa-4ad3-b91a-925b8f0a4679",
        create_time="2021-09-15T22:36:44Z",
        update_time=None,
        type="Layer",
        downstream_node=example_time_series["uuid"],
        upstream_node="36cad5b7-6ea8-4e08-9546-d28218e2486f",
        output_index=0,
        label_indexer=None,
        order=0,
        start_timing=None,
        end_timing=None,
    )
