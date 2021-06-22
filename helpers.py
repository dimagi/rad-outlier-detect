# Helper Functions
# Dropping a lot of the uncategorizable functions that I use throughout the script here.

import hashlib
import numpy as np
import pandas as pd
from scipy import stats

def config_ipy():
    """Start the script with this.
    """
    %load_ext autoreload
    %autoreload 2

def format_scores(scores):
    """Formats the interviewer outlier scores.

    Args:
        scores: the outputted defaultdict object from the algorithm.

    Returns:
        a dataframe with relevant columns displaying outlier score, corresponding labels, and frequencies.

    """
    results = []

    for interviewer in scores.keys():
        for column in scores[interviewer].keys():
            
            score = scores[interviewer][column]['score']
            observed_frequencies = scores[interviewer][column]['observed_freq']
            expected_frequencies = scores[interviewer][column]['expected_freq']

            result = {"user": interviewer, 
                      "question": column, 
                      "outlier_score": score,
                      "user_distribution": observed_frequencies,
                      "total_distribution": expected_frequencies,
                      "user_distribution_normalized": normalize_value_counts(observed_frequencies),
                      "total_distribution_normalized": normalize_value_counts(expected_frequencies),
                      "N_user": sum(observed_frequencies.values()), 
                      "N_total": sum(expected_frequencies.values())}
            
            results.append(result)
            
    df_results = pd.DataFrame(results)
    df_results = df_results.replace([np.inf, -np.inf], np.nan)

    q = list(df_results['outlier_score'].quantile([0.00, 0.25, 0.50, 0.75, 1.00]))
    df_results['score_label'] = df_results.apply(lambda x: assign_label(x['outlier_score'], q), axis=1)

    df_results = df_results.sort_values(by=['outlier_score'], ascending=False)
    
    return df_results

def hash_string(string):
    """Return a SHA-256 hash of the given string.
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def normalize_value_counts(frequencies):
    """Format the float frequencies into nice rounded percentages.
    """
    for r in list(frequencies.keys()):
        frequencies[r] = round(100 * frequencies[r])
    return frequencies  

# 
def calc_p_value(x1, x2):
    """We need to do a chi squared test to get a p-value for the distributions.
    We have an observed distribution, but the expected
    distribution needs to be calculated based on the percentage value counts.
    """
    x1_num = [k[1] for k in x1]
    x2_num = [k[1] for k in x2]
    return stats.chisquare(x1_num, x2_num)[1]

def assign_label(x, q):
    """Assigns labels to quartiles in a dataset.

    Args:
        x: the list the labels should correspond to.
        q: the boundaries to use to break up the list.
    """
    if x <= q[1]:
        return 'Not Surprising'
    elif x <= q[2]:
        return 'Little Surprising'
    elif x <= q[3]:
        return 'Surprising'
    elif x <= q[4]:
        return 'Very Surprising'
    
def format_for_commcare(df, n):
    """Format the dataframe to be as easy as possible to upload as a lookup to CommCare.
    # TODO: add index sheet!
    """

    sample = df.sample(n = n)
    sample.index = np.arange(1, len(sample) + 1)
    df.columns = ['field: ' + str(col) for col in df.columns]
    return df