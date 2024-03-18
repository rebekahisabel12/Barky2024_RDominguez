"""
This module utilizes the command pattern - https://en.wikipedia.org/wiki/Command_pattern - to 
specify and implement the business logic layer
"""
import sys
from abc import ABC, abstractmethod
from datetime import datetime


from sqlalchemy.orm import sessionmaker
from database import Bookmark, engine
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime
from database import Base

Session = sessionmaker(bind=engine)


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        raise NotImplementedError(
            "A command must implement the execute method")


class CreateBookmarksTableCommand(Command):

    def execute(self, data=None):
        if 'bookmarks' not in Base.metadata.tables:
            class Bookmark(Base):
                __tablename__ = 'bookmarks'

                id = Column(Integer, primary_key=True)
                title = Column(String, nullable=False)
                url = Column(String, nullable=False)
                notes = Column(String)
                date_added = Column(DateTime, default=datetime.utcnow)

            Base.metadata.create_all(engine)
            print("Bookmarks table created successfully.")
        else:
            print("Bookmarks table already exists.")


class AddBookmarkCommand(Command):

    def execute(self, data, timestamp=None):
        # Create a new bookmark object
        bookmark = Bookmark(
            title=data["title"],
            url=data["url"],
            notes=data.get("notes"),
            date_added=datetime.utcnow(),
        )

        session = Session()

        session.add(bookmark)

        session.commit()

        session.close()

        return "Bookmark added!"


class ListBookmarksCommand(Command):

    def __init__(self, order_by="date_added"):
        self.order_by = order_by

    def execute(self, data=None):
        # Create a session
        session = Session()

        # Query bookmarks
        bookmarks = (
            session.query(Bookmark)
            .order_by(getattr(Bookmark, self.order_by))
            .all()
        )

        # Close the session
        session.close()

        return bookmarks


class DeleteBookmarkCommand(Command):
    """
    We also need to remove bookmarks.
    """

    def execute(self, data):
        # Create a session
        session = Session()

        # Delete the bookmark
        session.query(Bookmark).filter_by(id=data).delete()

        # Commit the transaction
        session.commit()

        # Close the session
        session.close()

        return "Bookmark deleted!"


class ImportGitHubStarsCommand(Command):
    """
    Import starred repos in Github - credit Dane Hillard
    """

    def _extract_bookmark_info(self, repo):
        return {
            "title": repo["name"],
            "url": repo["html_url"],
            "notes": repo["description"],
        }

    def execute(self, data):
        bookmarks_imported = 0

        github_username = data["github_username"]
        next_page_of_results = f"https://api.github.com/users/{github_username}/starred"
        while next_page_of_results:
            stars_response = requests.get(
                next_page_of_results,
                headers={"Accept": "application/vnd.github.v3.star+json"},
            )
            next_page_of_results = stars_response.links.get(
                "next", {}).get("url")

            for repo_info in stars_response.json():
                repo = repo_info["repo"]

                if data["preserve_timestamps"]:
                    timestamp = datetime.strptime(
                        repo_info["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                else:
                    timestamp = None

                bookmarks_imported += 1
                AddBookmarkCommand().execute(
                    self._extract_bookmark_info(repo),
                    timestamp=timestamp,
                )

        return f"Imported {bookmarks_imported} bookmarks from starred repos!"


class EditBookmarkCommand(Command):
    def execute(self, data):
        session = Session()

        bookmark_id = data["id"]
        updated_notes = data["update"]

        bookmark = session.query(Bookmark).filter_by(id=bookmark_id).first()

        if not bookmark:
            session.close()
            return "Bookmark not found!"

        if "title" in updated_notes:
            bookmark.title = updated_notes["title"]
        if "url" in updated_notes:
            bookmark.url = updated_notes["url"]
        if "notes" in updated_notes:
            bookmark.notes = updated_notes["notes"]

        session.commit()

        session.close()

        return "Bookmark updated!"


class QuitCommand(Command):
    def execute(self, data=None):
        sys.exit()
