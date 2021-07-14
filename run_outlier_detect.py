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
import outlierdetect
from simple_settings import settings

# %%
# Uncomment if running as an iPython script.
# helpers.config_ipy()

# %% [markdown]
# ## CommCare Data
# Load in a form from a CommCare project and pre-process it for a smooth run through the algorithm.

# %%
df_form = pd.read_parquet(settings.FORM_PATH)

# Hash the usernames for privacy reasons.
columns_to_copy = ['username'] + settings.QUESTIONS
df_form_cleaned = df_form[columns_to_copy].copy()
df_form_cleaned['username'] = df_form_cleaned['username'].apply(helpers.hash_string)

# Replace Nones with a value that can be subscriptable.
df_form_cleaned = df_form_cleaned.fillna(value='missing')
df_form_cleaned.head()

# %% [markdown]
# Run the MMA algorithm on the CommCare data.

# %%
(mma_scores, agg_col_to_data) = outlierdetect.run_mma(df_form_cleaned, 'username', settings.QUESTIONS)
df_results = helpers.format_scores(mma_scores)
df_results.to_csv(settings.RESULTS_PATH)