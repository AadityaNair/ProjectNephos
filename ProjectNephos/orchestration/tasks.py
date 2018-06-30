from ProjectNephos.backends import DBStorage


def add_task(config):
    db = DBStorage(config)
    download = db.pop_download()
    if download is None:
        return 5
    print(download)

    # job_name = download.jobname
