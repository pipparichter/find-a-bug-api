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

# TODO: Add another function which allows you to look at KO groups for a specific
# genome ID. 

def get_all_ko_with_genome_id(genome_id, as_df=True):
    '''
    Get all the KO groups associated with a particular genome_id.
    '''
    pass



def get_genes_with_ko(ko, as_df=True):
    '''
    Gets all results from the database for a particular KO group. Returns a
    string or DataFrame containing the gene_name, genome_id, and ko group for
    all records which match the specified KO group(s). 

    args:
        : ko (str or list of str): The KO group or groups to match against when
            grabbing the gene information from the database.
    kwargs:
        : as_df (bool): True by default. Specifies whether or not to
            automatically parse the text response from the website to a
            DataFrame.
    '''
    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(ko) == str:
        ko = [ko]
    
    # The list of columns to grab from the database. 
    cols = ['ko', 'gene_name', 'genome_id']
    
    url, headers = generate_url(cols, {'ko':ko}, 'get')
    response = requests.get(url, headers=headers)
 
    if response.status_code == 500: # In case of an error...
        print(response.text)
        return None
   
    if as_df:
        return to_df(response, print_sql_query=True)
    else:
        return response


def get_sequence_count_with_gene_name(gene_name):
    '''
    Retrieves the total number of results from a call (as an integer) to the database using the
    get_sequence_by_gene_name function. 
     
    args:
        : gene_name (str or list of str): The gene name(s) to match against in the
            database. 
    '''

    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(gene_name) == str:
        gene_name = [gene_name]
 
    url, headers = generate_url(['gene_name'], {'gene_name':gene_name}, 'count')
    response = requests.get(url, headers=headers)
    
    if response.status_code == 500: # In case of an error...
        print(response.text)
        return None

    df = to_df(response, print_sql_query=False)
    
    return df.iloc[0]


def get_sequence_by_gene_name(gene_name, 
        page=0,
        as_df=True):
    '''
    Return 100 sequences associated with a particular gene name(s). Also returns
    the genome_id associated with the gene.

    args:
        : gene_name (str or list of str): The gene name(s) to match against in the
            database. 
    kwargs:
        : page (int): The page of results to return. Only 100 results are returned at
            once, so pagination is required. 
        : as_df (bool): True by default. Specifies whether or not to
            automatically parse the text response from the website to a
            DataFrame.    
    '''

    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(gene_name) == str:
        gene_name = [gene_name]
    
    cols = ['gene_name', 'genome_id', 'sequence']

    url, headers = generate_url(cols, {'gene_name':gene_name}, 'get', page=page)
    response = requests.get(url, headers=headers)

    if response.status_code == 500: # In case of an error...
        print(response.text)
        return None

    if as_df:
        return to_df(response, print_sql_query=False)
    else:
        return response


# TODO: Grab by a taxonomical category function -- specify by dictionary. 

def get_taxonomy_with_genome_id(genome_id, as_df=True):
    '''
    Gets the taxonomical information from the database for a particular genome_id or genome_ids. 

    args:
        : genome_id (str or list of str): One or more genome ID to match against
            the database genome_id column. 
    kwargs: 
        : as_df (bool): True by default. Specifies whether or not to
            automatically parse the text response from the website to a
            DataFrame.    
        
    '''
    # Can be either be a string or a list of strings; make sure it's a list. 
    if type(genome_id) == str:
        genome_id = [genome_id]
 
    cols = ['genome_id']

    taxonomy = ['domain', 'phylum', 'class', 'order', 'genus', 'species']
    # Only grab the GTDB taxonomy. 
    cols += [f'gtdb_{t}' for t in taxonomy]

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


