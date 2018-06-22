from json import JSONDecodeError
from os.path import isfile
from typing import List, Tuple
from mimetypes import guess_type

from apiclient import discovery
from oauth2client import client
from oauth2client.client import OAuth2Credentials, FlowExchangeError
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError

from httplib2 import Http
from logging import getLogger
from configparser import ConfigParser

from oauth2client.clientsecrets import InvalidClientSecretsError

from ProjectNephos.exceptions import OAuthFailure, FileNotFound

logger = getLogger(__name__)


class DriveStorage(object):
    SCOPES = "https://www.googleapis.com/auth/drive"
    APPLICATION_NAME = "Project Nephos"

    @staticmethod
    def _run_credentials_flow(client_secret_loc: str) -> OAuth2Credentials:
        """
        Get credentials via OAuth2.
        Run once during the first use of Nephos or when the stored
        credentials have somehow been invalidated.

        Returns:
            The credentials after the flow succeeded.
        Side Effects:
            Writes the credentials in the predetermined location.
        """
        try:
            flow = client.flow_from_clientsecrets(
                filename=client_secret_loc,
                scope=DriveStorage.SCOPES,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",  # Make sure that opening GUI is not attempted.
            )
        except InvalidClientSecretsError:
            logger.critical(
                "An invalid client secret file was supplied. Check"
                "the file contents at {} and try again".format(client_secret_loc)
            )
            raise OAuthFailure("Invalid Client Secret file provided")
        except JSONDecodeError:
            logger.critical(
                "The client secret file is not a valid JSON file. Check it and try again."
            )
            raise OAuthFailure("Non JSON client secret file was provided.")

        flow.user_agent = DriveStorage.APPLICATION_NAME

        url = (
            flow.step1_get_authorize_url()
        )  # Returns the URL that the user is supposed to visit to authorize.
        print("Please visit the following URL to authorize Project Nephos: " + url)
        code = input("Please enter the code you found there: ")

        try:
            credentials = flow.step2_exchange(code)
        except FlowExchangeError:
            logger.critical(
                "Authentication flow has failed due to bad code entered. This can happen because some "
                "entries in the client secret is corrupted. Please check the file and try again."
            )
            raise OAuthFailure("Invalid Code")
        logger.debug("Auth flow has been completed successfully")

        return credentials

    def _get_credentials(
        self, credential_path: str, client_secret_loc: str
    ) -> OAuth2Credentials:
        """Gets valid user credentials from storage.

        If credentials do not exist, it runs the OAuth2 flow to get them.

        Takes:
            The location where the credentials are stored. This needs to be
            an *absolute path*
        Returns:
            Credentials, the obtained credential.
        """
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials:
            logger.debug("No credentials found on the location.")
        elif credentials.invalid:
            logger.warning("Credentials were found but are invalid.")

        if not credentials or credentials.invalid:
            logger.debug("Running the authentication flow.")
            credentials = self._run_credentials_flow(client_secret_loc)
            store.put(credentials)
        return credentials

    def __init__(self, config: ConfigParser):
        """
        Driver code to interact with Google Drive.
        This will try to authorize with your google account before proceeding.
        """
        credentials = self._get_credentials(
            credential_path=config["google", "auth_token_location"],
            client_secret_loc=config["google", "client_secret_location"],
        )
        http = credentials.authorize(Http())
        service = discovery.build("drive", "v3", http=http)

        self.file_service = service.files()
        self.perm_service = service.permissions()

    def write(self, filename: str) -> dict:
        """
        Upload the file the Google Drive. The file should essentially exist before you try to upload it.
        It will return the metadata of the file, as set by Google. Most important of the metadata is the `id`
        which is unique to each file.
        Takes:
            path to the file as a string.
        Returns:
             The metadata dictionary
        """
        logger.debug("Trying to upload file: {}".format(filename))

        if not isfile(filename):
            logger.critical("No such file exists. Check path and try again")
            raise FileNotFound(filename + "does not exist")

        media = MediaFileUpload(
            filename=filename, mimetype=guess_type(filename)[0], chunksize=1024
        )
        file_metadata = {
            "name": filename.split("/")[-1],  # Get filename from path
            "description": "",  # Required so that the field actually exists when the file is uploaded.
        }

        f = self.file_service.create(body=file_metadata, media_body=media).execute()
        logger.info("File successfully uploaded.")
        logger.debug("File metadata: {}".format(f))
        return f

    def is_exists(self, fileid: str) -> bool:
        """
        Check if given file already exists in the Drive. It does it by requesting for the
        file metadata.

        Takes:
            The unique fileid for the item.
        Returns:
            Boolean.
        """
        try:
            self.file_service.get(fileId=fileid).execute()
        except HttpError:
            return False
        return True

    def search(
        self, name_subs: str = None, tag_subs: List[str] = None, do_and: bool = False
    ) -> List[Tuple[str, str]]:
        """
        Search for a file in the drive. Many filters are supported but we currently only
        search for a substring on a filename and for tags. It returns the names as well as fileids for
        all matching objects.

        Takes:
            Substring to be searched.
        Returns:
             A list of tuples: [(filename, fileid)...]
        """
        # TODO: Improve this section
        if tag_subs is None:
            query = "name contains '{}'".format(name_subs)
        elif name_subs is None:
            query_set = ["fullText contains '{}'".format(x) for x in tag_subs]
            if do_and:
                query = " and ".join(query_set)
            else:
                query = " or ".join(query_set)
        else:
            qn = "name contains '{}'".format(name_subs)
            qt_set = ["fullText contains '{}'".format(x) for x in tag_subs]

            if do_and:
                query = qn + " and " + " and ".join(qt_set)

        logger.debug("Following is the search query: " + query)

        response = self.file_service.list(
            q=query, pageSize=5, includeTeamDriveItems=True, supportsTeamDrives=True
        ).execute()

        items = response.get("files", [])
        if not items:
            logger.critical("No files were found matching the query.")
            raise FileNotFound("Query returned empty")

        response = [(f["name"], f["id"]) for f in items]
        logger.debug("following information was returned.\n{}".format(response))
        return response

    def read(self, fileid: str) -> str:
        """
        Read a file of the given id. Raises error if file does not already
        exist for some reason

        Takes:
            The id of the file to be read.
        Returns:
            The contents of the file as a binary string.
        """
        logger.debug("Trying to read file id: {}".format(fileid))

        if self.is_exists(fileid):
            return self.file_service.get_media(fileId=fileid).execute()
        else:
            logger.critical("Given file not found.")
            raise FileNotFound("{} not found on drive".format(fileid))

    def delete(self, fileid: str) -> None:
        """
        Delete a file from the cloud drive. Returns nothing on success. Error on failure.
        If file does not already exist before deleting, the operation is treated as a success.

        Takes:
            fileid of the object to be deleted.
        """
        if not self.is_exists(fileid):
            logger.warning("The provided fileid ({}) never existed.".format(fileid))
            return None

        self.file_service.delete(fileId=fileid).execute()
        logger.debug("Fileid ({}) deleted.".format(fileid))

    def tag(self, fileid: str, tags: List[str]) -> None:
        """
        Add the provided tag to a valid file. The current method of adding tags involves
        directly writing the tag onto the description field of the file on the drive.

        Note that this does not check if it is a valid tag. This is the caller's job.

        Takes:
            fileid of the object to be tagged.
            a list of tags to be added.
        """
        if not self.is_exists(fileid):
            logger.critical("Given file not found")
            raise FileNotFound("The provided fileid {} does not exist".format(fileid))

        # so as to not delete old contents:
        info = self.file_service.get(fileId=fileid, fields="description").execute()
        old_description = info["description"]

        # TODO: We can do this better by overwriting repeating tags
        metadata = {"description": old_description + "\n" + " \n".join(tags)}
        self.file_service.update(fileId=fileid, body=metadata).execute()

    def add_permissions_user(self, fileid: str, email: str, role: str) -> dict:
        """
        Share a given fileid with some other entity. Currently, the only supported entity
        is a single user addressed by their email. Role defines the level of access the entity can have
        The supported values for role are: owner, reader, writer or commenter.

        Permissions are idempotent. Adding the same permission twice will have no extra effect but
        the permission will have to be removed all the times it had been added to actually revoke it.

        Takes:
            id of the file to which permissions have to be added.
            email address of the entity to which permission is granted.
            the role granted to the entity.
        Returns:
            the metadata associated with the permission
        """
        logger.debug(
            "Following information to be updated\n"
            "fileid: {f}\nrole: {r}\n email: {e}\n".format(f=fileid, r=role, e=email)
        )

        if not self.is_exists(fileid):
            logger.critical("File not found")
            raise FileNotFound("No file to add permission to")

        permission = {"type": "user", "role": role, "emailAddress": email}
        mdata = self.perm_service.create(fileId=fileid, body=permission).execute()
        logger.debug("The permission was created.\n{}".format(mdata))

        return mdata
