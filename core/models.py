from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('left_id', Integer, ForeignKey('playlists.id')),
    Column('right_id', Integer, ForeignKey('songs.id'))
)


class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    songs = relationship("Song", secondary=association_table, back_populates="playlists")


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
    playlists = relationship("Playlist", secondary=association_table, back_populates="songs")


class MusicPaths(Base):
    __tablename__ = "music_paths"
    id = Column(Integer, primary_key=True)
    is_primary = Column(Boolean, default=False)
    path = Column(String, unique=True)
