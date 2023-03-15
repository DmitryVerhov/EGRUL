import requests
import pandas as pd
from time import sleep
from random import randint
from fake_headers import Headers
from tqdm import tqdm
from typing import Union


class EgrulParser:
    """
    Use first: check_numbers(numbers) - fetch data from website,
    and store it into the "data" variable  
     get_expired() - returns expired ogrn numbers 
    """

    def __init__(self) -> None:
        # Target sites
        self.home_url = "https://egrul.nalog.ru"
        self.search_url = "https://egrul.nalog.ru/search-result/"
        # Generating headers
        self.HEADERS = Headers(browser="chrome", os="win", headers=True).generate()
        

    def try_post(self, url: str, data: dict, retry: int = 5) -> requests.models.Response:
        """Makes 'post' requests to the url with retry logic in case of failure."""
        try:
            response = requests.post(url=url, data=data, headers=self.HEADERS)
            if response.status_code != 200:
                raise
        except:
            sleep(randint(30, 50))
            if retry:  # retries several times (default - 5)
                print(f"Request retries left: {retry}")
                return self.try_post(url, data, retry=(retry - 1))
            else:
                raise Exception("Retries exhausted")
        else:
            return response
        
    def try_get(self, url: str, retry: int = 5) -> requests.models.Response:
        """Makes get-requests to the url with retry logic in case of failure."""
        try:
            response = requests.get(url=url, headers=self.HEADERS)
            if response.status_code != 200:
                raise
        except:
            sleep(randint(30, 50))
            if retry:  # retries several times (default - 5)
                print(f"Request retries left: {retry}")
                return self.try_get(url, retry=(retry - 1))
            else:
                raise Exception("Retries exhausted")
        else:
            return response

    def check_numbers(self, numbers: Union[list, tuple]) -> None:
        """Takes a list or tuple of numbers as an argument 
        and check each number in the list for expiration. 
        If there is client info available, it is added to the "data" list, 
        otherwise it is added to the "wrong_numbers" list. 
        """
        self.data = []
        self.wrong_numbers = []
        pbar = tqdm(numbers, desc="Total")
        for ogrn in pbar:
            try:
                token = self.try_post(self.home_url, data={"query": ogrn}).json()["t"]
                client_info = self.try_get(self.search_url + token).json()["rows"]
                if len(client_info) != 0:
                    self.data = self.data + client_info
                else:
                    self.wrong_numbers.append(ogrn)
                sleep(randint(1, 5))
            except:
                continue
            pbar.set_description(f"Processing '{ogrn}'")
