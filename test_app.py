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


class TestStopWordsLimit:
    """Test that stop_words doesn't exceed OpenAI's limit of 4"""

    def test_stop_words_max_four(self):
        from app import stop_words
        assert len(stop_words) <= 4, f"stop_words has {len(stop_words)} items, max is 4"


class TestRelatedQuestionsFormat:
    """Test that related questions are formatted correctly for frontend"""

    @patch("app.search_with_serper")
    @patch("app.get_openai_client")
    @patch("app.executor")
    def test_related_questions_format(self, mock_executor, mock_client, mock_search):
        mock_search.return_value = [
            {"name": "Test", "url": "https://test.com", "snippet": "Test snippet"}
        ]
        
        # Mock LLM streaming response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(delta=MagicMock(content="Answer"))]
        mock_client.return_value.chat.completions.create.return_value = iter([mock_completion])
        
        # Mock related questions future
        mock_future = MagicMock()
        mock_future.result.return_value = ["1. Question one?", "2. Question two?"]
        mock_executor.submit.return_value = mock_future

        with patch.dict("os.environ", {"SERPER_SEARCH_API_KEY": "fake_key", "OPENAI_API_KEY": "fake_key"}):
            response = client.post("/query", json={
                "query": "test",
                "search_uuid": "test-uuid",
                "generate_related_questions": True
            })

        assert response.status_code == 200
        content = response.text
        
        if "__RELATED_QUESTIONS__" in content:
            related_part = content.split("__RELATED_QUESTIONS__")[1].strip()
            related_data = json.loads(related_part)
            # Check format is [{question: string}]
            for item in related_data:
                assert "question" in item, "Related question should have 'question' key"
                assert isinstance(item["question"], str), "Question should be a string"
                # Check numbering is stripped
                assert not item["question"].startswith("1."), "Numbering should be stripped"
                assert not item["question"].startswith("2."), "Numbering should be stripped"


class TestBranding:
    """Test that branding is Evidence Search, not Lepton"""

    def test_search_placeholder_branding(self):
        with open("web/src/app/components/search.tsx", "r") as f:
            content = f.read()
        assert "Evidence Search" in content, "Search placeholder should mention Evidence Search"
        assert "Lepton" not in content, "Search should not mention Lepton"

    def test_layout_title_branding(self):
        with open("web/src/app/layout.tsx", "r") as f:
            content = f.read()
        assert "Evidence Search" in content, "Page title should be Evidence Search"
        assert "Lepton" not in content, "Layout should not mention Lepton"

    def test_logo_branding(self):
        with open("web/src/app/components/logo.tsx", "r") as f:
            content = f.read()
        assert "Evidence Search" in content, "Logo should show Evidence Search"
        assert "Lepton Search" not in content, "Logo should not show Lepton Search"

    def test_footer_branding(self):
        with open("web/src/app/components/footer.tsx", "r") as f:
            content = f.read()
        assert "Lepton" not in content, "Footer should not mention Lepton"
