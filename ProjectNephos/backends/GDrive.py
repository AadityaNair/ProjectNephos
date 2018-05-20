import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client.client import OAuth2Credentials
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError

from logging import getLogger

logger = getLogger(__name__)


class DriveStorage(object):
    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Project Nephos'

    def _run_credentials_flow(self,) -> OAuth2Credentials:
        """
        Get credentials via OAuth2.
        Run once during the first use of Nephos or when the stored
        credentials have somehow been invalidated.

        Returns:
            The credentials after the flow succeeded.
        Side Effects:
            Writes the credentials in the predetermined location.
        """
        flow = client.flow_from_clientsecrets(
                filename=CLIENT_SECRET_FILE,  # TODO: Convert to a file from config
                scope=SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob',  # Make sure that opening GUI is not attempted.
        )
        flow.user_agent = APPLICATION_NAME

        url = flow.step1_get_authorize_url()  # Returns the URL that the user is supposed to visit to authorize.
        print('Please visit the following URL to authorize Project Nephos: ' + url)
        code = input('Please enter the code you found there: ')
        credentials = flow.step2_exchange(code)
        logger.debug('Auth flow has been completed successfully')

        return credentials

    def _get_credentials(self, credential_path: str, ) -> OAuth2Credentials:
        """Gets valid user credentials from storage.

        If credentials do not exist, it runs the OAuth2 flow to get them.

        Takes:
            The location where the credentials are stored
        Returns:
            Credentials, the obtained credential.
        """
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            credentials = self._run_credentials_flow()
            store.put(credentials)
        return credentials

    def __init__(self, config):
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)

        self.file_service = service.files()
        self.perm_service = service.permissions()

    def write(self, filename):
        media = MediaFileUpload(filename=filename, mimetype=None, chunksize=1024, resumable=True)
        file_metadata = {'name': filename}

        self.file_service.create(body=file_metadata, media_body=media).execute()
        return f

    def _isExists(self, fileid):
        try:
            mdata = self.file_service.get(fileId=fileid).execute()
        except HttpError:
            return False
        return True

    def read(self, fileid):
        if self._isExists(fileid):
            data = self.file_service.get_media(fileId=fileid).execute()
            print(data)
        else:
            print("File Unavailable")

    def search(self, name_subs):
        query = "name contains '{}'".format(name_subs)
        response = self.file_service.list(q=query, pageSize=5, includeTeamDriveItems=True,
                                          supportsTeamDrives=True).execute()
        items = response.get('files', [])
        if not items:
            print("No such item found")

        for f in items:
            print("{name}\t{id}".format(name=f['name'], id=f['id']))

    def delete(self, fileid):
        if not self._isExists(fileid):
            print('File already non-existant')
            return None

        self.file_service.delete(fileId=fileid).execute()

    def add_permissions_user(self, fileid, email, role):
        if not self._isExists(fileid):
            print("No such file exists.")
            return None
        permission = {'type': 'user', 'role': role, 'emailAddress': email}
        self.perm_service.create(fileId=fileid, body=permission).execute()
