"""
generate_supervisor_card.py

Created by Faisal M. Lalani.
flalani@dimagi.com

Generates csv files with sampled health workers for uploading to CommCare HQ as lookup tables.
"""

import helpers
import pandas as pd
import numpy as np

def format_for_commcare(df, n):
    """Format the dataframe to be as easy as possible to upload as a lookup to CommCare.
    # TODO: add index sheet!

    Args:
        df: the dataframe to format.
        n: the number of rows to sample from the dataframe.
    """

    sample = df.sample(n = n)
    sample.index = np.arange(1, len(sample) + 1)
    df.columns = ['field: ' + str(col) for col in df.columns] # CommCare requires the word "field: " before every header.
    return df

def main():
    # Read in the results from the algorithm.
    # Can be generated using run_outlier_detect.py.
    df_results = pd.read_csv('results.csv')

    # Containers to hold results:
    outputs = []
    groupby_users = df_results.groupby('user')

    # Loop through each set of results by user.
    for user_id, df_user in groupby_users:
        score_labels = []
        output = {'rank': user_id}
        
        for i, (index, row) in enumerate(df_user.iterrows()):

            # Narrow down the user's top 3 highest scored questions.   
            num_questions = 3 

            if row['score_label'] and i < num_questions:
                
                score_labels.append(row['score_label'])
                
                # Find the biggest gap between values.
                differences = {x: abs(row['user_distribution_normalized'][x] - row['total_distribution_normalized'][x]) for x in row['user_distribution_normalized'] if x in row['total_distribution_normalized']}
                largest_difference_key = max(differences, key= lambda x: differences[x])

                # Create a sentence for the question and score based on what the largest difference key is.
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

    df_final = pd.DataFrame(outputs)
    df_final = helpers.format_for_commcare(df_final)

if __name__ == "__main__":
    main()
