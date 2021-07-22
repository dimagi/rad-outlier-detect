# Helper Functions
# Dropping a lot of the uncategorizable functions that I use throughout the script here.

import hashlib
import numpy as np
import pandas as pd
from scipy import stats
import sqlalchemy

# If you're running the script through iPython, uncomment this function.
# def config_ipy():
#     """Start the script with this.
#     """
#     %load_ext autoreload
#     %autoreload 2

def read_commcare_form(project_path, form, username=None, password=None, address=None, port=None, dbname=None):
    """Reads a CommCare project's form's submission history file.

    Args:
        project_path: the location of the table.
        form: the name of the submission history file.
        username: PostGres username
        password: PostGres password
        address: PostGres address
        port: PostGres port
        dbname: PostGres database name

    Returns:
        a dataframe of the form.

    """
    form_path = 'data/forms/' + form + '.gzip'
    
    try:
        df_form = pd.read_parquet(form_path)

    except FileNotFoundError:
        # Connect using given properties.
        cnx = sqlalchemy.create_engine(f'postgresql://{username}:{password}@{address}:{port}/{dbname}')
        sql_query = ('SELECT * FROM "{path}"."{table}"'.format(
            path=project_path, table=form))
        df_form = pd.read_sql_query(sql_query, con=cnx)
        # First time calls should save output in csv to eliminate need for future calls for the same data.
        df_form.to_parquet(form_path, compression='gzip', index=False)

    return df_form

def clean_form(df_form, questions):
    """Cleans a dataframe of a CommCare form by hashing usernames and filtering out non-categorical columns.

    Args:
        df_form: the dataframe of the submission history file.
        questions: a list of non-categorical questions in the form.

    Returns:
        a cleaned and hashed dataframe of the form.

    """
    columns_to_copy = ['owner_name'] + questions
    df_form_cleaned = df_form[columns_to_copy].copy()
    df_form_cleaned['username'] = df_form_cleaned['username'].apply(hash_string)

    # Replace Nones with a value that can be subscriptable.
    df_form_cleaned = df_form_cleaned.fillna(value='missing')

    return df_form_cleaned

def format_scores(scores, date=None):
    """Formats the interviewer outlier scores.

    Args:
        scores: the outputted defaultdict object from the algorithm.

    Returns:
        a dataframe with relevant columns displaying outlier score, corresponding labels, and frequencies.

    """
    results = []

    for interviewer in scores.keys():
        for column in scores[interviewer].keys():
            
            score = scores[interviewer][column]['score']
            observed_frequencies = scores[interviewer][column]['observed_freq']
            expected_frequencies = scores[interviewer][column]['expected_freq']

            if date:
                result = {"user": interviewer, 
                      "outlier_score": score,
                      "by_date": date}
            else:
                result = {"user": interviewer, 
                      "question": column, 
                      "outlier_score": score,
                      "user_distribution": observed_frequencies,
                      "total_distribution": expected_frequencies,
                      "user_distribution_normalized": normalize_value_counts(observed_frequencies),
                      "total_distribution_normalized": normalize_value_counts(expected_frequencies),
                      "N_user": sum(observed_frequencies.values()), 
                      "N_total": sum(expected_frequencies.values())}
            
            results.append(result)
            
    df_results = pd.DataFrame(results)
    df_results = df_results.replace([np.inf, -np.inf], np.nan)

    # Apply a score label by dividing all scores into quartiles.
    q = list(df_results['outlier_score'].quantile([0.00, 0.25, 0.50, 0.75, 1.00]))
    df_results['score_label'] = df_results.apply(lambda x: assign_label(x['outlier_score'], q), axis=1)

    # Sort results.
    sort_parameter = 'user' if date else 'outlier_score'
    df_results = df_results.sort_values(by=[sort_parameter], ascending=False)
    
    return df_results

def hash_string(string):
    """Return a SHA-256 hash of the given string.
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def normalize_value_counts(frequencies):
    """Format the float frequencies into nice rounded percentages.
    """
    n = sum(frequencies.values())
    normalized_frequencies = {}
    for r in list(frequencies.keys()):
        normalized_frequencies[r] = round(100 * frequencies[r] / float(n), 1)
    return normalized_frequencies  

# 
def calc_p_value(x1, x2):
    """We need to do a chi squared test to get a p-value for the distributions.
    We have an observed distribution, but the expected
    distribution needs to be calculated based on the percentage value counts.
    """
    x1_num = [k[1] for k in x1]
    x2_num = [k[1] for k in x2]
    return stats.chisquare(x1_num, x2_num)[1]

def assign_label(x, q):
    """Assigns labels to quartiles in a dataset.

    Args:
        x: the list the labels should correspond to.
        q: the boundaries to use to break up the list.
    """
    if x <= q[1]:
        return 'Not Surprising'
    elif x <= q[2]:
        return 'Little Surprising'
    elif x <= q[3]:
        return 'Surprising'
    elif x <= q[4]:
        return 'Very Surprising'
    
def format_for_commcare(df, n):
    """Format the dataframe to be as easy as possible to upload as a lookup to CommCare.
    # TODO: add index sheet!
    """

    sample = df.sample(n = n)
    sample.index = np.arange(1, len(sample) + 1)
    df.columns = ['field: ' + str(col) for col in df.columns]
    return df

def filter_form_data_by_time(df, date):
    """Returns a dataframe filtered by a given time.

    Args:
        df: the dataframe to analyze.
        time: the time to filter by.

    Returns:
        the same dataframe filtered by a given time.

    """

    date_format = '%Y-%m-%d %H:%M:%S'
    df['started_time'] = pd.to_datetime(df['started_time'], format=date_format)
    mask = df['started_time'] < date
    df = df.loc[mask]

    return df