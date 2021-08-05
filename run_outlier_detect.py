"""
run_outlier_detect.py

Created by Faisal M. Lalani.
flalani@dimagi.com

Runs Ben Birnbaum's outlier detection algorithm on a CommCare form submission dataset and formats it with frequency data.
"""

# %% [markdown]
# # Run Outlier Detect
# ### Faisal M. Lalani
# ---

# %% [markdown]
# ## Imports
import datetime as dt
import helpers
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from os import error
import outlier_detect
from simple_settings import settings

# %%
# Uncomment if running as an iPython script.
# helpers.config_ipy()

# %% [markdown]
# ## CommCare Data
# Load in a form from a CommCare project and pre-process it for a smooth run through the algorithm.

# %%
def run_algorithm(df_form, questions, date=None):
    """Runs the MMA algorithm on the given forms.

    Args:
        form: the dataframe of the form to run the algorithm on.
        date: if not empty, formats data for historical trend analysis.

    Returns:
        formatted output of the algorithm.
    """

    # Run the MMA algorithm.
    (mma_scores, _) = outlier_detect.run_mma(df_form, settings.FORM_USER_ID, questions)

    # Format the scores for easy reading.
    df_results = helpers.format_scores(mma_scores, date)

    return df_results

# %%
def find_historical_outliers(df_form, questions):
    """Runs the MMA algorithm on the given forms, filtered by given dates.

    Args:
        df_form: the dataframe of the form to run the algorithm on.
        questions: the set of questions to run the algorithm on.

    Returns:
        a culminated dataframe full of results from different date ranges.
    """

    df_historical = pd.DataFrame()

    # Loop thorugh dates.
    for dates in settings.DATES:

        date_range = dates[0] + ' - ' + dates[1]
        print(date_range)

        # Filter the form by the date range.
        df_form_by_date = helpers.filter_form_data_by_time(df_form, dates[0], dates[1])

        # Run the algorithm on the filtered dataset.
        df_results = run_algorithm(df_form_by_date, questions, dates[0])

        # Group the results by median outlier score.
        df_results = df_results.groupby(['user', 'date'], as_index=False)['outlier_score'].median()

        # Sort by median outlier score.
        df_results = df_results.sort_values(by=['outlier_score'], ascending=False)
    
        # Use the index to create a rank for each user.
        df_results['rank'] = df_results.index

        # Add the results to the full output dataset.
        df_historical = df_historical.append(df_results)

    df_historical['date'] = pd.to_datetime(df_historical['date'])
    
    # If you want to plot each user:
    #df_historical.pivot_table(index='date', columns='user', values='score_label')
    #.plot(legend=False)
    #plt.savefig('users.png')

    return df_historical

def compute_correlations(df_form, df_results):
    """Runs the MMA algorithm on the given forms.

    Args:
        df_form: the dataframe of the form the algorithm ran on.
        df_results: the formatted output the algorithm returned.

    Returns:
        a dataframe of users with their average scores and other factors to correlate scores with.
    """

    # Group users by their median score.
    df_users = pd.DataFrame(df_results.groupby(['user'], as_index=True)['outlier_score'].median())

    # Create a dwell time column and group users by it.
    df_form['dwell_time'] = (df_form['completed_time'] - df_form['started_time']).dt.total_seconds()
    df_dwell_time = pd.DataFrame(df_form.groupby(['username'], as_index=True)['dwell_time'].median())

    # Merge the results together.
    df_users = df_users.merge(df_dwell_time, left_index=True, right_index=True, how='inner')

    # To add a correlation for a form property, use this:
    form_property = ''
    # df_property= pd.DataFrame(df_form.groupby(['username', 'form_property']).size().unstack(fill_value=0))  
    # df_users = df_users.merge(df_property, left_index=True, right_index=True, how='inner')

    return df_users

# %%
def main():

    for form in settings.FORMS:
        print("Form: ", form)

        df_form = helpers.read_commcare_form(settings.PROJECT_PATH, form, settings.POSTGRES_USERNAME, settings.POSTGRES_PASSWORD, settings.POSTGRES_ADDRESS, settings.POSTGRES_PORT, settings.POSTGRES_DBNAME)

        # Create a questions list without metadata and non-categorical columns.
        questions = [col for col in df_form.columns if col not in settings.COLUMNS_TO_AVOID]

        # If you already have previously run results, you can grab the list of questions from there so you don't have to annotate again.
        # questions = helpers.read_prev_results(settings.PROJECT, form)

        # Clean and hash the dataframe.
        df_form_cleaned = helpers.clean_form(df_form, settings.FORM_USER_ID, questions)

        # For historical trend analysis:
        #df_historical = find_historical_outliers(df_form, questions)

        # For a normal run:
        df_results = run_algorithm(df_form_cleaned, questions)

        # Add a column for average dwell time:
        df_correlations = compute_correlations(df_form, df_results)
    
        # Save the results.
        df_correlations.to_csv('data/results/' + form + '.csv', index=False)

# %%
if __name__ == "__main__":
    main()
