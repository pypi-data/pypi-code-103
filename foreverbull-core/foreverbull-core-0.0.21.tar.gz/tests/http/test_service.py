import pytest
import requests
import requests_mock

from foreverbull_core.http import RequestError
from foreverbull_core.http.service import Service
from foreverbull_core.models import service


@pytest.fixture(scope="function")
def service_session():
    def setup():
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount("http://", adapter)
        service = Service("127.0.0.1:8080", session=session)
        return service, adapter

    return setup


def test_list_services(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services", json=[])
    assert service_api.list() == []


def test_list_services_negative(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services", status_code=500)

    with pytest.raises(RequestError, match="get call /services gave bad return code: 500"):
        service_api.list()


def test_create_service(service_session):
    service_api, adapter = service_session()
    stored = service.Service(
        id="service_id", name="demo_service", image="service_image", type=service.ServiceType.WORKER
    )
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/services", json=stored.dict())
    assert service_api.create(stored) == stored


def test_create_service_negative(service_session):
    service_api, adapter = service_session()
    stored = service.Service(
        id="service_id", name="demo_service", image="service_image", type=service.ServiceType.WORKER
    )
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/services", status_code=500)

    with pytest.raises(RequestError, match="post call /services gave bad return code: 500"):
        service_api.create(stored)


def test_get_service(service_session):
    service_api, adapter = service_session()
    stored = service.Service(
        id="service_id", name="demo_service", image="service_image", type=service.ServiceType.WORKER
    )

    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services/service_id", json=stored.dict())
    assert service_api.get("service_id") == stored


def test_get_service_negative(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services/service_id", status_code=500)

    with pytest.raises(RequestError, match="get call /services/service_id gave bad return code: 500"):
        service_api.get("service_id")


def test_delete_service(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/services/service_id")
    assert service_api.delete("service_id") is None


def test_delete_service_negative(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/services/service_id", status_code=500)

    with pytest.raises(RequestError, match="delete call /services/service_id gave bad return code: 500"):
        service_api.delete("service_id")


def test_list_instances(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services/service_id/instances", json=[])
    assert service_api.list_instances("service_id") == []


def test_list_instances_negative(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services/s_id/instances", status_code=500)

    with pytest.raises(RequestError, match="get call /services/s_id/instances gave bad return code: 500"):
        service_api.list_instances("s_id")


def test_get_instance(service_session):
    service_api, adapter = service_session()
    stored = service.Instance(
        id="instance_id",
        service_id="service_id",
        session_id="session_id",
        host="host",
        port=1337,
        listen=True,
        online=True,
    )
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services/s_id/instances/i_id", json=stored.dict())
    assert service_api.get_instance("s_id", "i_id") == stored


def test_get_instance_negative(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/services/s_id/instances/i_id", status_code=500)

    with pytest.raises(RequestError, match="get call /services/s_id/instances/i_id gave bad return code: 500"):
        service_api.get_instance("s_id", "i_id")


def test_delete_instance(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/services/s_id/instances/i_id")
    assert service_api.delete_instance("s_id", "i_id") is None


def test_delete_instance_negative(service_session):
    service_api, adapter = service_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/services/s_id/instances/i_id", status_code=500)

    with pytest.raises(RequestError, match="delete call /services/s_id/instances/i_id gave bad return code: 500"):
        service_api.delete_instance("s_id", "i_id")
