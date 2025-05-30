import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsManager:
    """Class to manage Google Sheets operations."""

    def __init__(self, credentials: dict):
        """
        Initialize the Google Sheets manager with credentials.

        Args:
            credentials: Dictionary containing service account credentials.
                Example:
                {
                    "type": "service_account",
                    "project_id": "project-id",
                    "private_key_id": "private-key-id",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nprivate-key\n-----END PRIVATE KEY-----\n",
                    "client_email": "client-email",
                    "client_id": "111111111111111",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/<client_email>",
                    "universe_domain": "googleapis.com"
                }
        """
        self.credentials = credentials
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.client = self._get_google_sheets_client()

    def _get_google_sheets_client(self):
        """Initialize and return Google Sheets API client."""
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.credentials, self.scope)
        return gspread.authorize(creds)

    def get_worksheet(self, spreadsheet_url, worksheet_name):
        """
        Get specific worksheet from Google Spreadsheet.

        Args:
            spreadsheet_url: URL of the Google Spreadsheet
            worksheet_name: Name of the worksheet to access

        Returns:
            Worksheet object
        """
        spreadsheet = self.client.open_by_url(spreadsheet_url)
        return spreadsheet.worksheet(worksheet_name)

    def get_worksheet_by_index(self, spreadsheet_url, worksheet_index):
        """
        Get specific worksheet from Google Spreadsheet by index.

        Args:
            spreadsheet_url: URL of the Google Spreadsheet
            worksheet_index: Index of the worksheet to access

        Returns:
            Worksheet object
        """
        spreadsheet = self.client.open_by_url(spreadsheet_url)
        return spreadsheet.get_worksheet(worksheet_index)

    def get_worksheet_values(self, spreadsheet_url, worksheet_name):
        """
        Retrieve all values from a specified worksheet in a Google Spreadsheet.

        Args:
            spreadsheet_url: URL of the Google Spreadsheet
            worksheet_name: Name of the worksheet to retrieve values from

        Returns:
            List of all values in the worksheet
        """
        worksheet = self.get_worksheet(spreadsheet_url, worksheet_name)
        return worksheet.get_all_values()


# Usage example:
# credentials = {...}  # Your service account credentials dictionary
# sheets_manager = GoogleSheetsManager(credentials)
# values = sheets_manager.get_worksheet_values(
#     "https://docs.google.com/spreadsheets/d/15pNIt9574qWHlFLHlmvHhgqyiEsEcEspW8--oFiVqaw",
#     "Задание"
# )
