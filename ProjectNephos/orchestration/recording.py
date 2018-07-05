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
        + str(datetime.datetime.now().strftime("%Y-%m-%d_%H%M"))
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

    p = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode != 0:
        logger.critical("Some error has occured during recording {}".format(job))
        # logger.critical(
        #     "Dumping entire output:\nSTDOUT:\n{}\nSTDERR:\n{}".format(
        #         p.stdout, p.stderr
        #     )
        # )
    else:
        logger.debug("Successful recording of {}".format(job))
        # logger.debug(
        #     "Dumping entire output:\nSTDOUT:\n{}\nSTDERR:\n{}".format(
        #         p.stdout, p.stderr
        #     )
        # )
        db.add_file(full_path, job.name)
