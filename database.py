'''
This module supports the following schema:

ID — The ID is the primary key of the table, or the main identifier of each record. It should automatically increment each time a new record is added, using the AUTOINCREMENT keyword. This column is an INTEGER type; the rest are TEXT.
Title — The title is required because it’s hard to skim your existing bookmarks if they’re only URLs. You can tell SQLite the column can’t be empty by using the NOT NULL keyword.
URL — The URL is required, so it gets NOT NULL as well.
Notes — Notes for a bookmark are optional, so only the TEXT specifier is necessary.
Date — The date the bookmark was added is required, so it gets NOT NULL.

SQL reference: https://www.w3schools.com/sql/default.asp

CREATE TABLE IF NOT EXISTS bookmarks
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    notes TEXT,
    date_added TEXT NOT NULL
);

'''

# My edits
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import sqlalchemy


engine = create_engine('sqlite:///bookmarks.db', echo=True)
Session = sessionmaker(bind=engine)
Base = sqlalchemy.orm.declarative_base()


class Bookmark(Base):
    __tablename__ = 'bookmarks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    notes = Column(String)
    date_added = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"ID: {self.id}, Title: {self.title}, URL: {self.url}, Notes: {self.notes}, Date Added: {self.date_added}"

    def __eq__(self, other):
        if not isinstance(other, Bookmark):
            return False
        return (
            self.title == other.title
            and self.url == other.url
            and self.notes == other.notes
            and self.date_added == other.date_added
        )


Base.metadata.create_all(engine)


def add_bookmark(title, url, notes=None):
    bookmark = Bookmark(title=title, url=url, notes=notes)

    session = Session()

    session.add(bookmark)

    session.commit()

    session.close()


def list_bookmarks(order_by='date_added'):
    session = Session()
    bookmarks = session.query(Bookmark).order_by(order_by).all()
    session.close()
    return bookmarks


def list_bookmarks(order_by='title'):
    session = Session()
    bookmarks = session.query(Bookmark).order_by(order_by).all()
    session.close()
    return bookmarks
