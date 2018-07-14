import ftplib, io
from logging import getLogger
from os.path import isfile

# from ProjectNephos.exceptions import AuthFailure, FileNotFound
class AuthFailure(Exception):
    pass


class FileNotFound(Exception):
    pass


logger = getLogger(__name__)


class FTPClient(object):

    def __init__(self, config):
        self.ftp = ftplib.FTP()

        try:
            self.ftp.connect(config["ftp", "host"], int(config["ftp", "port"]))
        except ConnectionError:
            logger.critical(
                "Unable to connect to the server. Please check and try again"
            )
            raise
        else:
            logger.debug("FTP connection established.")

        try:
            self.ftp.login(config["ftp", "username"], config["ftp", "password"])
        except ftplib.error_perm:
            logger.critical(
                "Bad username or password supplied. Please check and try again."
            )
            raise AuthFailure("Wrong credentials supplied")
        else:
            logger.debug("FTP authenticated successfully")

    def write(self, filename, folder=None):
        logger.debug("Trying to upload {}".format(filename))

        if not isfile(filename):
            logger.critical("No such file exists. Check path and try again")
            raise FileNotFound(filename + "does not exist")

        folder_path = ""
        if folder is not None:
            folder_path = self.create_folder(folder)
        full_path = folder_path + "/" + filename

        with open(filename, "rb") as f:
            self.ftp.storbinary("STOR {}".format(full_path), f)

        return full_path

    def is_exists(self, fullpath):
        current_folder = self.ftp.pwd()

        file_path = "/".join(fullpath.split("/")[:-1])
        filename = fullpath.split("/")[-1]

        self.ftp.cwd(file_path)

        files_in_pwd = list(self.ftp.mlsd())

        if len(files_in_pwd) == 0:
            return False

        for file in files_in_pwd:
            if file[0] == filename and file[1]["type"] == "file":
                return True

        self.ftp.cwd(current_folder)
        return False

    def create_folder(self, foldername):
        try:
            self.ftp.mkd(foldername)
        except ftplib.error_perm:
            logger.debug("Folder already exists.")
        else:
            logger.debug("Created new folder.")
        return "/" + foldername

    def search(self, name_subs=None, tag_subs=None, do_and=False):
        pass

    def read(self, fileid):
        pass

    def delete(self, fileid):
        pass

    def tag(self, filepath, tags):
        if not self.is_exists(filepath):
            logger.critical("Given file not found")
            raise FileNotFound("The provided fileid {} does not exist".format(filepath))

        tag_filepath = filepath + ".tag"
        f = io.BytesIO(b"\n".join(map(lambda x: x.encode("utf-8"), tags)))

        self.ftp.storlines("STOR {}".format(tag_filepath), f)

    def add_permission_user(self, *_):
        return None
