import json
from copy import deepcopy
from uuid import uuid4

from app.models.app_model import StateEnum

valid_json = {
    "kind": "this is a test kind",
    "name": "and this is a test name",
    "version": "1.0.0",
    "description": "test",
    "configuration": {"settings": {}, "specification": {}},
}

endpoint = "/test"


class TestPostDocument:
    def test_valid_data(self, test_client, db_session):
        response = test_client.post(endpoint, json=valid_json)
        assert response.status_code == 201

    def test_invalid_version(self, test_client, db_session):
        json_copy = deepcopy(valid_json)
        json_copy["version"] = "1.0"
        response = test_client.post(endpoint, json=json_copy)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"].startswith("string does not match regex")

    def test_extra_fields(self, test_client, db_session):
        json_copy = deepcopy(valid_json)
        json_copy["configuration"]["extra_field"] = "test"
        response = test_client.post(endpoint, json=json_copy)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "extra fields not permitted"

    def test_empty_data(self, test_client, db_session):
        response = test_client.post(endpoint, json={})
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"

    def test_empty_fields(self, test_client, db_session):
        json_copy = deepcopy(valid_json)
        json_copy["kind"] = ""
        response = test_client.post(endpoint, json=json_copy)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"].startswith("ensure this value has at least") is True

    def test_missing_fields(self, test_client, db_session):
        json_copy = deepcopy(valid_json)
        json_copy.pop("kind")
        response = test_client.post(endpoint, json=json_copy)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"


class TestDeleteDocument:
    def test_valid_data(self, test_client, db_session):
        print(valid_json)
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        delete_response = test_client.delete(f"{endpoint}/{uuid}")
        assert delete_response.status_code == 204

    def test_invalid_data(self, test_client, db_session):
        response = test_client.delete(f"{endpoint}/{uuid4()}")
        assert response.status_code == 404


class TestGetDocument:
    def test_valid_data(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        get_response = test_client.get(f"{endpoint}/{uuid}")
        assert get_response.status_code == 200

    def test_invalid_data(self, test_client, db_session):
        response = test_client.get(f"{endpoint}/{uuid4()}")
        assert response.status_code == 404


class TestGetDocumentState:
    def test_valid_data(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        get_response = test_client.get(f"{endpoint}/{uuid}/state")
        assert get_response.status_code == 200

    def test_invalid_data(self, test_client, db_session):
        response = test_client.get(f"{endpoint}/{uuid4()}/state")
        assert response.status_code == 404


class TestPutDocumentState:
    def test_valid_state(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"{endpoint}/{uuid}/state", params={"state": StateEnum.RUNNING.name})
        print(put_response.json())
        assert put_response.status_code == 200
        assert put_response.json().get("state") == StateEnum.RUNNING.name

    def test_invalid_state(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"{endpoint}/{uuid}/state", params={"state": "invalid"})
        print(put_response.json())
        assert put_response.status_code == 400

    def test_valid_state_invalid_uuid(self, test_client, db_session):
        put_response = test_client.put(f"{endpoint}/{uuid4()}/state", params={"state": StateEnum.RUNNING.name})
        print(put_response.json())
        assert put_response.status_code == 404


class TestPutDocumentConfig:
    def test_valid_config(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print("the post response is:\n", post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        config_dict = {
            "settings": {"settingA": "valueA", "settingB": "valueB"},
            "specification": {"specificationA": "valueA", "specificationB": "valueB"},
        }
        put_response = test_client.put(f"{endpoint}/{uuid}/configuration", json=config_dict)
        print("the put response is:\n", put_response.json())
        assert put_response.status_code == 200
        json_dict = json.loads(put_response.json().get("json"))
        assert json_dict["configuration"] == config_dict

    def test_invalid_config(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"{endpoint}/{uuid}/configuration", json={"json": {"invalid": "invalid"}})
        print(put_response.json())
        assert put_response.status_code == 400

    def test_invalid_config_extra_field(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        config = {
            "settings": {"settingA": "valueA", "settingB": "valueB"},
            "specification": {"specificationA": "valueA", "specificationB": "valueB"},
            "extra": "extra",
        }
        put_response = test_client.put(f"{endpoint}/{uuid}/configuration", json=config)
        print(put_response.json())
        assert put_response.status_code == 400

    def test_invalid_config_missing_field(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        config = {
            "settings": {"settingA": "valueA", "settingB": "valueB"},
        }
        put_response = test_client.put(f"{endpoint}/{uuid}/configuration", json=config)
        print(put_response.json())
        assert put_response.status_code == 400

    def test_valid_config_invalid_uuid(self, test_client, db_session):
        config = {
            "settings": {"settingA": "valueA", "settingB": "valueB"},
            "specification": {"specificationA": "valueA", "specificationB": "valueB"},
        }
        put_response = test_client.put(f"{endpoint}/{uuid4()}/configuration", json={"json": config})
        print(put_response.json())
        assert put_response.status_code == 400


class TestPutDocumentSettings:
    def test_valid_settings(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        settings = {"settingA": "valueA", "settingB": "valueB"}
        put_response = test_client.put(f"{endpoint}/{uuid}/settings", json=settings)
        print(put_response.json())
        assert put_response.status_code == 200
        json_dict = json.loads(put_response.json().get("json"))
        assert json_dict["configuration"]["settings"] == settings

    def test_invalid_settings(self, test_client, db_session):
        post_response = test_client.post(endpoint, json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"{endpoint}/{uuid}/settings", json="invalid")
        print(put_response.json())
        assert put_response.status_code == 400

    def test_valid_settings_invalid_uuid(self, test_client, db_session):
        settings = {"settingA": "valueA", "settingB": "valueB"}
        put_response = test_client.put(f"{endpoint}/{uuid4()}/settings", json=settings)
        print(put_response.json())
        assert put_response.status_code == 404
