"""
generate_supervisor_card.py

Created by Faisal M. Lalani.
flalani@dimagi.com

Generates csv files with sampled health workers for uploading to CommCare HQ as lookup tables.
"""

# %% [markdown]
# # Generate Outlier Report
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
## Generating Reports

# %%
df_results = pd.read_csv(settings.RESULTS_PATH)
outputs = []
groupby_users = df_results.groupby('user')

for user_id, df_user in groupby_users:
    score_labels = []
    output = {'rank': user_id}
    
    for i, (index, row) in enumerate(df_user.iterrows()):    
        num_questions = 3    
        if row['score_label'] and i < num_questions:
            
            score_labels.append(row['score_label'])
            
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
                            
            output['question_' + str(i+1)] = row['question']
            output['algorithm_label_' + str(i+1)] = '**' + row['score_label'] + '**'

            answer_index = '_answer_' + str(i+1)
            output['hw' + answer_index] = hw_answer
            output['others' + answer_index] = others_answer
    
    output['health_worker'] = f"[{', '.join(score_labels)}]"
    outputs.append(output)

# %%
df_final = pd.DataFrame(outputs)
df_final = helpers.format_for_commcare(df_final)
