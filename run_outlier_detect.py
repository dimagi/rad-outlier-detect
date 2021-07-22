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
import pandas as pd
from os import error
import outlierdetect
from simple_settings import settings

# %%
# Uncomment if running as an iPython script.
# helpers.config_ipy()

# %% [markdown]
# ## CommCare Data
# Load in a form from a CommCare project and pre-process it for a smooth run through the algorithm.

# %%
def run_algorithm(df_form, date=None):
    """Runs the MMA algorithm on the given forms.

    Args:
        form: the dataframe of the form to run the algorithm on.
        date: if not empty, formats data for historical trend analysis.
    """

    # Create a questions list without metadata and non-categorical columns.
    questions = [col for col in df_form.columns if col not in settings.COLUMNS_TO_AVOID]

    # Clean and hash the dataframe.
    df_form_cleaned = helpers.clean_form(df_form, questions)

    # Run the MMA algorithm.
    (mma_scores, _) = outlierdetect.run_mma(df_form_cleaned, settings.FORM_USER_ID, questions)

    # Format the scores for easy reading.
    df_results = helpers.format_scores(mma_scores, date)

    # Group questions by their median score.
    #df_results = df_results.groupby(['question'], as_index=False)['outlier_score'].median()

    return df_results

# %%
def find_historical_outliers(df_form):
    """Runs the MMA algorithm on the given forms, filtered by given dates.

    Args:
        df_form: the dataframe of the form to run the algorithm on.
    """

    df_historical = pd.DataFrame()

    for date in settings.BY_DATE:

        print("Date: ", date)

        df_form_by_date = helpers.filter_form_data_by_time(df_form, date)

        df_results = run_algorithm(df_form_by_date, date)

        df_results = df_results.groupby(['user', 'by_date'], as_index=False)['outlier_score'].median()

        df_historical = df_historical.append(df_results)

        return df_historical

# %%
def main():

    for form in settings.FORM:
        print("FORM: ", form)

        df_form = helpers.read_commcare_form(settings.PROJECT_PATH, form, settings.POSTGRES_USERNAME, settings.POSTGRES_PASSWORD, settings.POSTGRES_ADDRESS, settings.POSTGRES_PORT, settings.POSTGRES_DBNAME)

        df_historical = find_historical_outliers(form)
        df_results = run_algorithm(form)

if __name__ == "__main__":
    main()
