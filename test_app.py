import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app import app, search_with_serper, get_related_questions


client = TestClient(app)


class TestSearchWithSerper:
    """Tests for search_with_serper function"""

    @patch("app.requests.post")
    def test_search_with_serper_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "organic": [
                {"title": "Result 1", "link": "https://example.com/1", "snippet": "Snippet 1"},
                {"title": "Result 2", "link": "https://example.com/2", "snippet": "Snippet 2"},
            ]
        }
        mock_post.return_value = mock_response

        results = search_with_serper("test query", "fake_api_key")

        assert len(results) == 2
        assert results[0]["name"] == "Result 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["snippet"] == "Snippet 1"

    @patch("app.requests.post")
    def test_search_with_serper_with_knowledge_graph(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "knowledgeGraph": {
                "title": "Knowledge Title",
                "website": "https://kg.example.com",
                "description": "KG Description"
            },
            "organic": []
        }
        mock_post.return_value = mock_response

        results = search_with_serper("test query", "fake_api_key")

        assert len(results) == 1
        assert results[0]["name"] == "Knowledge Title"
        assert results[0]["snippet"] == "KG Description"

    @patch("app.requests.post")
    def test_search_with_serper_api_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(Exception):
            search_with_serper("test query", "fake_api_key")


class TestQueryEndpoint:
    """Tests for /query endpoint"""

    @patch("app.search_with_serper")
    @patch("app.get_openai_client")
    def test_query_endpoint_success(self, mock_client, mock_search):
        mock_search.return_value = [
            {"name": "Test", "url": "https://test.com", "snippet": "Test snippet"}
        ]
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(delta=MagicMock(content="Test answer"))]
        mock_client.return_value.chat.completions.create.return_value = iter([mock_completion])

        with patch.dict("os.environ", {"SERPER_SEARCH_API_KEY": "fake_key", "OPENAI_API_KEY": "fake_key"}):
            response = client.post("/query", json={
                "query": "test question",
                "search_uuid": "test-uuid"
            })

        assert response.status_code == 200

    def test_query_endpoint_missing_query(self):
        with patch.dict("os.environ", {"SERPER_SEARCH_API_KEY": "fake_key", "OPENAI_API_KEY": "fake_key"}):
            response = client.post("/query", json={
                "search_uuid": "test-uuid"
            })
        assert response.status_code == 422


class TestIndexEndpoint:
    """Tests for / endpoint"""

    def test_index_redirect(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/ui/index.html"


class TestGetRelatedQuestions:
    """Tests for get_related_questions function"""

    @patch("app.get_openai_client")
    def test_get_related_questions_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Question 1?\nQuestion 2?\nQuestion 3?"))]
        mock_client.return_value.chat.completions.create.return_value = mock_response

        with patch.dict("os.environ", {"OPENAI_API_KEY": "fake_key"}):
            questions = get_related_questions("test", [{"snippet": "context"}])

        assert len(questions) == 3

    @patch("app.get_openai_client")
    def test_get_related_questions_error_returns_empty(self, mock_client):
        mock_client.return_value.chat.completions.create.side_effect = Exception("API Error")

        with patch.dict("os.environ", {"OPENAI_API_KEY": "fake_key"}):
            questions = get_related_questions("test", [{"snippet": "context"}])

        assert questions == []
