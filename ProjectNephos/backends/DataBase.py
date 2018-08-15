from sqlalchemy import create_engine, ForeignKey, Boolean, event, or_
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

    is_up = Column(Boolean, default=True)

    def __repr__(self):
        return "<Channel (Name: {}, IP: {}, UP: {})>".format(
            self.name, self.ip_string, self.is_up
        )


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
    subtitles = Column(Boolean)
    upload = Column(Boolean)
    tags = Column(String(1200))

    # True if the jobs are already scheduled. False if they need to be scheduled.
    # Note that this field is ignored during the first run of the scheduler.
    in_execution = Column(Boolean)

    def __repr__(self):
        return "<Job: namne={}, channel={}, convert_to={}, upload={}, tags={}>".format(
            self.name, self.channel, self.convert_to, self.upload, self.tags
        )


class Schedule(Base):
    """
    Store the schedules for all configured channels.
    This is a manual step and not yet performed automatically
    """
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True)

    channel = Column(String, ForeignKey("channel.name"))
    program = Column(String, nullable=False)
    start = Column(String(16))
    duration = Column(Integer)

    tags = Column(String)

    def __repr__(self):
        return "<Schedule: program={}, channel={}, start={}, duration={}, tags={}>".format(
            self.program, self.channel, self.start, self.duration, self.tags
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

    def add_permissions(self, tags, email, role="reader"):
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

    def get_permissions(self, tag=None):
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

    def add_channel(self, name, ip):
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

    def get_channels(self, name=None):
        if name is None:
            return self.session.query(Channel).order_by(Channel.name).all()
        else:
            return self.session.query(Channel).filter(Channel.name == name).first()

    def set_channel_up(self, name):
        channel = self.session.query(Channel).filter(Channel.name == name).first()
        channel.is_up = True
        self.session.commit()

    def set_channel_down(self, name):
        channel = self.session.query(Channel).filter(Channel.name == name).first()
        channel.is_up = False
        self.session.commit()

    def add_job(
        self, name, channel, start, duration, upload, convert_to, subtitles, tags
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
            subtitles=subtitles,
            tags=tagstring,
        )
        self.session.add(entry)
        self.session.commit()

    def get_job(self, jobname=None):
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

    def add_file(self, filename, jobname):
        """
        This method adds files to the downloads table.
        Takes:
            The full path to the file.
            Name of the associated job.

        """
        entry = Download(filename=filename, jobname=jobname)
        self.session.add(entry)
        self.session.commit()

    def add_schedule(self, program, channel, start, duration, tags):
        entry = Schedule(
            program=program,
            channel=channel,
            start=start,
            duration=duration,
            tags=",".join(tags),
        )
        self.session.add(entry)
        self.session.commit()

    def get_schedule_items(self, channel=None, tags=None):
        if tags is None and channel is None:
            return self.session.query(Schedule).all()
        if tags is None:
            return (
                self.session.query(Schedule).filter(Schedule.channel == channel).all()
            )
        else:
            paramaters = [Schedule.tags.like("%{}%".format(x)) for x in tags]
            return self.session.query(Schedule).filter(or_(*paramaters)).all()
