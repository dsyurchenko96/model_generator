from app.models.main_model import MainModel

class TestPostDocument:
    def test_post_document(self, test_client, db_session):
        document = MainModel(
            kind="test",
            name="test",
            version="v1.0.0",
            description="test",
            configuration={
                "settings": {},
                "specification": {}
            },
        )
        response = test_client.post("/kind", json=document.dict())
        assert response.status_code == 201