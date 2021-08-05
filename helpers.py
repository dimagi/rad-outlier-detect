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

def read_prev_results(project, form):
    """Reads a previously run CommCare submission file's algorithm output. Useful to grab categorical questions that were previously annotated in case you want to run the algorithm on the form again.

    Args:
        project: the name of the project.
        form: the name of the submission history file.

    Returns:
        a list of categorical questions.

    """

    print("Reading previous form results... ", end=' ')

    results_path = 'data/results/' + project + '/' + form + '.csv'
    
    df_prev_results = pd.read_csv(results_path)

    print("Successfully read previous results from local path.")

    questions = list(set(df_prev_results['question']))

    return questions

def clean_form(df_form, user_id, questions):
    """Cleans a dataframe of a CommCare form by hashing usernames and filtering out non-categorical columns.

    Args:
        df_form: the dataframe of the submission history file.
        questions: a list of non-categorical questions in the form.

    Returns:
        a cleaned and hashed dataframe of the form.

    """

    print("Cleaning form... ", end=' ')

    # For datetime calculations or if doing historical trend analysis.
    df_form = convert_col_to_datetime(df_form)

    columns_to_copy = [user_id] + questions
    df_form_cleaned = df_form[columns_to_copy].copy()
    #df_form_cleaned[user_id] = df_form_cleaned[user_id].apply(hash_string)
    
    # Replace Nones with a value that can be subscriptable.
    df_form_cleaned = df_form_cleaned.fillna(value='missing')

    print("Done.")

    return df_form_cleaned

def format_scores(scores, date=None):
    """Formats the interviewer outlier scores.

    Args:
        scores: the outputted defaultdict object from the algorithm.

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
            n_user = sum(observed.values())
            n_total = sum(expected.values())
            normalized_observed = normalize_value_counts(observed) if n_user != 0 else 0
            normalized_expected = normalize_value_counts(expected) if n_total != 0 else 0

            if date:
                result = {"user": interviewer, 
                      "outlier_score": score,
                      "N_user": sum(observed.values()),
                      "date": date}
            else:
                result = {"user": interviewer, 
                      "question": column, 
                      "outlier_score": score,
                      "user_distribution": observed,
                      "total_distribution": expected,
                      "user_distribution_normalized": normalized_observed,
                      "total_distribution_normalized": normalized_expected,
                      "N_user": n_user, 
                      "N_total": n_total}
            
            results.append(result)
            
    df_results = pd.DataFrame(results)
    df_results = df_results.replace([np.inf, -np.inf], np.nan)

    # Apply a score label by dividing all scores into quartiles.
    q = list(df_results['outlier_score'].quantile([0.00, 0.25, 0.50, 0.75, 1.00]))
    df_results['score_label'] = df_results.apply(lambda x: assign_label(x['outlier_score'], q), axis=1)

    # Sort results.
    sort_parameter = 'user' if date else 'outlier_score'
    df_results = df_results.sort_values(by=[sort_parameter], ascending=False)

    print("Done.")
    
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