from ProjectNephos.backends import DBStorage
from ProjectNephos.handlers.upload import UploadHandler
from ProjectNephos.handlers.process import ProcessHandler
from ProjectNephos.handlers.tag import TagHandler

from logging import getLogger

logger = getLogger(__name__)


def process_job(convert_to, filename, config):
    if convert_to:
        p = ProcessHandler("process")
        p.init_with_config(config)

        file_basename = filename.split("/")[-1]

        # This code changes the extension of the file
        l = file_basename.split(".")
        l.pop()  # Remove old extension
        l.append(convert_to)  # add new extension
        new_filename = ".".join(l)
        new_full_path = config["downloads", "temp_save_location"] + new_filename
        logger.critical(new_full_path)

        p.execute_command(filename, new_full_path)
        return new_full_path
    else:
        return filename


def upload_job(upload, path, config):
    if not upload:
        return None
    else:
        u = UploadHandler("upload")
        u.init_with_config(config)
        mdata = u.execute_command(path)
        return mdata["id"]


def tag_job(fileid, tagstring, config):
    if fileid is None:
        return None
    else:
        taglist = tagstring.split(",")

        t = TagHandler("tag")
        t.init_with_config(config)
        t.execute_command(fileid, taglist)


def run_job(config):
    db = DBStorage(config)
    download = db.pop_download()
    if download is None:
        return 5

    associated_job = db.get_job(download.jobname)

    new_path = process_job(associated_job.convert_to, download.filename, config)

    fileId = upload_job(associated_job.upload, new_path, config)

    tag_job(fileId, associated_job.tags, config)
