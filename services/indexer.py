from elasticsearch import Elasticsearch
from abc import ABC, abstractmethod
from typing import Dict, List
from config.settings import ELASTICSEARCH_HOST, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD
from services.text_extractor import TesseractTextExtractor
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndexService(ABC):
    @abstractmethod
    def index_file(self, file: Dict, content: bytes):
        pass

    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        pass

class Indexer(IndexService):
    def __init__(self):
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                self.es = Elasticsearch(
                    [ELASTICSEARCH_HOST],
                    basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
                    verify_certs=False,
                    request_timeout=10
                )
                if not self.es.ping():
                    raise Exception("Elasticsearch ping failed")
                logger.info("Connected to Elasticsearch at %s", ELASTICSEARCH_HOST)
                break
            except Exception as e:
                logger.error("Attempt %d: Failed to connect to Elasticsearch: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise Exception("Elasticsearch connection failed after retries")
        self.extractor = TesseractTextExtractor()

    def index_file(self, file: Dict, content: bytes):
        try:
            text = self.extractor.extract_text(content, file['mimeType'])
            logger.info("Extracted text for %s (length: %d characters)", file['name'], len(text))
            self.es.index(
                index='files',
                id=file['id'],
                body={
                    'name': file['name'],
                    'content': text,
                    'url': file.get('webViewLink', '')
                }
            )
            logger.info("Indexed file: %s (ID: %s)", file['name'], file['id'])
        except Exception as e:
            logger.error("Error indexing file %s: %s", file.get('name', 'unknown'), e)

    def search(self, query: str) -> List[Dict]:
        try:
            response = self.es.search(
                index='files',
                body={
                    'query': {
                        'multi_match': {
                            'query': query,
                            'fields': ['name', 'content']
                        }
                    }
                }
            )
            results = [
                {
                    'name': hit['_source']['name'],
                    'url': hit['_source']['url']
                }
                for hit in response['hits']['hits']
            ]
            logger.info("Search query '%s' returned %d results", query, len(results))
            return results
        except Exception as e:
            logger.error("Error searching for query '%s': %s", query, e)
            return []