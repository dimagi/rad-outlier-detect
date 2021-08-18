"""
run_outlier_detect.py

Created by Faisal M. Lalani.
flalani@dimagi.com

Runs Ben Birnbaum's outlier detection algorithm on a CommCare form submission dataset and formats it with frequency data.
"""

import helpers
import pandas as pd
import outlier_detect
from simple_settings import settings

def run_algorithm(df_form, questions, date=None):
    """Runs the MMA algorithm on the given forms.

    Args:
        df_form: the dataframe of the form to run the algorithm on.
        questions: the list of questions to use for the algorithm.
        date: if not empty, formats data for historical trend analysis.

    Returns:
        formatted output of the algorithm.
    """

    # Run the MMA algorithm.
    (mma_scores, _) = outlier_detect.run_mma(df_form, settings.FORM_USER_ID, questions, null_responses=settings.AVOID_RESPONSES)

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
        df_results = df_results.reset_index(drop=True)
    
        # Use the index to create a rank for each user.
        df_results['rank'] = df_results.index

        # Add the results to the full output dataset.
        df_historical = df_historical.append(df_results)

    # Convert date column to datetime format.
    df_historical['date'] = pd.to_datetime(df_historical['date'])

    return df_historical


def main():

    for form in settings.FORMS:
        print("Form: ", form)

        df_form = helpers.read_commcare_form(settings.PROJECT_PATH, form, settings.POSTGRES_USERNAME, settings.POSTGRES_PASSWORD, settings.POSTGRES_ADDRESS, settings.POSTGRES_PORT, settings.POSTGRES_DBNAME)

        # Create a questions list without metadata and non-categorical columns.
        questions = [col for col in df_form.columns if len(df_form[col].value_counts()) <= settings.ANSWER_LIMIT]

        # Clean and hash the dataframe.
        df_form_cleaned = helpers.clean_form(df_form, settings.FORM_USER_ID, questions)

        # For a normal run:
        df_results = run_algorithm(df_form_cleaned, questions)

        # For historical trend analysis:
        #df_historical = find_historical_outliers(df_form, questions)

        df_results.to_csv('results.csv')

if __name__ == "__main__":
    main()
