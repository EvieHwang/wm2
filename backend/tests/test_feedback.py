"""Tests for the feedback module."""

import pytest
from unittest.mock import MagicMock, patch

from src.feedback.keywords import extract_keywords, tokenize, STOPWORDS
from src.feedback.retrieval import get_relevant_feedback, format_feedback_for_prompt


class TestTokenize:
    """Tests for tokenize function."""

    def test_basic_tokenization(self):
        result = tokenize("Hello World")
        assert result == ["hello", "world"]

    def test_removes_punctuation(self):
        result = tokenize("Hello, World! How are you?")
        assert result == ["hello", "world", "how", "are", "you"]

    def test_handles_numbers(self):
        result = tokenize("Box 10x8x4 inches")
        assert result == ["box", "10x8x4", "inches"]

    def test_empty_string(self):
        result = tokenize("")
        assert result == []

    def test_lowercase_conversion(self):
        result = tokenize("UPPERCASE lowercase MixedCase")
        assert result == ["uppercase", "lowercase", "mixedcase"]


class TestExtractKeywords:
    """Tests for extract_keywords function."""

    def test_filters_stopwords(self):
        result = extract_keywords("This is a product with the box")
        assert "this" not in result
        assert "is" not in result
        assert "a" not in result

    def test_filters_short_words(self):
        result = extract_keywords("I am a to go do")
        # All words are either stopwords or too short
        assert result == []

    def test_extracts_meaningful_keywords(self):
        result = extract_keywords("Sony headphones wireless bluetooth")
        assert "sony" in result
        assert "headphones" in result
        assert "wireless" in result
        assert "bluetooth" in result

    def test_max_keywords_limit(self):
        result = extract_keywords(
            "keyword1 keyword2 keyword3 keyword4 keyword5 keyword6 keyword7 keyword8 keyword9 keyword10 keyword11",
            max_keywords=5
        )
        assert len(result) <= 5

    def test_deduplicates_keywords(self):
        result = extract_keywords("headphones headphones headphones sony sony")
        assert result.count("headphones") == 1
        assert result.count("sony") == 1

    def test_empty_input(self):
        result = extract_keywords("")
        assert result == []

    def test_none_input(self):
        result = extract_keywords(None)
        assert result == []

    def test_preserves_order(self):
        result = extract_keywords("first second third fourth fifth")
        assert result[0] == "first"
        assert result[1] == "second"


class TestGetRelevantFeedback:
    """Tests for get_relevant_feedback function."""

    @patch('src.feedback.retrieval.get_recent_feedback')
    @patch('src.feedback.retrieval.get_feedback_by_keywords')
    def test_combines_recent_and_keyword_matches(self, mock_keyword, mock_recent):
        mock_recent.return_value = [
            {"id": "1", "description": "Recent item"},
            {"id": "2", "description": "Another recent"},
        ]
        mock_keyword.return_value = [
            {"id": "3", "description": "Keyword match"},
        ]

        result = get_relevant_feedback("test description")

        # Keyword matches should come first, then recent
        assert result[0]["id"] == "3"
        assert len(result) == 3

    @patch('src.feedback.retrieval.get_recent_feedback')
    @patch('src.feedback.retrieval.get_feedback_by_keywords')
    def test_deduplicates_results(self, mock_keyword, mock_recent):
        mock_recent.return_value = [
            {"id": "1", "description": "Duplicate item"},
        ]
        mock_keyword.return_value = [
            {"id": "1", "description": "Duplicate item"},  # Same ID
        ]

        result = get_relevant_feedback("test")

        # Should only have one entry with id "1"
        assert len([r for r in result if r["id"] == "1"]) == 1

    @patch('src.feedback.retrieval.get_recent_feedback')
    @patch('src.feedback.retrieval.get_feedback_by_keywords')
    def test_respects_max_entries(self, mock_keyword, mock_recent):
        mock_recent.return_value = [{"id": str(i)} for i in range(20)]
        mock_keyword.return_value = []

        result = get_relevant_feedback("test", max_entries=5)

        assert len(result) <= 5


class TestFormatFeedbackForPrompt:
    """Tests for format_feedback_for_prompt function."""

    def test_empty_list_returns_empty_string(self):
        result = format_feedback_for_prompt([])
        assert result == ""

    def test_formats_correct_feedback(self):
        feedback = [
            {
                "description": "Sony headphones",
                "classification": "SMALL_BIN",
                "is_correct": True,
            }
        ]
        result = format_feedback_for_prompt(feedback)

        assert "SMALL_BIN" in result
        assert "confirmed correct" in result
        assert "Sony headphones" in result

    def test_formats_incorrect_feedback(self):
        feedback = [
            {
                "description": "Large TV",
                "classification": "TOTE",
                "is_correct": False,
            }
        ]
        result = format_feedback_for_prompt(feedback)

        assert "TOTE" in result
        assert "incorrect" in result.lower()
        assert "Large TV" in result

    def test_truncates_long_descriptions(self):
        long_desc = "A" * 150
        feedback = [
            {
                "description": long_desc,
                "classification": "TOTE",
                "is_correct": True,
            }
        ]
        result = format_feedback_for_prompt(feedback)

        # Should be truncated to 100 chars with "..."
        assert "..." in result
        assert long_desc not in result  # Full string shouldn't appear


class TestValidateFeedbackRequest:
    """Tests for feedback request validation in handler."""

    def test_missing_description(self):
        from src.handler import validate_feedback_request
        body = {"classification": "TOTE", "is_correct": True}
        result, error = validate_feedback_request(body)

        assert result is None
        assert error is not None
        assert "description" in error.message.lower()

    def test_missing_classification(self):
        from src.handler import validate_feedback_request
        body = {"description": "Test product", "is_correct": True}
        result, error = validate_feedback_request(body)

        assert result is None
        assert error is not None
        assert "classification" in error.message.lower()

    def test_missing_is_correct(self):
        from src.handler import validate_feedback_request
        body = {"description": "Test product", "classification": "TOTE"}
        result, error = validate_feedback_request(body)

        assert result is None
        assert error is not None
        assert "is_correct" in error.message.lower()

    def test_invalid_classification(self):
        from src.handler import validate_feedback_request
        body = {
            "description": "Test product",
            "classification": "INVALID",
            "is_correct": True
        }
        result, error = validate_feedback_request(body)

        assert result is None
        assert error is not None
        assert "invalid classification" in error.message.lower()

    def test_valid_request(self):
        from src.handler import validate_feedback_request
        body = {
            "description": "Test product",
            "classification": "TOTE",
            "is_correct": True
        }
        result, error = validate_feedback_request(body)

        assert error is None
        assert result is not None
        assert result["description"] == "Test product"
        assert result["classification"] == "TOTE"
        assert result["is_correct"] is True

    def test_is_correct_must_be_boolean(self):
        from src.handler import validate_feedback_request
        body = {
            "description": "Test product",
            "classification": "TOTE",
            "is_correct": "yes"  # String, not boolean
        }
        result, error = validate_feedback_request(body)

        assert result is None
        assert error is not None
        assert "boolean" in error.message.lower()
