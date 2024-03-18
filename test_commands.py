# how would I test Barky?
# First, I wouldn't test barky, I would test the reusable modules barky relies on:
# commands.py and database.py

# we will use pytest: https://docs.pytest.org/en/stable/index.html

# should we test quit? No, its behavior is self-evident and not logic dependent
from unittest.mock import MagicMock
from commands import ListBookmarksCommand
import pytest
from unittest.mock import MagicMock, patch
from commands import EditBookmarkCommand, ListBookmarksCommand
from database import Bookmark


@pytest.fixture
def mock_session():
    with patch('commands.Session') as mock:
        yield mock.return_value


def test_edit_bookmark_url(mock_session):
    data = {"id": 1, "update": {"url": "https://duckduckgo.com/"}}

    old_url = "https://www.google.com"
    bookmark = Bookmark(id=1, url=old_url)

    mock_session.query.return_value.filter_by.return_value.first.return_value = bookmark

    command = EditBookmarkCommand()
    result = command.execute(data)

    assert bookmark.url == "https://duckduckgo.com/"
    assert result == "Bookmark updated!"


def test_list_bookmarks_by_title(mock_session):
    mock_session.query().order_by().all.return_value = [
        MagicMock(title="Bookmark A"),
        MagicMock(title="Bookmark B"),
        MagicMock(title="Bookmark C")
    ]

    command = ListBookmarksCommand(order_by="title")
    bookmarks = command.execute()

    assert [bookmark.title for bookmark in bookmarks] == [
        "Bookmark A", "Bookmark B", "Bookmark C"]


def test_list_bookmarks_by_date(mock_session):
    mock_session.query().order_by().all.return_value = [
        MagicMock(date_added="2024-01-01"),
        MagicMock(date_added="2024-01-02"),
        MagicMock(date_added="2024-01-03")
    ]

    command = ListBookmarksCommand(order_by="date_added")
    bookmarks = command.execute()

    assert [bookmark.date_added for bookmark in bookmarks] == [
        "2024-01-01", "2024-01-02", "2024-01-03"]

# okay, should I test the other commands?
# not really, they are tighly coupled with sqlite3 and its use in the database.py module
