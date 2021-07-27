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
import helpers
import matplotlib.pyplot as plt
import pandas as pd
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
    """

    # Clean and hash the dataframe.
    df_form_cleaned = helpers.clean_form(df_form, settings.FORM_USER_ID, questions)

    # Run the MMA algorithm.
    (mma_scores, _) = outlier_detect.run_mma(df_form_cleaned, settings.FORM_USER_ID, questions)

    # Format the scores for easy reading.
    df_results = helpers.format_scores(mma_scores, date)

    # Group questions by their median score.
    #df_results = df_results.groupby(['question'], as_index=False)['outlier_score'].median()

    return df_results

# %%
def find_historical_outliers(df_form, questions):
    """Runs the MMA algorithm on the given forms, filtered by given dates.

    Args:
        df_form: the dataframe of the form to run the algorithm on.
    """

    df_historical = pd.DataFrame()

    for dates in settings.DATES:

        date_range = dates[0] + ' - ' + dates[1]
        print(date_range)

        df_form_by_date = helpers.filter_form_data_by_time(df_form, dates[0], dates[1])

        df_results = run_algorithm(df_form_by_date, questions, dates[0])

        df_results = df_results.groupby(['user', 'date'], as_index=False)['outlier_score'].median()

        df_historical = df_historical.append(df_results)

    df_historical['date'] = pd.to_datetime(df_historical['date'])
    
    # If you want to plot each user:
    # df_historical.pivot_table(index='date', columns='user', values='outlier_score').plot(legend=False)

    return df_historical

# %%
def main():

    for form in settings.FORMS:
        print("Form: ", form)

        df_form = helpers.read_commcare_form(settings.PROJECT_PATH, form, settings.POSTGRES_USERNAME, settings.POSTGRES_PASSWORD, settings.POSTGRES_ADDRESS, settings.POSTGRES_PORT, settings.POSTGRES_DBNAME)

        # Create a questions list without metadata and non-categorical columns.
        questions = [col for col in df_form.columns if col not in settings.COLUMNS_TO_AVOID]

        # If you already have previously run results, you can grab the list of questions from there so you don't have to annotate again.
        questions = helpers.read_prev_results(settings.PROJECT, form)

        # For historical trend analysis:
        df_historical = find_historical_outliers(df_form, questions)

        # For a normal run:
        df_results = run_algorithm(df_form)

if __name__ == "__main__":
    main()
