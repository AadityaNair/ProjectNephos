from typing import List, Tuple

from sqlalchemy import create_engine, ForeignKey, Boolean, event
from sqlalchemy.engine import Engine
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

    name = Column(String(1200), primary_key=True, nullable=False)
    ip_string = Column(String(128))

    # meta_teletext_page = Column(String(128))
    # meta_country_code = Column(String(16))
    # meta_language_code = Column(String(16))
    # meta_timezone = Column(String(128))
    # meta_video_source = Column(String(1200))

    def __repr__(self):
        return "<Channel (Name: {}, IP: {})>".format(self.name, self.ip_string)


class Job(Base):
    """
    Define jobs for each channel.
    This does not use the old conventions.
    """
    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    name = Column(String(1200), unique=True, nullable=False)
    channel = Column(String, ForeignKey("channel.name"))

    start = Column(String(16))
    duration = Column(Integer)

    convert_to = Column(String(8))
    upload = Column(Boolean)
    tags = Column(String(1200))

    # True if the jobs are already scheduled. False if they need to be scheduled.
    # Note that this field is ignored during the first run of the scheduler.
    in_execution = Column(Boolean)

    def __repr__(self):
        return "<Job: namne={}, channel={}, convert_to={}, upload={}, tags={}>".format(
            self.name, self.channel, self.convert_to, self.upload, self.tags
        )


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


class Download(Base):
    """
    Update this table whenever a download completes.
    This is associated with a job name. It retrieves metadata
    from the job.
    """
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)  # Full path to the filename
    jobname = Column(String, ForeignKey("job.name"))  # Associated Job

    def __repr__(self):
        return "<Download: {} ## {}>".format(self.filename, self.jobname)


class DBStorage(object):
    """
    This class encompasses all our interactions with the database.
    This will connect to the SQL database and perform operations.
    """

    def __init__(self, config):
        self.config = config

        db_file = "sqlite:///" + config["recording", "db_location"]
        self.engine = create_engine(db_file)

        self.engine.execute("pragma foreign_keys=ON;")

        Base.metadata.create_all(self.engine)

        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()

    @staticmethod
    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        """
        This is needed because SQLite by default doesn't enforce
        FOREIGN KEY Constraints. This enables them for every query.

        Ref:
            http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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

    def get_permissions(self, tag: str = None) -> List[Tuple[str, str, str]]:
        """
        Same as get_permission_from_tag but without any filtering.

        Returns:
             A list with (tag, email, role) tuples ordered by tag
        """
        if tag is None:
            response = self.session.query(Permission).order_by(Permission.tag)
        else:
            response = self.session.query(Permission).filter(Permission.tag == tag)
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

    def get_channels(self, name: str = None) -> List[Tuple[str, str]]:
        if name is None:
            response = self.session.query(Channel).order_by(Channel.name)
        else:
            response = self.session.query(Channel).filter(Channel.name == name)
        return [(x.name, x.ip_string) for x in response]

    def add_job(
        self,
        name: str,
        channel: str,
        start: str,
        duration: int,
        upload: bool,
        convert_to: str,
        tags: List[str],
    ):
        if tags:
            tagstring = ",".join(tags)
        else:
            tagstring = None
        entry = Job(
            name=name,
            channel=channel,
            start=start,
            duration=duration,
            upload=upload,
            convert_to=convert_to,
            tags=tagstring,
        )
        self.session.add(entry)
        self.session.commit()

    def get_job(self, jobname: str = None):
        if jobname is None:
            return self.session.query(Job).all()
        else:
            return self.session.query(Job).filter(Job.name == jobname).first()

    def pop_download(self):
        item = self.session.query(Download).first()
        if item is None:
            return None
        else:
            self.session.delete(item)
            self.session.commit()
            return item

    def _add_filename(self, filename, jobname):
        """
        Helper method to add files to Download table.
        This is for testing purposes only. IN production,
        this will be done by the recording module.
        :param filename:
        :param jobname:
        :return:
        """
        entry = Download(filename=filename, jobname=jobname)
        self.session.add(entry)
        self.session.commit()
