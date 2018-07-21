from ProjectNephos.backends.GDrive import DriveStorage
from ProjectNephos.backends.FTP import FTPStorage

options = {"google": DriveStorage, "ftp": FTPStorage}


class DataStore(object):

    def __init__(self, config):
        self.backends = {}

        for item in config["others", "backends"].split():
            self.backends[item] = options[item](config)

    def write(self, filename, folder=None):
        response = {}
        for backend, obj in self.backends.items():
            response[backend] = obj.write(filename, folder)

        return response

    def is_exists(self, filename):
        return all(map(lambda x: x.is_exists(filename), self.backends.items()))

    def create_folder(self, name):
        response = {}
        for backend, obj in self.backends.items():
            response[backend] = obj.create_folder(name)

        return response

    def search(self, name_subs=None, tag_subs=None, do_and=False):
        response = []
        for backend, obj in self.backends.items():
            intr = sorted(obj.search(name_subs, tag_subs, do_and), key=lambda x: x[0])
            if len(response) == 0:
                response = [(x[0], {backend: x[1]}) for x in intr]
            else:
                for item in intr:
                    name, id = item
                    for i in range(len(response)):
                        if response[i][0] == name:
                            break
                    value = response[i]
                    value[1][backend] = id
                    response[i] = value
        return response

    def read(self, fileids):
        name, obj = list(self.backends.items())[0]
        return obj.read(fileids[name])

    def delete(self, fileids):
        map(lambda name, obj: obj.delete(fileids[name]), self.backends.items())

    def tag(self, fileids, tags):
        response = {}
        for backend, obj in self.backends.items():
            response[backend] = obj.tag(fileids[backend], tags)

        return response

    def add_permission_user(self, fileids, email, role):
        for backend, obj in self.backends.items():
            obj.add_permission_user(fileids[backend], email, role)
