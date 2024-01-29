'''A Python wrapper for the Find-A-Bug REST API.'''
import requests
import pandas as pd
import io
from typing import List, Union, Dict, Tuple, NoReturn

HOST = 'microbes.gps.caltech.edu:8000'


def parse_response(response:requests.Response) -> pd.DataFrame:
    '''Takes a requests Response object, extracts the text, and converts it to a
    pandas DataFrame. An exception is raised if appropriate.

    :param response: The response object obtained using requests.get.
    :return: A pandas DataFrame containing the data in the response. 
    '''
    if response.status_code != 200:
        raise Exception(f'parse_response: {response.text}')
    else:
        data = pd.read_csv(io.StringIO(response.text), index_col=0)
        return data


def get_url(filters:Dict[str, List[str]], resource:str, page:int=0, verbose:bool=False) -> str:
    '''Converts a set of search options to an API URL to be sent to the microbes.caltech.gps.edu server. 

    :param cols: The names of the columns in the database to access. 
    :param filters: The filters to apply to each column, given as a tuple of (operator, value), 
        or a single value (equality operator implied).
    :param resource: The resource table to access (one of 'sequences', 'metadata', or 'annotations')
    :param page: The page of results to retrieve. 
    :return: The URL for accessing the Find-A-Bug web application. 
    '''
    url = f'http://{HOST}/api/{resource}?' 
    for col, vals in filters.items():
        for val in vals:
            url += f'&{col}={val}'
    url =  url + f'&page={page}' # &fmt=csv'
    # Print the URL if the verbose option is specified.
    if verbose: print(url)
    return url


def get_ko_with_genome_id(genome_id:str, page:int=0, verbose:bool=False) -> pd.DataFrame:
    '''Gets all the KO groups associated with a particular genome.

    :param genome_id: The GTDB accession for a particular genome. 
    :param page: The page of results to return. 
    :return: A pandas DataFrame containing the query results. 
    '''

    url = get_url({'genome_id':[genome_id]}, 'annotations', page=page, verbose=verbose)
    return parse_response(requests.get(url)) # Send a request to the web application.


def get_genome_id_with_gene_id(gene_id:str, verbose:bool=False) -> pd.DataFrame:
    
    url = get_url({'gene_id':[gene_id]}, 'sequences', verbose=verbose)
    data = parse_response(requests.get(url))
    return data.genome_id.item()


def get_gtdb_taxonomy_with_genome_id(genome_id:str) -> pd.DataFrame:

    fields = ['gtdb_domain', 'gtdb_class', 'gtdb_family', 'gtdb_order', 'gtdb_phylum', 'gtdb_genus', 'gtdb_species']
    filters = {'genome_id':[genome_id]}
    for field in fields:
        filters[field] = '*' # Select the specified fields, without filtering.
    url = get_url(filters, 'metadata')
    return parse_response(requests.get(url))


def get_ko_with_gene_id(gene_id:str, page:int=0, verbose:bool=False) -> pd.DataFrame:
    '''Gets all the KO groups associated with a particular genome.

    :param gene_id: The GTDB accession for a particular gene. 
    :param page: The page of results to return. 
    :return: A pandas DataFrame containing the query results. 
    '''
    url = get_url({'gene_id':[gene_id]}, 'annotations', page=page, verbose=verbose)
    return parse_response(requests.get(url)) # Send a request to the web application.  


def get_gene_ids_with_genome_id(genome_id:str, page:int=0) -> pd.DataFrame:
    '''Gets all the genes IDs associated with a particular genome. 

    :param genome_id: The GTDB accession for a particular genome. 
    :param page: The page of results to return. 
    :return: A pandas DataFrame containing the query results. 
    '''
    url = get_url({'genome_id':[genome_id]}, 'sequences', page=page)
    return parse_response(requests.get(url)) # Send a request to the web application.  


def get_gene_ids_with_ko(ko:str, page:int=0) -> pd.DataFrame:
    '''Gets all results from the database for a particular KO group. 

    :param ko: The KO group of the genes to be retrieved. 
    :param page: The page of results to return. 
    :return: A pandas DataFrame containing the query results. 
    '''
    url = get_url({'ko':[ko]}, 'annotations', page=page)
    return parse_response(requests.get(url)) # Send a request to the web application.  


def get_sequence_with_gene_id(gene_id:str) -> pd.DataFrame:
    '''Gets the amino acid sequence for a particular gene.

    :param gene_id: The GTDB accession for the gene for which the sequence will be retrieved.
    :return: A pandas DataFrame containing the amino acid sequence. 
    '''
    url = get_url({'gene_id':[gene_id]}, 'sequences')
    return parse_response(requests.get(url)) # Send a request to the web application.  


def get_fields(resource:str) -> List[str]:
    '''Get all fields available within the specified resource table.

    :param resource: The name of the resource. One of 'metadata', 'annotations', or 'sequences.'
    :return: A list of field names.
    '''
    url = f'http://{HOST}/info/{resource}' # ?fmt=csv'
    data = parse_response(requests.get(url))

    return list(data.column_name)


def info(resource:str) -> NoReturn:
    '''Returns the column descriptions for the specified resource.'''
    url = f'http://{HOST}/info/{resource}' # ?fmt=csv'
    data = parse_response(requests.get(url))

    for row in data.itertuples():
        lw = 20 # Line width of the description in number of words.
        description = row.description.split(' ')
        n_words = len(description)
        description = [' '.join(description[i:min(n_words, i + lw)]) for i in range(0, n_words, lw)]
        description = '\n\t'.join(description)

        if row.primary:
            print(f'[PRIMARY KEY] {row.column_name} ({row.data_type}): {description}')
        else:
            print(f'{row.column_name} ({row.data_type}): {description}')
