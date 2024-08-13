import requests
import pandas as pd
import io
from typing import List, Union, Dict, Tuple, NoReturn
from io import StringIO

# TODO: Might be good to make this an iterable to make paginating easier. Like for x in query... 

class Query():

    operators = ['[eq]', '[gt]', '[gte]', '[lt]', '[lte]', '[in]']
    symbols = ['[to]', '[or]']
    connector = '[and]'

    base_url = None

    def __init__(self, table_name:str, fields:List[str]=[]):

        self.filters = []
        self.fields = fields
        self.url = type(self).base_url + f'/{table_name}?'

    def equal_to(self, field:str, value):
        if type(value) == list:
            self.filters.append(field + '[eq]' + '[or]'.join(value))
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

    def get_url(self):
        url = self.url + Query.connector.join(self.fields)
        url = url + Query.connector.join(self.filters)
        return url

    def submit(self) -> pd.DataFrame:
        url = self.get_url()
        content = requests.get(url).text
        print(content)
        return None if content == '' else pd.read_csv(StringIO(content), index_col=0)



class CountQuery(Query):

    base_url = 'http://microbes.gps.caltech.edu:8000/count'

    def __init__(self, table_name:str):

        super().__init__(table_name)


# TODO: Need to figure out what the database does when the number of pages exceeds the number of entries. 
# Apparently when offset value overshoots, no rows are returned.
class GetQuery(Query):
    
    base_url = 'http://microbes.gps.caltech.edu:8000/get'

    def __init__(self, table_name:str):

        super().__init__(table_name)
        self.page = 0

    def get_url(self):
        return Query.get_url(self) + f'[page]{self.page}'

    def next(self):
        result = self.submit()
        self.page += 1
        return result 





