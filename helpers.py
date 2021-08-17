# Helper Functions
# Dropping a lot of the uncategorizable functions that I use throughout the script here.

import hashlib
import numpy as np
import pandas as pd
from scipy import stats
import sqlalchemy

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

    print("Reading form... ", end=' ')

    form_path = 'data/forms/' + form + '.gzip'
    
    try:

        df_form = pd.read_parquet(form_path)
        print("Successfully read form from local path.")

    except FileNotFoundError:

        # Connect using given properties.
        cnx = sqlalchemy.create_engine(f'postgresql://{username}:{password}@{address}:{port}/{dbname}')
        sql_query = ('SELECT * FROM "{path}"."{table}"'.format(
            path=project_path, table=form))
        df_form = pd.read_sql_query(sql_query, con=cnx)
        # First time calls should save output in csv to eliminate need for future calls for the same data.
        df_form.to_parquet(form_path, compression='gzip', index=False)

        print("Successfully downloaded form from server and saved to local path.")

    return df_form

def clean_form(df_form, user_id, questions):
    """Cleans a dataframe of a CommCare form by hashing usernames and filtering out non-categorical columns.

    Args:
        df_form: the dataframe of the submission history file.
        user_id: the column header that corresponds to the name of the interviewers.
        questions: a list of non-categorical questions in the form.

    Returns:
        a cleaned and hashed dataframe of the form.
    """

    print("Cleaning form... ", end=' ')

    # For datetime calculations or if doing historical trend analysis.
    df_form = convert_col_to_datetime(df_form)

    # Hash the usernames and remove non-categorical columns.
    columns_to_copy = [user_id] + questions
    df_form_cleaned = df_form[columns_to_copy].copy()
    df_form_cleaned[user_id] = df_form_cleaned[user_id].apply(hash_string)
    
    # Replace Nones with a value that can be subscriptable.
    df_form_cleaned = df_form_cleaned.fillna(value='missing')

    print("Done.")

    return df_form_cleaned

def format_scores(scores, date=None):
    """Formats the interviewer outlier scores.

    Args:
        scores: the outputted defaultdict object from the algorithm.
        date: if a date is provided, format the output in a different way.

    Returns:
        a dataframe with relevant columns displaying outlier score, corresponding labels, and frequencies.
    """

    print("Formatting results... ", end=' ')

    results = []

    for interviewer in scores.keys():
        for column in scores[interviewer].keys():
            
            score = scores[interviewer][column]['score']
            observed = scores[interviewer][column]['observed_freq']
            expected = scores[interviewer][column]['expected_freq']
            p_value = scores[interviewer][column]['p_value']
            n_user = sum(observed.values())
            n_total = sum(expected.values())
            normalized_observed = normalize_value_counts(observed) if n_user != 0 else 0
            normalized_expected = normalize_value_counts(expected) if n_total != 0 else 0

            if date:
                result = {"user": interviewer, 
                      "outlier_score": score,
                      "N_user": n_user,
                      "date": date}
            else:
                result = {"user": interviewer, 
                      "question": column, 
                      "outlier_score": scores[interviewer][column]['score'],
                      "user_distribution": observed,
                      "total_distribution": expected,
                      "user_distribution_normalized": normalized_observed,
                      "total_distribution_normalized": normalized_expected,
                      "N_user": n_user, 
                      "N_total": n_total,
                      "p_value": p_value}
            
            results.append(result)
        
    # Convert the resulting dictionary into a dataframe.
    df_results = pd.DataFrame(results)
    df_results = df_results.replace([np.inf, -np.inf], np.nan)

    # Apply a score label by p-value thresholds.
    df_results['score_label'] = df_results.apply(lambda x: assign_label(x['p_value']), axis=1)

    # Sort results.
    sort_parameter = 'user' if date else 'outlier_score'
    df_results = df_results.sort_values(by=[sort_parameter], ascending=False)

    print("Done.")
    
    return df_results

def hash_string(string):
    """Return a SHA-256 hash of the given string.

    Args:
        string: the string to hash.

    Returns:
        a hashed version of the string.
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def normalize_value_counts(frequencies):
    """Format the float frequencies into nice rounded percentages.

    Args:
        frequencies: the value counts to normalize.

    Returns:
        a normalized version of the frequencies dictionary.
    """
    n = sum(frequencies.values())
    normalized_frequencies = {}
    for r in list(frequencies.keys()):
        normalized_frequencies[r] = round(100 * frequencies[r] / float(n), 1)
    return normalized_frequencies  

def assign_label(x):
    """Assigns labels to quartiles in a dataset.

    Args:
        x: the value the labels should correspond to.

    Returns:
        a label based on where the value falls in a given threshold.
    """
    if x <= 0.0001:
        return 'Very Surprising'
    elif x >= 0.0001 and x <= 0.01:
        return 'Surprising'
    elif x >= 0.01 and x <= 0.05:
        return 'Little Surprising'
    elif x >= 0.05:
        return 'Not Surprising'

def convert_col_to_datetime(df):
    """Returns a dataframe with the relevant columns converted to the proper datetime format.

    Args:
        df: the dataframe to analyze.

    Returns:
        the same dataframe filtered by a given time.
    """

    date_format = '%Y-%m-%d %H:%M:%S'
    df['started_time'] = pd.to_datetime(df['started_time'], format=date_format)
    df['completed_time'] = pd.to_datetime(df['completed_time'], format=date_format)

    return df

def filter_form_data_by_time(df, start_date, end_date):
    """Returns a dataframe filtered by a given time.

    Args:
        df: the dataframe to analyze.
        start_date: the start_date to filter by.
        end_date: the end_date to filter by.

    Returns:
        the same dataframe filtered by a given time.
    """

    mask = (df['started_time'] >= start_date) & (df['started_time'] < end_date)
    df = df.loc[mask]

    return df