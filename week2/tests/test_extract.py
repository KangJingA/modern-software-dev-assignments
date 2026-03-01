import json
import os
from unittest.mock import MagicMock, patch

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def _fake_chat_response(items: list[str]) -> MagicMock:
    mock = MagicMock()
    mock.message.content = json.dumps({"items": items})
    return mock


def test_llm_bullet_list():
    with patch("week2.app.services.extract.chat", return_value=_fake_chat_response(["Fix login bug", "Deploy to prod"])):
        result = extract_action_items_llm("- Fix login bug\n- Deploy to prod")
    assert "Fix login bug" in result
    assert "Deploy to prod" in result


def test_llm_keyword_prefixed():
    with patch("week2.app.services.extract.chat", return_value=_fake_chat_response(["Update README", "Review PR"])):
        result = extract_action_items_llm("todo: Update README\naction: Review PR")
    assert "Update README" in result
    assert "Review PR" in result


def test_llm_empty_input():
    with patch("week2.app.services.extract.chat", return_value=_fake_chat_response([])):
        result = extract_action_items_llm("")
    assert result == []


def test_llm_plain_prose():
    with patch("week2.app.services.extract.chat", return_value=_fake_chat_response(["Investigate the crash"])):
        result = extract_action_items_llm("The server went down last night. Someone should look into it.")
    assert "Investigate the crash" in result


@pytest.mark.integration
def test_llm_integration_bullet_list():
    result = extract_action_items_llm("- Fix login bug\n- Deploy to prod")
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.integration
def test_llm_integration_keyword_prefixed():
    result = extract_action_items_llm("todo: Update README\naction: Review PR")
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.integration
def test_llm_integration_empty_input():
    result = extract_action_items_llm("")
    assert isinstance(result, list)


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items
