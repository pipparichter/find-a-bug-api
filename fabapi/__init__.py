'''Front-end API for accessing the genome database. All of these functions should
return pandas DataFrame objects with the requested information.'''
import requests
import pandas as pd
import io
from typing import List, Union, Dict, Tuple, NoReturn

HOST = 'microbes.gps.caltech.edu:8000'


def get_url(filters:Dict[str, List[str]], resource:str, page:int=None) -> str:
    '''Converts a set of search options to a URL to be sent to the microbes.caltech.gps.edu server. 

    :param cols: The names of the columns in the database to access. 
    :param filters: The filters to apply to each column, given as a tuple of (operator, value), 
        or a single value (equality operator implied).
    :param resource: The resource table to access (one of 'sequences', 'metadata', or 'annotations')
    :param page: The page of results to retrieve. 
    :return: The URL for accessing the Find-A-Bug web application. 
    '''
    url = f'http://{HOST}/{resource}?' 
    for col, vals in filters.items():
        for val in vals:
            url += f'{col}={val}'

    return url + f'&page={page}'


def pd_from_response(response:requests.Response) -> pd.DataFrame:
    '''Parse the text response received from the HTTP server. Converts the data
    received into a pd.DataFrame object.  

    :param response: The response object returned by the Find-A-Bug web application. 
    :return: A pandas DataFrame containing the information in the response. 
    '''
    # Extract the text from the response and remove the header with the time information. 
    csv = response.text.split('-' * 50)[-1]
    df = pd.read_csv(io.StringIO(csv), sep=',')

    # TODO: Should add something to handle a case of a non-200 status code. 
    return df


def get_ko_with_genome_id(genome_id:str, page:int=0) -> pd.DataFrame:
    '''Gets all the KO groups associated with a particular genome_id.

    :param genome_id: The GTDB accession for a particular genome. 
    :param page: The page of results to return. 
    :return: A pandas DataFrame containing the query results. 
    '''

    url = get_url({'genome_id':[genome_id]}, 'annotations', page=page)
    response = requests.get(url) # Send a request to the web application. 
    
    return pd_from_response(response)


def get_genes_ids_with_ko(ko:str, page:int=0) -> pd.DataFrame:
    '''Gets all results from the database for a particular KO group. 

    :param ko: The KO group of the genes to be retrieved. 
    :param page: The page of results to return. 
    :return: A pandas DataFrame containing the query results. 
    '''
    url = get_url({'ko':[ko]}, 'annotations', page=page)
    response = requests.get(url) # Send a request to the web application.  
    
    return pd_from_response(response)



def get_sequence_with_gene_id(gene_id:str) -> pd.DataFrame:
    '''Gets the amino acid sequence for a particular gene.

    :param gene_id: The GTDB accession for the gene for which the sequence will be retrieved.
    :return: A pandas DataFrame containing the amino acid sequence. 
    '''
    url = get_url({'gene_id':[gene_id]}, 'sequences')
    response = requests.get(url) # Send a request to the web application.  
    
    return pd_from_response(response)


# Is this useful?
def get_ko_with_gtdb_taxonomy(taxonomy:str, level:str='phylum') -> pd.DataFrame:
    '''Gets the KO groups of every genome matching a certain taxonomical category. 
    '''
    assert level in ['domain', 'class', 'order', 'phylum', 'genus', 'species']



def info() -> NoReturn:
    '''Returns information about the database, like which tables are present and
    the columns contained in these tables.'''
    url = f'http://{HOST}/info'
    result = requests.get(url).text

    print(result)


if __name__ == '__main__':

    print(get_genes_ids_with_ko('K00075'))
