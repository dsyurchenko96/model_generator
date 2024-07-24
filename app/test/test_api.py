from app.models.main_model import MainModel

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
        assert response.status_code == 400
        assert response.json()["detail"].startswith("string does not match regex")
        print(response.json())

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
        assert response.status_code == 400
        assert response.json()["detail"] == "extra fields not permitted"
        print(response.json())

    def test_empty_data(self, test_client, db_session):
        response = test_client.post("/kind", json={})
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"
        print(response.json())

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
        assert response.status_code == 400
        assert response.json()["detail"] == "ensure this value has at least 1 characters"
        print(response.json())
    
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
        assert response.status_code == 400
        assert response.json()["detail"] == "field required"
        print(response.json())
