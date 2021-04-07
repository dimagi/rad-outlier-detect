#!/usr/bin/env python
# encoding: utf-8
"""
analyze_results.py

Created by Faisal M. Lalani on March 2021.
flalani@dimagi.com

Uses calculated outlier detection results to do further analysis.
"""

from simple_settings import settings
import pandas as pd
import numpy as np
from scipy import stats

def generate_descriptive_statistics(df):
    """Computes general statistics about a dataframe.

    Args:
        df: the dataframe to analyze.

    Returns:
        a dataframe with a variety of stats measured.

    TODO:
        - add more than just pandas given function.

    """
    return df_results.describe()

def compute_score_statistics(df, metric, q):
    """Finds descriptive statistics for scores over time for a given metric in an outlier results dataset.

    Args:
        - the form outlier data for a specific time period to analyze.
        - the metric to find score stats by.
        - the quarter.

    Returns:
        - a list of dicts with ids and that id's score statistics for the quarter.

    """

    score_stats = []

    for i in set(df[metric]):
        df_i = df.loc[df[metric] == i]

        # Compute the average score for the id.
        average_score = np.mean(df_i['score'])
        min_score = np.min(df_i['score'])
        max_score = np.max(df_i['score'])
        mode_score = stats.mode(df_i['score'])
        median_score = np.median(df_i['score'])

        average_score_key_string = 'average_score_' + str(q)
        min_score_key_string = 'min_score_' + str(q)
        max_score_key_string = 'max_score_' + str(q)
        mode_score_key_string = 'mode_score_' + str(q)
        median_score_key_string = 'median_score_' + str(q)

        score_stats.append({metric: i, average_score_key_string: average_score, 
        min_score_key_string: min_score,
        max_score_key_string: max_score,
        mode_score_key_string: mode_score,
        median_score_key_string: median_score})

    return score_stats

if __name__ == '__main__':

    # The number of quarters (3 months) to analyze.
    number_of_quarters = 1

    for form in settings.FORMS[:1]:

        print("FORM: ", form)

        user_trends = []
        question_trends = []

        for q in range(1,number_of_quarters+1):
            try:
                # Grab a specific quarter's outlier results.
                form_results_path = 'data/results/' + settings.DB + '/cumulative/' + form + '_quarter' + str(q) + '.csv'
                df_results = pd.read_csv(form_results_path)
            
                # Sort dataframe by outlier score.
                df_results = df_results.sort_values('score')

                quarter_user_score_stats = compute_score_statistics(df_results, 'user_id', q)
                user_trends.extend(quarter_user_score_stats)

                quarter_question_score_stats = compute_score_statistics(df_results, 'question', q)
                question_trends.extend(quarter_question_score_stats)

            except FileNotFoundError:
                pass

        try:
            # Create a dataframe from the lists of trend dicts.
            df_user_trends = pd.DataFrame(user_trends)
            df_question_trends = pd.DataFrame(question_trends)

            # We need to group the same users together but keep their score stats for each quarter.
            # If we replace the NAs by 0, we can sum each column and condense the dataframe.
            df_user_trends = df_user_trends.fillna(0)
            df_user_trends = df_user_trends.groupby('user_id', as_index=False).sum()

            # Same for question trends.
            df_question_trends = df_question_trends.fillna(0)
            df_question_trends = df_question_trends.groupby('question', as_index=False).sum()

            # We can drop the user_ids column for anonymity.
            df_user_trends.drop('user_id', axis=1, inplace=True)

            # Output to CSV.
            output_filename_users = 'data/results/' + settings.DB + '/user_trends/' + form + '.csv'
            df_user_trends.to_csv(output_filename_users)

            output_filename_questions = 'data/results/' + settings.DB + '/question_trends/' + form + '.csv'
            df_question_trends.to_csv(output_filename_questions)

        except KeyError as err:
            # KeyError corresponds to a user trend file not havign a 'user_id' column, which only happens if it's empty.
            print("FAILED: ", err)
            pass