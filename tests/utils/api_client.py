import requests
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, headers:dict=None, timeout: int = 10):
        if headers is None:
            headers = {"Content-Type": "application/json; charset=UTF-8"}
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.timeout = timeout

    def _headers(self, headers: dict = None, token: str = None) -> dict:
        merged = dict(headers or {})
        if token:
            merged["Authorization"] = f"Bearer {token}"
        return merged
    
    def get(self, endpoint: str, headers: dict = None, token = None) -> requests.Response:
        logger.info(f"GET {self.base_url}{endpoint}")
        response = self.session.get(
            f"{self.base_url}{endpoint}", 
            headers=self._headers(headers, token), 
            timeout=self.timeout,
        )
        logger.info(f"Response {response.status_code}: {response.text}")
        return response
    
    def post(self, endpoint: str, body: dict = None, headers: dict = None, token = None) -> requests.Response:
        logger.info(f"POST {self.base_url}{endpoint} | body: {body}")
        response = self.session.post(
            f"{self.base_url}{endpoint}", 
            json=body, 
            headers=self._headers(headers, token), 
            timeout=self.timeout
        )
        logger.info(f"Response {response.status_code}: {response.text}")
        return response
    
    def put(self, endpoint: str, body: dict = None, headers: dict = None, token = None) -> requests.Response:
        logger.info(f"PUT {self.base_url}{endpoint} | body: {body}")
        response = self.session.put(
            f"{self.base_url}{endpoint}", 
            json=body, 
            headers=self._headers(headers, token),
            timeout=self.timeout
        )
        logger.info(f"Response {response.status_code}: {response.text}")
        return response
    
    def patch(self, endpoint: str, body: dict = None, headers: dict = None, token = None) -> requests.Response:
        logger.info(f"PATCH {self.base_url}{endpoint} | body: {body}")
        response = self.session.patch(
            f"{self.base_url}{endpoint}", 
            json=body, 
            headers=self._headers(headers, token), 
            timeout=self.timeout,
        )
        logger.info(f"Response {response.status_code}: {response.text}")
        return response
    
    def delete(self, endpoint: str, headers: dict = None, token = None) -> requests.Response:
        logger.info(f"DELETE {self.base_url}{endpoint}")
        response = self.session.delete(
            f"{self.base_url}{endpoint}", 
            headers=self._headers(headers, token), 
            timeout=self.timeout)
        logger.info(f"Response {response.status_code}: {response.text}")
        return response