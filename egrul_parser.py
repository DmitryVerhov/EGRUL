import requests
import pandas as pd
from  time import sleep
from random import randint
from fake_headers import Headers
from tqdm import tqdm 


class EgrulParser():
    def __init__(self) -> None:
        # Generating headers
        self.HEADERS = Headers(browser="chrome",
                               os="win",
                               headers=True).generate()
        self.home_url = 'https://egrul.nalog.ru'
        self.search_url = 'https://egrul.nalog.ru/search-result/'
        

    def try_post(self,url:str,data,retry=5):
        try:
            response = requests.post(url=url,data=data,headers=self.HEADERS)
            if response.status_code != 200:
                raise
        except:
            sleep(randint(30,50))
            if retry:# retries several times (default - 5)
                print(F'Request retries left: {retry}')
                return self.try_post(url, data, retry=(retry - 1))
            else:
                raise
        else:
            return response

    def try_get(self,url:str,retry=5):
        try:
            response = requests.get(url=url, headers=self.HEADERS)
            if response.status_code != 200:
                raise
        except:
            sleep(randint(30,50))
            if retry:# retries several times (default - 5)
                print(F'Request retries left: {retry}')
                return self.try_get(url, retry=(retry - 1))
            else:
                raise
        else:
            return response    

    def get_table(self, numbers):

        full_data = []
        wrong_numbers = []
        pbar = tqdm(numbers, desc='Total')

        for ogrn in pbar:
            
            token  = self.try_post(self.home_url, data={'query': ogrn}).json()['t']
            client_data = self.try_get(self.search_url + token).json()['rows']
            if len(client_data) != 0: 
                full_data =  full_data + client_data
            else:
                wrong_numbers.append(ogrn)
            sleep(randint(1,5))
            pbar.set_description(f"Processing '{ogrn}'")

        clients_df = pd.DataFrame(full_data)    
        clients_df.to_excel('clients.xlsx',index=False)  