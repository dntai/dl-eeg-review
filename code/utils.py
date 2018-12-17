"""
Utilities for making literature review figures.

TODO:
- Make sure the data will be loaded correctly wherever the code is run from.
- Write function that makes sure the DataFrame is fine.
"""

import re

import pandas as pd
import numpy as np


def lstrip(list_of_strs, lower=True):
    """Remove left space and make lowercase."""
    return [a.lstrip().lower() if lower else a.lstrip() for a in list_of_strs] 

    
def replace_nans_in_column(df, column_name, replace_by=' '):
    nan_ind = df[column_name].apply(lambda x:
        np.isnan(x) if isinstance(x, float) else False)
    df.loc[nan_ind, column_name] = replace_by
    return df


def tex_escape(text):
    """Add escape character in front of LaTeX special characters in string.

        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
        
        From https://stackoverflow.com/a/25875504
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) 
        for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)


def split_column_with_multiple_entries(df, col, ref_col='Citation', sep=';\n', 
                                       lower=True):
    """Split the content of a column that contains more than one value per cell.
    
    Split the content of cells that contain more than one value. Some cells 
    contain two or more values for a single data item, e.g., 
        
        Number of subjects: '15, 203, 23'
        
    A DataFrame where each row contains a single value per cell is returned.
    
    Args:
        df (pd.DataFrame)
        col (str): name of the column to split
        
    Keyword Args:
        ref_col (str or list of str): identifier column(s) to use to identify 
            the row of origin of a splitted value.
        sep (str): separator between multiple values
        lower (bool): if True, make all values lowercase
        
    Returns:
        (pd.DataFrame)
    """
    df['temp'] = df[col].str.split(sep).apply(lstrip, lower=lower)
    
    if not isinstance(ref_col, list):
        ref_col = [ref_col]
    
    value_per_row = list()
    for i, items in df[[*ref_col, 'temp']].iterrows():
        for m in items['temp']:
            value_per_row.append([i, *items[ref_col].tolist(), m])

    return pd.DataFrame(value_per_row, columns=['paper nb', *ref_col, col])


def extract_main_domains(df):
    """Create column with the main domains.

    The main domains were picked by looking at the data and going with what made
    sense (there is no clear rule for defining them).
    """
    main_domains = ['Epilepsy', 'Sleep', 'BCI', 'Affective', 'Cognitive', 
                    'Improvement of processing tools', 'Generation of data']
    domains_df = df[['Domain 1', 'Domain 2', 'Domain 3', 'Domain 4']]
    df['Main domain'] = [row[row.isin(main_domains)].values[0] 
        if any(row.isin(main_domains)) else 'Others' 
        for ind, row in domains_df.iterrows()]

    return df


def load_data_items(start_year=2010):
    """Load data items table.

    TODO:
    - Normalize column names?
    - Double check all the required columns are there?
    """
    fname = '../data/data_items.csv'
    df = pd.read_csv(fname, header=1)

    # A little cleaning up
    df = df.dropna(axis=0, how='all')
    df = df.dropna(axis=1, how='all', thresh=int(df.shape[0] * 0.1))
    df = df[df['Year'] >= start_year]

    df = extract_main_domains(df)

    return df


def load_reported_results_data():
    """Load table of reported results (second tab on spreadsheet).
    """
    fname = '../data/reporting_results.csv'
    df = pd.read_csv(fname, header=0)
    df = df.drop(columns=['Unnamed: 0', 'Title', 'Comment'])
    df['Result'] = pd.to_numeric(df['Result'], errors='coerce')
    df = df.dropna()

    def extract_model_type(x):
        if 'arch' in x:
            out = 'Proposed'
        elif 'trad' in x:
            out = 'Baseline (traditional)'
        elif 'dl' in x:
            out = 'Baseline (deep learning)'
        else:
            raise ValueError('Model type {} not supported.'.format(x))
        
        return out

    df['model_type'] = df['Model'].apply(extract_model_type)

    return df


def check_data_items(df):
    """Check data items to make sure it contains the right stuff. 

    - Years
    - Number of layers
    - Domains
    - Checked by 2 people
    - Invasive

    TODO:
    - Should this be some kind of unit test?
    """
    pass


def wrap_text(string, max_char=25):
    """Wrap string at `max_char` per line.

    Args:
        string (str): string to be wrapped.

    Keyword Args:
        max_char (int): maximum number of characters per line.

    Returns:
        (str): wrapped string.
    """
    string_parts = string.split()
    if len(string) > max_char and len(string_parts) > 1:
        out_string = string_parts[0]
        line_len = len(out_string)
        for i in string_parts[1:]:
            if line_len + 1 + len(i) > max_char:
                out_string += '\n'
                line_len = len(i)
            else:
                out_string += ' '
                line_len += len(i) + 1
            out_string += i
    else:
        out_string = string
        
    return out_string