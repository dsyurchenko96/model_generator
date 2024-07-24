from app.models.main_model import MainModel
from uuid import uuid4

class TestPostDocument:
    def test_valid_data(self, test_client, db_session):
        response = test_client.post("/kind", json=
            {
                "kind": "test",
                "name": "test",
                "version": "1.0.0",
                "description": "test",
                "configuration": {
                    "settings": {},
                    "specification": {}
                }
            }
        )
        assert response.status_code == 201

    def test_invalid_version(self, test_client, db_session):
        response = test_client.post("/kind", json=
            {
                "kind": "test",
                "name": "test",
                "version": "v1.0.0",
                "description": "test",
                "configuration": {
                    "settings": {},
                    "specification": {}
                }
            }
        )
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"].startswith("string does not match regex")
        

    def test_extra_fields(self, test_client, db_session):
        response = test_client.post("/kind", json=
            {
                "kind": "test",
                "name": "test",
                "version": "1.0.0",
                "description": "test",
                "configuration": {
                    "settings": {},
                    "specification": {},
                    "extra_field": "test"
                }
            }
        )
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "extra fields not permitted"
        

    def test_empty_data(self, test_client, db_session):
        response = test_client.post("/kind", json={})
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"
        

    def test_empty_fields(self, test_client, db_session):
        response = test_client.post("/kind", json=
            {
                "kind": "",
                "name": "test",
                "version": "1.0.0",
                "description": "test",
                "configuration": {
                    "settings": {},
                    "specification": {}
                }
            }
        )
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "ensure this value has at least 1 characters"
        
    
    def test_missing_fields(self, test_client, db_session):
        response = test_client.post("/kind", json=
            {
                "name": "test",
                "version": "1.0.0",
                "description": "test",
                "configuration": {
                    "settings": {},
                    "specification": {}
                }
            }
        )
        print(response.json())
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"
        
class TestDeleteDocument:
    def test_valid_data(self, test_client, db_session):
        post_response = test_client.post("/kind", json=
            {
                "kind": "test",
                "name": "test",
                "version": "1.0.0",
                "description": "test",
                "configuration": {
                    "settings": {},
                    "specification": {}
                }
            }
        )
        print(post_response.json())
        assert post_response.status_code == 201
        assert post_response.json() is not None
        uuid = post_response.json()
        delete_response = test_client.delete(f"/kind/{uuid}")
        assert delete_response.status_code == 204

    def test_invalid_data(self, test_client, db_session):
        response = test_client.delete(f"/kind/{uuid4()}")
        assert response.status_code == 404