import os

from ProjectNephos.backends import DBStorage
from ProjectNephos.handlers.upload import UploadHandler
from ProjectNephos.handlers.process import ProcessHandler
from ProjectNephos.handlers.tag import TagHandler
from ProjectNephos.handlers.permissions import PermissionHandler

from logging import getLogger

logger = getLogger("job_log")


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
        logger.debug(new_full_path)

        stdout = p.execute_command(filename, new_full_path)
        logger.debug("FFMPEG OUTPUT:\n{}".format(stdout))
        return new_full_path
    else:
        return filename


def run_ccex(subtitles, filename, config):
    if subtitles:
        p = ProcessHandler(config=config)

        file_basename = filename.split("/")[-1]

        # This code changes the extension of the file
        l = file_basename.split(".")
        l.pop()  # Remove old extension
        l.append("srt")  # add new extension
        new_filename = ".".join(l)
        new_full_path = config["downloads", "temp_save_location"] + new_filename
        logger.debug(new_full_path)
        stdout = p.execute_ccextractor(filename, new_full_path)
        logger.debug("CCEx Output:\n{}".format(stdout))
        return new_full_path


def upload_job(upload, path, subtitle, folder, config):
    if not upload:
        return None
    else:
        u = UploadHandler("upload")
        u.init_with_config(config)
        fileid_record = u.execute_command(path, folder)
        if subtitle is not None:
            fileid_subtitle = u.execute_command(subtitle, folder)
        else:
            fileid_subtitle = None
        return fileid_record, fileid_subtitle


def tag_job(fileid, tagstring, config):
    if fileid is None or tagstring is None:
        return None
    else:
        taglist = tagstring.split(",")

        t = TagHandler("tag")
        t.init_with_config(config)
        t.execute_command(fileid, taglist)


def share_job(fileid, permission_set, config):
    if len(permission_set) == 0:
        return 0

    p = PermissionHandler(config=config)

    for mail, role in permission_set:
        p.execute_command(fileid, mail, role)

    return 1


def delete_job(old_path, new_path, subt_path):
    l = old_path.split(".")
    l.pop()  # Remove old extension
    l.append("aux")  # add new extension
    aux_file = ".".join(l)

    os.remove(old_path)
    logger.debug("Deleted file {}".format(old_path))

    os.remove(aux_file)
    logger.debug("Deleted file {}".format(aux_file))

    os.remove(new_path)
    logger.debug("Deleted file {}".format(new_path))

    os.remove(subt_path)
    logger.debug("Deleted file {}".format(subt_path))


def delete_and_upload_log(config, rec_path, folder):
    f = rec_path.split("/")[-1]
    fname = f.split(".")[0]
    log_file_path = config["recording", "logs"] + fname + ".log"
    u = UploadHandler(config=config)
    u.execute_command(log_file_path, folder)
    os.remove(log_file_path)


def run_job(_, config):
    db = DBStorage(config)
    download = db.pop_download()
    if download is None:
        db.session.close()
        return 5

    associated_job = db.get_job(download.jobname)

    permission_set = set()
    if associated_job.tags is not None and len(associated_job.tags) > 0:
        for tag in associated_job.tags.split(","):
            perms = db.get_permissions(tag)
            for _, mail, role in perms:
                permission_set.add((mail, role))

    new_path = process_job(associated_job.convert_to, download.filename, config)

    subt_path = run_ccex(associated_job.subtitles, new_path, config)

    fileId, _ = upload_job(
        associated_job.upload, new_path, subt_path, associated_job.channel, config
    )

    tag_job(fileId, associated_job.tags, config)

    share_job(fileId, permission_set, config)

    delete_job(download.filename, new_path, subt_path)

    delete_and_upload_log(config, download.filename, associated_job.channel)

    db.session.close()
