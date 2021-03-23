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

def find_average_scores(df, metric, q):
    """Finds the average score for a given metric in an outlier results dataset.

    Args:
        - the form outlier data for a specific time period to analyze.
        - the metric to find average scores by.
        - the quarter.

    Returns:
        - a list of dicts with ids and that id's average scores for the quarter.

    """

    average_scores = []

    ids = list(set(df[metric]))

    for i in ids:
        df_i = df.loc[df[metric] == i]

        # Compute the average score for the id.
        average_score = np.mean(df_i['score'])

        score_key_string = 'average_score_' + str(q)
        average_scores.append({metric: i, score_key_string: average_score})

    return average_scores

if __name__ == '__main__':

    # The db we want to connect to.
    db = settings.DB
    forms = settings.FORMS

    # The number of quarters (3 months) to analyze.
    number_of_quarters = 8

    for form in forms:

        print("FORM: ", form)

        user_trends = []
        question_trends = []

        q = 1

        while q <= number_of_quarters:
            try:
                # Grab a specific quarter's outlier results.
                form_results_path = ''
                df_results = pd.read_csv(form_results_path)
            
                # Sort dataframe by outlier score.
                df_results = df_results.sort_values('score')

                quarter_average_user_scores = find_average_scores(df_results, 'user_id', q)
                user_trends.extend(quarter_average_user_scores)

                quarter_average_question_scores = find_average_scores(df_results, 'question', q)
                question_trends.extend(quarter_average_question_scores)

            except FileNotFoundError:
                pass

            q += 1

        try:
            # Create a dataframe from the lists of trend dicts.
            df_user_trends = pd.DataFrame(user_trends)
            df_question_trends = pd.DataFrame(question_trends)

            # We need to group the same users together but keep their average scores for each quarter.
            # If we replace the NAs by 0, we can sum each column and condense the dataframe.
            df_user_trends = df_user_trends.fillna(0)
            df_user_trends = df_user_trends.groupby('user_id', as_index=False).sum()

            # Same for question trends.
            df_question_trends = df_question_trends.fillna(0)
            df_question_trends = df_question_trends.groupby('question', as_index=False).sum()

            # We can drop the user_ids column for anonymity.
            df_user_trends.drop('user_id', axis=1, inplace=True)

            # Output to CSV.
            output_filename_users = ''
            df_user_trends.to_csv(output_filename_users)

            output_filename_questions = ''
            df_question_trends.to_csv(output_filename_questions)

        except KeyError as err:
            # KeyError corresponds to a user trend file not havign a 'user_id' column, which only happens if it's empty.
            print("FAILED: ", err)
            pass