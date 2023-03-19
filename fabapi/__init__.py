'''
Front-end API for accessing the genome database. All of these functions should
return pandas DataFrame objects with the requested information. 
'''
import requests
import pandas as pd
import io

host = 'microbes.gps.caltech.edu:8000'


# TODO: Some kind of check function which makes sure all the specified options
# are OK. Not sure if I should put it in this file, or a module closer to the
# back end. Maybe both.


def where_to_url(where):
    '''
    Converts the set of options specified in the 'where' keyword argument into
    string for the URL.
    '''
    operator_map = {'=':'eq', '>':'gt', '<':'lt', '<=':'le', '>=':'ge'}
    options = [] 

    for field in where.keys():
        # If a list is given in the options, then join as an or statement.
        if type(where[field]) == list:
            
            for val in where[field]:
                if type(val) == tuple:
                    operator, filter_ = val
                else: # In this case, assume the specified string is something to match
                    operator, filter_ = 'eq', val
    
                # Make sure the operator is in the correct form for the URL.
                operator = operator_map.get(operator, operator)
                options.append(f'{field}={operator};{filter_}')
        
        else: # If only one thing is specified.
            val = where[field]

            if type(val) == tuple:
                operator, filter_ = val
            else: # In this case, assume the specified string is something to match
                operator, filter_ = 'eq', val
            
            # Make sure the operator is in the correct form for the URL.
            operator = operator_map.get(operator, operator)
            options.append(f'{field}={operator};{filter_}')

    # Join the options according to URL format and return.
    return '+'.join(options)

def info():
    '''
    '''


def to_df(result):
    '''
    Convert a result returned by the get function into a pandas DataFrame. 
    '''
    result = result.split('\n')
    start = None
    for i, row in enumerate(result):
        if '*' in row:
            start = i + 1
            break

    cols = result[start].split(',')
    csv = result[i + 1]
    df = pd.read_csv(io.StringIO(csv), sep=',', header=None, names=cols)

    return df


def get(fields, where={}, verbose=True):
    '''
    Send a query to the Find-A-Bug Flask app. 

    args:
        : fields (str or list): Either a single field or a list of fields for
            which to retrieve information. 
    kwargs:
        : where (dict): Specifies search options. Some format options for the
            key, value pairs are as follows:
            (1) 'ko':'KO123'
            (2) 'ko':['KO123', 'KO456'] retrieves all fields where the KO group
              matches EITHER of the specified groups. 
            (3) 'threshold':('>', 500)
            (4) 'threshold':[('>', 500), ('<', 1000)]
        : verbose (bool): True by default. Whether or not to print the
            constructed URL.
    '''
    # If multiple fields are specified, join as a list. 
    if type(fields) == list:
        fields = '+'.join(fields)
    
    # Convert the specified options into a URL string. 
    options = where_to_url(where)

    url = f'http://{host}/{fields}/{options}'
    result = requests.get(url).text
    
    if verbose:
        print(f'GET {url}')

    return result


def count(fields, where={}, verbose=True):
    '''

    args:
        : fields (str or list): Either a single field or a list of fields for
            which to retrieve information. 
    kwargs:
        : where (dict): Specifies search options. Some format options for the
            key, value pairs are as follows:
            (1) 'ko':'KO123'
            (2) 'ko':['KO123', 'KO456'] retrieves all fields where the KO group
              matches EITHER of the specified groups. 
            (3) 'threshold':('>', 500)
            (4) 'threshold':[('>', 500), ('<', 1000)]
        : verbose (bool): True by default. Whether or not to print the
            constructed URL.
    '''
    # If multiple fields are specified, join as a list. 
    if type(fields) == list:
        fields = '+'.join(fields)
    
    # Convert the specified options into a URL string. 
    options = where_to_url(where)

    url = f'http://{host}/{fields}/{options}/count'
    result = requests.get(url).text
    
    if verbose:
        print(f'GET {url}')

    return result


def get_genes_with_score_over_threshold(annotation='kegg'):
    '''
    '''
    pass


def get_genes_in_ko_group(ko):
    '''
    '''
    pass
