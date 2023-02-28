import datetime
import os
import toml

class AppSettings:
    splunk_home: str
    splunk_environment: bool = False
    splunk_session_key: str
    splunk_username: str
    splunk_password: str
    splunk_api_url: str = 'https://localhost:8089'
    bw_api_url: str = 'https://api.bitwarden.com'
    bw_identity_url: str = 'https://identity.bitwarden.com'
    events_start_date = (datetime.datetime.utcnow() -
                         datetime.timedelta(days=365)).isoformat()

    def __init__(self):
        self.splunk_home = os.environ.get('SPLUNK_HOME')
        self.splunk_environment = self._splunk_environment()
        self.splunk_session_key = os.getenv('SPLUNK_SESSION_KEY')
        self.splunk_username = os.getenv('SPLUNK_USERNAME')
        self.splunk_password = os.getenv('SPLUNK_PASSWORD')
        self.splunk_api_url = os.getenv('SPLUNK_API_URL', self.splunk_api_url)
        self.bw_api_url = os.getenv('BW_API_URL', self.bw_api_url)
        self.bw_identity_url = os.getenv('BW_IDENTITY_URL', self.bw_identity_url)
        self.events_start_date = os.getenv(
            'BW_EVENTS_START_DATE', self.events_start_date)
        self.settings = self._load_settings()

    def _load_settings(self):
        settings = {}
        try:
            with open(f'{self.splunk_home}/etc/apps/bitwarden_event_logs/local/script.conf', 'r') as f:
                settings = toml.load(f)
        except FileNotFoundError:
            print('No local settings file found.')
        if 'config' in settings:
            config = settings['config']
            self.bw_api_url = config.get('apiUrl', self.bw_api_url)
            self.bw_identity_url = config.get('identityUrl', self.bw_identity_url)
        if 'startDate' in settings:
            config = settings['startDate']
            self.events_start_date = config.get('startDate', self.events_start_date)
        if 'apiUrl' in settings:
            config = settings['apiUrl']
            self.bw_api_url = config.get('apiUrl', self.bw_api_url)
        if 'identityUrl' in settings:
            config = settings['identityUrl']
            self.bw_identity_url = config.get('identityUrl', self.bw_identity_url)
        return settings

    def get(self, key):
        return self.settings.get(key)

    def get_all(self):
        return self.settings
