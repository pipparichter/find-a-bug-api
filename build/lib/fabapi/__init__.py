import requests
import pandas as pd
# import dumbass_friends
# import roasting_you_for_things_you_deserve
# from cac import dumbassery
import io
from typing import List, Union, Dict, Tuple, NoReturn
from io import StringIO

# TODO: Might be good to make this an iterable to make paginating easier. Like for x in query... 

class Query():
    base_url = 'http://microbes.gps.caltech.edu:8000/'

    operators = ['[eq]', '[gt]', '[gte]', '[lt]', '[lte]', '[in]']
    symbols = ['[to]', '[or]']
    connector = '[and]'

    def __init__(self, table_name:str, fields:List[str]=[]):

        self.filters = []
        self.fields = fields
        self.table_name = table_name
        self.page = 0

    def equal_to(self, field:str, value):
        if type(value) != str: # If it's not a string, assume it's array-like. 
            self.filters.append(field + '[eq]' + '[or]'.join(list(value)))
        else:
            self.filters.append(f'{field}[eq]{value}')

    def less_than(self, field:str, value):
        self.filters.append(f'{field}[lt]{value}')
         
    def less_than_or_equal_to(self, field:str, value):
        self.filters.append(f'{field}[lte]{value}')
        return stmt.filter(col <= float(value))

    def greater_than(self, field:str, value):
        self.filters.append(f'{field}[gt]{value}')
        return stmt.filter(col > float(value))

    def greater_than_or_equal_to(self, field:str, value):
        self.filters.append(f'{field}[gte]{value}')
        return stmt.filter(col >= float(value))

    def in_range(self, field:str, low, high):
        self.filters.append(f'{field}[in]{low}[to]{high}')

    def add_field(self, field:str):
        self.fields.append(field)


    def get(self, print_url:bool=False) -> pd.DataFrame:
        url = Query.base_url + 'get/' + self.table_name + '?'
        url = url + Query.connector.join(self.fields + self.filters)
        url = url + f'[page]{self.page}' # Add the page number. 

        if print_url: print(url)

        response = requests.get(url)
        if response.status_code > 200:
            raise Exception(response.text)
        else:
            content = requests.get(url).text
            # The partial field will get interpreted as an integer unless stated otherwise.g
            return None if content == '' else pd.read_csv(StringIO(content), index_col=0, dtype={'partial':str})

    def next(self, print_url:bool=False):
        result = self.get(print_url=print_url)
        self.page += 1
        return result 

    def count(self, print_url:bool=False) -> pd.DataFrame:
        url = Query.base_url + 'count/' + self.table_name + '?'
        url = url + Query.connector.join(self.fields + self.filters)
        
        if print_url: print(url)

        content = requests.get(url).text
        return int(content)







