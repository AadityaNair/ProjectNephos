from typing import List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import sessionmaker, validates

Base = declarative_base()


class Channel(Base):
    """
    Define a particular channel.
    This uses the conventions used in the old recording module.
    """
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True)
    name = Column(String(1200), unique=True, nullable=False)
    ip_string = Column(String(128))

    meta_teletext_page = Column(String(128))
    meta_country_code = Column(String(16))
    meta_language_code = Column(String(16))
    meta_timezone = Column(String(128))
    meta_video_source = Column(String(1200))

    def __repr__(self):
        return "<Channel (Name: {}, IP: {})>".format(self.name, self.ip_string)


class Permission(Base):
    """
    Stores all permissions.
    """
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True)
    tag = Column(String(1200))
    role = Column(String(16))
    email = Column(String(128))

    def __repr__(self):
        return "<Permission: <{}>, <{}>, <{}>>".format(self.tag, self.role, self.email)

    @validates("role")
    def validate_role(self, _, role):
        assert role in ["owner", "reader", "writer", "commenter"]
        return role


class DBStorage(object):
    """
    This class encompasses all our interactions with the database.
    This will connect to the SQL database and perform operations.
    """

    def __init__(self, config):
        self.config = config

        db_file = "sqlite:///" + config["recording", "db_location"]
        self.engine = create_engine(db_file)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()

    def add_permissions(
        self, tags: List[str], email: str, role: str = "reader"
    ) -> None:
        """
        Store permissions. Permissions are of the form of (tag, mail, role) tuple.
        This means that all files uploaded with `tag` will be shared with `mail` and
        the role will be set to `role`.

        It creates a new record for each of the tag provided.

        Takes:
            List of tags that the user wants access to.
            Email ID of the user
            Optional role. Default is only being able to read.
        """
        for tag in tags:
            entry = Permission(tag=tag, email=email, role=role)
            self.session.add(entry)
        self.session.commit()

    def get_permissions_from_tag(self, tag: str) -> List[Tuple[str, str]]:
        """
        Get all the users that should be able to access the provided tag.

        Takes:
            A tag.
        Returns:
            A list with (email, role) tuples
        """
        response = self.session.query(Permission).filter(Permission.tag == tag)
        return [(x.email, x.role) for x in response]

    def get_all_permissions(self) -> List[Tuple[str, str, str]]:
        """
        Same as get_permission_from_tag but without any filtering.

        Returns:
             A list with (tag, email, role) tuples ordered by tag
        """
        response = self.session.query(Permission).order_by(Permission.tag)
        return [(x.tag, x.email, x.role) for x in response]

    def add_channel(self, name: str, ip: str):
        """
        Add a new channel to record. Currently not using most of the columns
        mentioned in Channel

        Takes:
            name of the channel.
            IP of the channel
        """

        entry = Channel(name=name, ip_string=ip)
        self.session.add(entry)
        self.session.commit()

    def get_channels(self) -> List[Tuple[str, str]]:
        response = self.session.query(Channel).order_by(Channel.name)
        return [(x.name, x.ip_string) for x in response]
