'''
Front-end API for accessing the genome database. All of these functions should
return pandas DataFrame objects with the requested information. 
'''
import requests
import pandas as pd
import io

host = 'microbes.gps.caltech.edu:8000'


def generate_url(cols, filters, type_, page=None):
    '''
    Converts the set of options specified in the 'where' keyword argument, as
    well as the requested columns, into a URL, to be sent to the HTTP server. 

    args:
        : cols (list of str): A list specifying the columns to grab. 
        : filters (dict): A dictionary of the form {col:[(op, val), ...]} or
            {col:[val]}. Each each col and op is a string, and the val can be a
            number or a string. 
        : type_ (str): The type of request to send.

    kwargs:
        : page (int): The page to grab from the database. Default page size is
            100, and the default page number is zero (first page). 
    '''
    # Include page information 
    if page is not None:
        headers = {'page':str(page)}
    else: 
        headers = {}

    # If multiple cols are specified, join as a list. 
    headers['cols'] = ','.join(cols)
 
    filter_list = []
    for col in filters.keys():
        for filter_ in filters[col]:
            if type(filter_) == tuple:
                op, val = filter_
            else: # In this case, assume the specified string is something to match
                op, val = '=', filter_

            # Make sure the operator is in the correct form for the URL.
            filter_list.append(f'{col};{op};{val}')
    headers['filters'] = ','.join(filter_list)

    return f'http://{host}/{type_}', headers


def to_df(response, print_sql_query=False):
    '''
    Parse the text response received from the HTTP server. Converts the data
    received into a pd.DataFrame object.  

    args:
        : response (requests.Response): The response from the HTTP server. 
    
    kwargs:
        : print_sql_query (bool): Whether or not to print the raw SQL query sent to
            the database. 
    '''
    response = response.text.split('\n')
    start = None
    for i, row in enumerate(response):
        if '-' in row:
            start = i + 1
            break
    
    if print_sql_query:
        sql_query = response[2:start - 1]
        print('\n'.join(sql_query))    

    cols = response[start].split(',')
    csv = '\n'.join(response[start + 1:])
    df = pd.read_csv(io.StringIO(csv), sep=',', names=cols)

    return df


# TODO: Will need to manually create an index for this. Something like, "CREATE
# idx_ko ON TABLE... 

def get_by_ko(ko,
        gene_name=True,
        genome_id=False,
        as_df=True):
    '''
    Gets all results from the database for a particular KO group. 
    '''
    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(ko) == str:
        ko = [ko]
    
    # Generate the list of columns to grab from the database. 
    cols = ['ko']
    if gene_name:
        cols.append('gene_name')
    if genome_id:
        cols.append('genome_id')
    if len(cols) < 1:
        raise ValueError('At least one column must be specified.')
    
    url, headers = generate_url(cols, {'ko':ko}, 'get')
    response = requests.get(url, headers=headers)
 
    if response.status_code == 500: # In case of an error...
        print(response.text)
        return None
   
    if as_df:
        return to_df(response, print_sql_query=True)
    else:
        return response


def get_by_gene_name(gene_name, 
        genome_id=True, 
        sequence=True,
        page=0,
        as_df=True):
    '''
    Get results from the database corresponding to a particular gene_name
    target. Only returns 100 results. 
    '''
    if (page is None) and sequence:
        msg = 'When grabbing sequences from the database, a page must be specified.'
        raise ValueError(msg)

    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(gene_name) == str:
        gene_name = [gene_name]
    
    cols = ['gene_name']
    if genome_id:
        cols.append('genome_id')
    if sequence:
        cols.append('sequence')

    url, headers = generate_url(cols, {'gene_name':gene_name}, 'get', page=page)
    response = requests.get(url, headers=headers)

    if response.status_code == 500: # In case of an error...
        print(response.text)
        return None

    if as_df:
        return to_df(response, print_sql_query=True)
    else:
        return response


def get_by_genome_id(genome_id, 
        gtdb_taxonomy=True, 
        ncbi_taxonomy=False,
        ssu_gg_taxonomy=False,
        as_df=True):
    '''
    Gets all results from the database for a particular genome_id. 
    '''
    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(genome_id) == str:
        genome_id = [genome_id]
 
    cols = ['genome_id']

    taxonomy = ['domain', 'phylum', 'class', 'order', 'genus', 'species']
    if gtdb_taxonomy:
        cols += [f'gtdb_{t}' for t in taxonomy]
    if ncbi_taxonomy:
        cols += [f'ncbi_{t}' for t in taxonomy]
    if ssu_gg_taxonomy:
        cols += [f'ssu_gg_{t}' for t in taxonomy]

    url, headers = generate_url(cols, {'genome_id':genome_id}, 'get')
    response = requests.get(url, headers=headers)
 
    if response.status_code == 500: # In case of an error...
        print(response.text)
        return None
   
    if as_df:
        return to_df(response, print_sql_query=True)
    else:
        return response

def info():
    '''
    Returns information about the database, like which tables are present and
    the columns contained in these tables. 
    '''
    url = f'http://{host}/info'
    result = requests.get(url).text

    print(result)


