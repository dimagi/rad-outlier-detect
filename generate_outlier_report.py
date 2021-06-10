"""
generate_outlier_report.py

Created by Faisal M. Lalani.
flalani@dimagi.com

Runs Ben Birnbaum's outlier detection algorithm on a CommCare form submission dataset, formats it with frequency data, and generates csv files with sampled health workers for uploading to CommCare HQ as lookup tables.
"""

# %% [markdown]
# # Generate Outlier Report
# ### Faisal M. Lalani
# ---

# %%
%load_ext autoreload
%autoreload 2

# %% [markdown]
# ## Imports
import helpers
import pandas as pd
import outlier_detect
from simple_settings import settings

# %% [markdown]
# ## CommCare Data
# Load in a form from a CommCare project and pre-process it for a smooth run through the algorithm.
df_form = pd.read_parquet(FORM_PATH)

# We'll also need the form summary to grab question/answer display text.
df_form_summary = pd.read_csv(FORM_SUMMARY_PATH)
# Remove the full path and only show questions in the question_id paths.
df_form_summary['question_id'] = df_form_summary['question_id'].str.split('/').apply(lambda x: x[-1])

# Load in the dataset of annotations created by Hailey that assign a "compelling score" to each question.
df_annotations = pd.read_csv(FORM_ANNOTATIONS_PATH)
# Filter only the questions that have a score above 1.
df_interesting_annotations = df_annotations.loc[df_annotations["hb outlier score"] > 1]

questions = list(df_interesting_annotations.loc[df_interesting_annotations["form_name"] == FORM]["question_id"])
user_id = 'username'

# Hash the usernames for privacy reasons.
columns_to_copy = [user_id] + questions
df_form_cleaned = df_form[columns_to_copy].copy()
df_form_cleaned[user_id] = df_form_cleaned[user_id].apply(helpers.hash_string)

# Replace Nones with a value that can be subscriptable.
df_form_cleaned = df_form_cleaned.fillna(value='missing')
df_form_cleaned.head()

# %% [markdown]
# Run the MMA algorithm on the CommCare data.
(mma_scores, agg_col_to_data) = outlier_detect.run_mma(df_form_cleaned, user_id, questions)
df_results = helpers.format_scores(mma_scores)
df_results.head()

# %% [markdown]
## Generating Reports
outputs = []
groupby_users = df_results.groupby('user')
user_num = 1

for user_id, df_user in groupby_users:
    
    health_worker = 'Health Worker ['
    full_statement = health_worker
    output = {'rank': user_num}
    
    for i, (index, row) in enumerate(df_user.iterrows()):
                
        num_questions = 3
                
        if row['score_label'] and i < num_questions:
            
            health_worker += row['score_label']
        
            # Use the form summary to grab the question's display text.
            question_display_text = list(df_form_summary.loc[df_form_summary['question_id'] == row['question']]['label'])[0]
            
            # Find the biggest gap between values.
            differences = {x: abs(row['user_distribution_normalized'][x] - row['total_distribution_normalized'][x]) for x in row['user_distribution_normalized'] if x in row['total_distribution_normalized']}
            largest_difference_key = max(differences, key= lambda x: differences[x])

            if largest_difference_key == 'missing':
                hw_answer = "Did not respond " 
                others_answer = "Other HWs did not respond "
            else:
                hw_answer = "Responded by answering '" + largest_difference_key + "' " 
                others_answer = "Other HWs responded by answering '" + largest_difference_key + "' "
                
            hw_percent = '**' + str(row['user_distribution_normalized'][largest_difference_key]) + '%** of the time.'
            others_percent = '**' + str(row['total_distribution_normalized'][largest_difference_key]) + '%** of the time.'
            hw_answer += hw_percent
            others_answer += others_percent
            
            # Add proper grammar for readability.
            if i != num_questions - 1:
                health_worker += ', '
                
            output['question_' + str(i+1)] = question_display_text
            output['algorithm_label_' + str(i+1)] = '**' + row['score_label'] + '**'

            answer_index = '_answer_' + str(i+1)
            output['hw' + answer_index] = hw_answer
            output['others' + answer_index] = others_answer
    
    health_worker += ']'
    output['health_worker'] = health_worker
    outputs.append(output)
    user_num += 1

# %%
df_final = pd.DataFrame(outputs)
df_final = helpers.get_sample(df_final, 10)
df_final = helpers.format_for_commcare(df_final)
df_final.head()
# %%
