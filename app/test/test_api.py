import json
from copy import deepcopy
from uuid import uuid4

from app.models.app_model import StateEnum

valid_json = {
    "kind": "test",
    "name": "test",
    "version": "1.0.0",
    "description": "test",
    "configuration": {"settings": {}, "specification": {}},
}


class TestPostDocument:
    def test_valid_data(self, test_client, db_session):
        response = test_client.post("/kind", json=valid_json)
        assert response.status_code == 201

    def test_invalid_version(self, test_client, db_session):
        json = deepcopy(valid_json)
        json["version"] = "1.0"
        response = test_client.post("/kind", json=json)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"].startswith("string does not match regex")

    def test_extra_fields(self, test_client, db_session):
        json = deepcopy(valid_json)
        json["configuration"]["extra_field"] = "test"
        response = test_client.post("/kind", json=json)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "extra fields not permitted"

    def test_empty_data(self, test_client, db_session):
        response = test_client.post("/kind", json={})
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"

    def test_empty_fields(self, test_client, db_session):
        json = deepcopy(valid_json)
        json["kind"] = ""
        response = test_client.post("/kind", json=json)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "ensure this value has at least 1 characters"

    def test_missing_fields(self, test_client, db_session):
        json = deepcopy(valid_json)
        json.pop("kind")
        response = test_client.post("/kind", json=json)
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"


class TestDeleteDocument:
    def test_valid_data(self, test_client, db_session):
        print(valid_json)
        post_response = test_client.post("/kind", json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        delete_response = test_client.delete(f"/kind/{uuid}")
        assert delete_response.status_code == 204

    def test_invalid_data(self, test_client, db_session):
        response = test_client.delete(f"/kind/{uuid4()}")
        assert response.status_code == 404


class TestGetDocument:
    def test_valid_data(self, test_client, db_session):
        post_response = test_client.post("/kind", json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        get_response = test_client.get(f"/kind/{uuid}")
        assert get_response.status_code == 200

    def test_invalid_data(self, test_client, db_session):
        response = test_client.get(f"/kind/{uuid4()}")
        assert response.status_code == 404


class TestGetDocumentState:
    def test_valid_data(self, test_client, db_session):
        post_response = test_client.post("/kind", json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        get_response = test_client.get(f"/kind/{uuid}/state")
        assert get_response.status_code == 200

    def test_invalid_data(self, test_client, db_session):
        response = test_client.get(f"/kind/{uuid4()}/state")
        assert response.status_code == 404


class TestPutDocumentState:
    def test_valid_state(self, test_client, db_session):
        post_response = test_client.post("/kind", json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"/kind/{uuid}/state", params={"state": StateEnum.RUNNING.name})
        print(put_response.json())
        assert put_response.status_code == 200
        assert put_response.json().get("state") == StateEnum.RUNNING.name

    def test_invalid_state(self, test_client, db_session):
        post_response = test_client.post("/kind", json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"/kind/{uuid}/state", params={"state": "invalid"})
        print(put_response.json())
        assert put_response.status_code == 400

    def test_valid_state_invalid_uuid(self, test_client, db_session):
        put_response = test_client.put(f"/kind/{uuid4()}/state", params={"state": StateEnum.RUNNING.name})
        print(put_response.json())
        assert put_response.status_code == 404


class TestPutDocumentConfig:
    def test_valid_config(self, test_client, db_session):
        post_response = test_client.post("/kind", json=valid_json)
        print("the post response is:\n", post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        config = {
            "settings": {"settingA": "valueA", "settingB": "valueB"},
            "specification": {"specificationA": "valueA", "specificationB": "valueB"},
        }
        put_response = test_client.put(f"/kind/{uuid}/configuration", json=config)
        print("the put response is:\n", put_response.json())
        assert put_response.status_code == 200
        json_dict = json.loads(put_response.json().get("json"))
        assert json_dict["configuration"] == config

    def test_invalid_config(self, test_client, db_session):
        post_response = test_client.post("/kind", json=valid_json)
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        put_response = test_client.put(f"/kind/{uuid}/configuration", json={"json": {"invalid": "invalid"}})
        print(put_response.json())
        assert put_response.status_code == 400

    def test_valid_config_invalid_uuid(self, test_client, db_session):
        config = {
            "settings": {"settingA": "valueA", "settingB": "valueB"},
            "specification": {"specificationA": "valueA", "specificationB": "valueB"},
        }
        put_response = test_client.put(f"/kind/{uuid4()}/configuration", json={"json": config})
        print(put_response.json())
        assert put_response.status_code == 400
