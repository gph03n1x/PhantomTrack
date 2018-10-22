from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    song_hash = Column(String)
    name = Column(String)
    location = Column(String)
    waves = Column(String)
    duration = Column(Integer)
    bars = Column(Integer)
    step = Column(Integer)


class MusicPaths(Base):
    __tablename__ = "music_paths"
    id = Column(Integer, primary_key=True)
    is_primary = Column(Boolean)
    path = Column(String)
