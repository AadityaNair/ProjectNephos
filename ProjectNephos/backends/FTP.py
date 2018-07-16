import ftplib, io
from logging import getLogger
from os.path import isfile

from ProjectNephos.exceptions import AuthFailure, FileNotFound

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

    def _traverse_tree(self, start):
        for item in self.ftp.mlsd(start):
            if item[1]["type"] == "dir":
                old_pwd = self.ftp.pwd()
                self.ftp.cwd(item[0])
                yield from self._traverse_tree(".")
                self.ftp.cwd(old_pwd)
            else:
                item[1]["folder"] = self.ftp.pwd()
                yield item

    def search(self, name_subs=None, tag_subs=None, do_and=False):
        # Current implementation is only for either search by name
        # or search by tags but not both
        if name_subs is not None and tag_subs is not None:
            raise NotImplementedError(
                "Currently only one of name_subs or tag_subs can be provided."
            )
        matching_items = []
        if name_subs is not None:
            for file in self._traverse_tree("/"):
                if file[0].endswith(".tag"):
                    continue
                else:
                    if file[0].find(name_subs) != -1:
                        matching_items.append(file[1]["folder"] + "/" + file[0])

        if tag_subs is not None:
            for file in self._traverse_tree("/"):
                if file[0].endswith(".tag"):
                    full_path = file[1]["folder"] + "/" + file[0]

                    contents = self.read(full_path)
                    matching_tags = list(map(contents.find, tag_subs))

                    if do_and:
                        if (
                            len(list(filter(lambda x: x != -1, matching_tags)))
                            == len(matching_tags)
                            and len(matching_tags) > 0
                        ):
                            matching_items.append(full_path)
                    else:
                        if len(list(filter(lambda x: x != -1, matching_tags))) > 0:
                            matching_items.append(full_path)

        return matching_items

    def read(self, filepath):
        logger.debug("Trying to read file id: {}".format(filepath))

        if self.is_exists(filepath):
            fp = io.BytesIO()
            self.ftp.retrbinary("RETR {}".format(filepath), fp.write)
            return fp.getvalue().decode("ascii")
        else:
            logger.critical("Given file not found.")
            raise FileNotFound("{} not found on drive".format(filepath))

    def delete(self, filepath):
        if not self.is_exists(filepath):
            logger.warning("The provided fileid ({}) never existed.".format(filepath))
            return None

        self.ftp.delete(filepath)
        logger.debug("Fileid ({}) deleted.".format(filepath))

    def tag(self, filepath, tags):
        if not self.is_exists(filepath):
            logger.critical("Given file not found")
            raise FileNotFound("The provided fileid {} does not exist".format(filepath))

        tag_filepath = filepath + ".tag"
        f = io.BytesIO(b"\n".join(map(lambda x: x.encode("utf-8"), tags)))

        self.ftp.storlines("STOR {}".format(tag_filepath), f)

    def add_permission_user(self, *_):
        return None
