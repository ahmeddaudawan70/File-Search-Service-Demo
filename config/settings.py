import os

GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'https://localhost:9200')
ELASTICSEARCH_USERNAME = os.getenv('ELASTICSEARCH_USERNAME', 'elastic')
ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')
