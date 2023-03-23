import requests
from time import sleep
from random import randint
from fake_headers import Headers
from tqdm import tqdm
from typing import Union


class EgrulParser:
    '''
    Use first: check_numbers(numbers) - fetch data from website,
    and store it into the "data" variable\n  
    get_expired() - returns expired ogrn numbers\n 
    get_wrong_numbers() - returns ogrn numbers not found on the site
    '''

    def __init__(self) -> None:
        # Target sites
        self.home_url = "https://egrul.nalog.ru"
        self.search_url = "https://egrul.nalog.ru/search-result/"
        # Generating headers
        self.HEADERS = Headers(browser="chrome",
                               os="win",
                               headers=True).generate()

    def try_post(self, url: str, data: dict, retry: int = 5) -> requests.models.Response:
        '''Makes 'post' requests to the url with retry logic in case of failure.'''
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
        '''Makes get-requests to the url with retry logic in case of failure.'''
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

    def check_numbers(self,
                      numbers: Union[list, tuple],
                      progress_bar: bool = True) -> None:
        '''Takes a list or tuple of numbers as an argument 
        and check each number in the list for expiration. 
        If there is client_info available, it is added to the "data" list, 
        otherwise number is added to the "wrong_numbers" list.'''

        self.data = []  # here clients info will be stored
        self.wrong_numbers = ['.']  # list for failed numbers
        # Initialise progress bar
        pbar = tqdm(numbers, desc = "Total", disable = not progress_bar)
        for ogrn in pbar:
            try:
                # Getting client token, using his orgn number 
                token = self.try_post(self.home_url,
                                      data={"query": ogrn}).json()["t"]

                client_url = self.search_url + token
                client_info = self.try_get(client_url).json()["rows"]
                if len(client_info) != 0:
                    self.data = self.data + client_info
                else:
                    self.wrong_numbers.append(ogrn)
                sleep(randint(1, 5))
            except:
                self.wrong_numbers.append(ogrn)
                continue
            pbar.set_description(f"Processing {ogrn}")

    def get_expired(self) -> list:
        '''Returns expired ogrn numbers found by check_numbers()'''
        if self.data:
            expired = [item['o'] for item in self.data if 'e' in item]
            return expired
        else:
            raise Exception('Run check_numbers() at first')

    def get_wrong_numbers(self) -> list:
        '''Returns ogrn numbers not found on the site'''
        if self.wrong_numbers:
            return self.wrong_numbers[1:]
        else:
            raise Exception('Run check_numbers() at first')
