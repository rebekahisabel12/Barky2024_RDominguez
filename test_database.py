# the database module is much more testable as its actions are largely atomic
# that said, the database module could certain be refactored to achieve decoupling
# in fact, either the implementation of the Unit of Work or just changing to sqlalchemy would be good.

# my edits
import pytest
from database import add_bookmark, Bookmark, list_bookmarks
from unittest.mock import MagicMock, patch, call


@pytest.fixture
def mock_session():
    with patch('database.Session') as mock:
        yield mock.return_value


def test_add_bookmark(mock_session):
    captured_bookmark = None

    def capture_bookmark(bookmark):
        nonlocal captured_bookmark
        captured_bookmark = bookmark

    mock_session.add.side_effect = capture_bookmark

    add_bookmark("Test Title", "http://example.com", "Test Notes")

    assert captured_bookmark == Bookmark(
        title="Test Title", url="http://example.com", notes="Test Notes"
    )


def test_list_bookmarks(mock_session):

    mock_query = mock_session.query.return_value

    mock_query.order_by.return_value.all.return_value = [
        Bookmark(id=1, title="Bookmark 1",
                 url="http://example.com/1", notes="Notes 1"),
        Bookmark(id=2, title="Bookmark 2",
                 url="http://example.com/2", notes="Notes 2"),
    ]

    list_bookmarks(order_by='date_added')

    mock_query.order_by.assert_called_once_with('date_added')
    mock_query.order_by.return_value.all.assert_called_once()
