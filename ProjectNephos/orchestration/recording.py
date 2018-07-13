import datetime
import subprocess
from logging import getLogger

from ProjectNephos.backends.DataBase import Job, DBStorage
from ProjectNephos.config import Configuration

logger = getLogger(__name__)


def record_video(job, config):
    db = DBStorage(config)
    base_path = config["downloads", "local_save_location"]
    full_path = (
        base_path
        + job.name
        + "--"
        + str(datetime.datetime.now().strftime("%Y%m%d_%H:%M"))
        + ".ts"
    )

    duration = job.duration * 60 * 27000000
    multicat = config["recording", "multicat"]
    bind_ip = config["recording", "bind"]
    channel = db.get_channels(job.channel)

    if bind_ip:
        bind_ip = "/ifaddr=" + bind_ip

    command = "{multicat} -u -d {duration} @{ip}{bind} {path}".format(
        multicat=multicat,
        duration=duration,
        ip=channel[0][1],
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
