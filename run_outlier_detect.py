#!/usr/bin/env python
# encoding: utf-8
"""
run_outlier_detect.py

Created by Faisal M. Lalani on March 2021.
flalani@dimagi.com

Using the outlierdetect.py module on CommCare data.
"""

from simple_settings import settings
from os import error
import sys
import outlierdetect
import numpy as np
import pyarrow
import pandas as pd
import sqlalchemy

def generate_df_from_sql_query(table, cnx):
    """Returns a dataframe from specified SQL table.

    Args:
        table: the form to parse.
        test: boolean that indicates limiting the number of rows.
        cnx: the connection to the SQL db.


    Returns:
        a dataframe containing the specified number of submissions for the given form.

    """
    sql_query = ('SELECT * FROM "outlier_detect"."{table}"'.format(
        table=table))
    df = pd.read_sql_query(sql_query, con=cnx)

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
    df['completed_time'] = pd.to_datetime(df['completed_time'], format=date_format)

    #mask = (df['started_time'] >= start_date) & (df['started_time'] < end_date)
    mask = df['started_time'] < date
    df = df.loc[mask]

    return df

def compute_dwell_time(df):
    """Returns a dataframe the average amount of time a user spent in a form.

    Args:
        df: the dataframe to analyze.

    Returns:
        the same dataframe with a column for dwell time.

    """

    df['dwell_time'] = df['completed_time'] - df['started_time']
    df['dwell_time'] = df['dwell_time']/np.timedelta64(1, 's')

    return df

def compute_user_distribution(df_form, user, question):
    """Computes basic distribution stats for a given dataframe and filter.

    Args:
        df_form: the initial form dataframe.
        user: the interviewer to query for.
        question: the question to query for.

    Returns:
        - a dictionary of value counts for the specific user and question
        - the size of the user-specific dataframe

    """
    df_user = df_form.loc[df_form['username'] == user]
    distribution_user = sorted(dict(df_user[question].value_counts(normalize=True, ascending=True).mul(100).round(1)).items())
    n_user = len(df_user)
    average_dwell_time_user = np.mean(df_user['dwell_time'])

    return distribution_user, n_user, average_dwell_time_user

def format_scores(scores, df_form):
    """Formats the interviewer outlier scores.

    Args:
        scores: the outputted defaultdict object from the algorithm.
        df_form: a dataframe of the original form data.

    Returns:
        a dataframe with the columns user_id, question, and score.

    """
    results = []

    i = 1 # To anonymize usernames.

    for interviewer in scores.keys():
        for column in scores[interviewer].keys():
            
            # Grab distribution data for the user.
            distribution_user, n_user, average_dwell_time_user = compute_user_distribution(df_form, interviewer, column)

            # Grab distribution data for all users.
            distribution_total = sorted(dict(df_form[column].value_counts(normalize=True, ascending=True).mul(100).round(1)).items())
            n_total = len(df_form)
            average_dwell_time_total = np.mean(df_form['dwell_time'])

            # Format for dataframe.
            # Use i for user_id if needing to anonymize; otherwise (like for result analysis), use interviewer.
            result = {"user_id": i, "question": column, "score": scores[interviewer][column], "user_distribution": distribution_user, "N_user": n_user, "average_dwell_time_user": average_dwell_time_user, "total_distribution": distribution_total, "N_total": n_total, "average_dwell_time_total": average_dwell_time_total}
            results.append(result)

        i += 1
        
    df_results = pd.DataFrame(results)
    return df_results

if __name__ == '__main__':

    # The db we want to connect to.
    db = settings.DB
    cnx = sqlalchemy.create_engine(f'postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_ADDRESS}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DBNAME}')

    # Read in qualatative annotations to identify interesting questions to examine.
    df_annotations = pd.read_csv('data/annotations/' + db + '.csv')
    df_interesting_annotations = df_annotations.loc[df_annotations["hb outlier score"] > 1]

    # The specific form we want to examine for analysis.
    forms = settings.FORMS

    # Specify a start and end date to filter form data by time.
    #start_date = ''
    #date = '2020-07-01'

    for form in forms:

        print("FORM: ", form)

        form_data_path = 'data/forms/' + db + '/' + form + '.gzip'

        try:
            data = pd.read_parquet(form_data_path)

        except FileNotFoundError:
            # Connect using given properties.
            data = generate_df_from_sql_query(form, cnx)
            # First time calls should save output in csv to eliminate need for future calls for the same data.
            data.to_parquet(form_data_path, compression='gzip', index=False)

        #data = filter_form_data_by_time(data, date)
        data = compute_dwell_time(data)

        #print(data.head())
        data = data[:20000]
        print("SIZE: ", len(data))

        # The distinguishing username field for the algorithm.
        username = 'username'
        
        # Use given annotations to grab a list of questions to analyze, or manually enter specific question IDs.
        questions = list(df_interesting_annotations.loc[df_interesting_annotations["form_name"] == form]["question_id"])
        #print(questions)
        # Compute SVA outlier scores.
        try:

            (sva_scores, agg_col_to_data) = outlierdetect.run_sva(data, username, questions)

            # Format and print results.
            df_results = format_scores(sva_scores, data)
            print(df_results.head())
            
            # Output to CSV.
            output_filename = 'data/results/' + db + '/' + form + '.csv'
            df_results.to_csv(output_filename, index=False)
            
        except Exception as err:
            # Usually Exception errors correspond to not enough aggregation units in the dataset.
            print("FAILED: ", err)
            pass