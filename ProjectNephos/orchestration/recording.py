import datetime
import subprocess
import logging

from ProjectNephos.backends.DataBase import Job, DBStorage
from ProjectNephos.config import Configuration

logger = logging.getLogger(__name__)


def record_video(job, config):
    db = DBStorage(config)
    channel = db.get_channels(job.channel)

    if not channel.is_up:
        logger.critical("{} skipped due to channel being down".format(job))
        return -1

    base_path = config["downloads", "local_save_location"]
    full_path = (
        base_path
        + job.name
        + "--"
        + str(datetime.datetime.now().strftime("%Y%m%d_%H:%M"))
        + ".ts"
    )

    log_file_path = (
        config["recording", "logs"]
        + job.name
        + "--"
        + str(datetime.datetime.now().strftime("%Y%m%d_%H:%M"))
        + ".log"
    )

    logger = logging.getLogger("job_log")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file_path)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    duration = job.duration * 60 * 27000000
    multicat = config["recording", "multicat"]
    bind_ip = config["recording", "bind"]
    channel = db.get_channels(job.channel)

    if bind_ip:
        bind_ip = "/ifaddr=" + bind_ip

    command = "{multicat} -u -d {duration} @{ip}{bind} {path}".format(
        multicat=multicat,
        duration=duration,
        ip=channel.ip_string,
        path=full_path,
        bind=bind_ip,
    )

    try:
        stdout = subprocess.check_output(command.split(), stderr=subprocess.STDOUT)

    except FileNotFoundError:
        logger.critical(
            "multicat does not exist at the provided path {}".format(multicat)
        )
        return -1
    except subprocess.CalledProcessError:
        logger.critical("Some error has occured during recording {}".format(job))
        logger.critical("Dumping output:\n{}".format(stdout))
        return -1

    logger.debug("Recording completed successfully for the job {}".format(job))
    db.add_file(full_path, job.name)
    db.session.close()
    return 0
