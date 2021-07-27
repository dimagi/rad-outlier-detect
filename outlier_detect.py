# Pasted the required functions from Ben's algorithm here in order to debug and further understand how it all works. Also modified parts of the algorithm to return frequencies.

import collections
import itertools
import numpy as np
import pandas as pd
from scipy import stats
import sys

_FLOAT_EQ_DELTA = 0.000001  # For comparing float equality

############################################## Models ##############################################
#
# Models define the core logic for computing an outlier score for a given algorithm.  Each model
# must implement a compute_outlier_scores() method defining this logic.

class MultinomialModel:
    """Model implementing MMA.  Requries scipy module."""

    def compute_outlier_scores(self, frequencies):
        """Computes the SVA outlier scores fo the given frequencies dictionary.

        Args:
            frequencies: dictionary of dictionaries, mapping (aggregation unit) -> (value) ->
                (number of times aggregation unit reported value).

        Returns:
            dictionary mapping (aggregation unit) -> (MMA outlier score for aggregation unit).
        """
        if len(frequencies.keys()) < 2:
            raise Exception("There must be at least 2 aggregation units. " + str(frequencies.keys()))
        rng = frequencies[list(frequencies.keys())[0]].keys()
        outlier_scores = {}
        expected_frequencies = {}
        for agg_unit in list(frequencies.keys()):
            summed_freq = self._sum_frequencies(agg_unit, frequencies)
            expected_frequencies[agg_unit] = summed_freq
            if(sum(summed_freq.values()) == 0):
                outlier_scores[agg_unit] = 0
            else:
                expected_counts = _normalize_counts(
                    summed_freq,
                    val=sum([frequencies[agg_unit][r] for r in rng]))
                x2 = self._compute_x2_statistic(expected_counts, frequencies[agg_unit])
                # logsf gives the log of the survival function (1 - cdf).
                outlier_scores[agg_unit] = -stats.chi2.logsf(x2, len(rng) - 1)
        return outlier_scores, expected_frequencies


    def _compute_x2_statistic(self, expected, actual):
        """Computes the X^2 statistic for observed frequencies.
        Args:
            expected: a dictionary giving the expected frequencies, e.g.,
                {'y' : 13.2, 'n' : 17.2}
            actual: a dictionary in the same format as the expected dictionary
                (with the same range) giving the actual distribution.

        Returns:
            the X^2 statistic for the actual frequencies, given the expected frequencies.
        """
        rng = expected.keys()
        if actual.keys() != rng:
            raise Exception("Ranges of two frequencies are not equal.")
        num_observations = sum([actual[r] for r in rng])
        if abs(num_observations - sum([expected[r] for r in rng])) > _FLOAT_EQ_DELTA:
            raise Exception("Frequencies must sum to the same value.")
        return sum([(actual[r] - expected[r])**2 / max(float(expected[r]), 1.0)
            for r in rng])

    def _sum_frequencies(self, agg_unit, frequencies):
        """Sums frequencies for each aggregation unit except the given one.

        Args:
            agg_unit: the aggregation unit of concern.
            frequencies: dictionary of dictionaries, mapping (aggregation unit) -> (value) ->
                (number of times aggregation unit reported value).

        Returns:
            a dictionary mapping (value) -> (number of times all aggregation units apart from
            agg_unit reported this value)
        """
        # Get the range from the frequencies dictionary.  Assumes that the range is the same
        # for each aggregation unit in this distribution.  Bad things may happen if this is not
        # the case.
        rng = frequencies[agg_unit].keys()
        all_frequencies = {}
        for r in rng:
            all_frequencies[r] = 0
        for other_agg_unit in list(frequencies.keys()):
            if other_agg_unit == agg_unit:
                continue
            for r in rng:
                all_frequencies[r] += frequencies[other_agg_unit][r]        
        return all_frequencies

########################################## Helper functions ########################################

def _normalize_counts(counts, val=1):
    """Normalizes a dictionary of counts, such as those returned by _get_frequencies().
    Args:
        counts: a dictionary mapping value -> count.
        val: the number the counts should add up to.
    
    Returns:
        dictionary of the same form as counts, except where the counts have been normalized to sum
        to val.
    """
    n = sum(counts.values())
    frequencies = {}
    for r in list(counts.keys()):
        frequencies[r] = val * float(counts[r]) / float(n)
    return frequencies


def _get_frequencies(data, col, col_vals, agg_col, agg_unit, agg_to_data):
    """Computes a frequencies dictionary for a given column and aggregation unit.
    
    Args:
        data: numpy.recarray or pandas.DataFrame containing the data.
        col: name of column to compute frequencies for.
        col_vals: a list giving the range of possible values in the column.
        agg_col: string giving the name of the aggregation unit column for the data.
        agg_unit: string giving the aggregation unit to compute frequencies for.
        agg_to_data: a dictionary of aggregation values pointing to subsets of data
    Returns:
        A dictionary that maps (column value) -> (number of times agg_unit has column value in
        data).
    """
    interesting_data = None
    frequencies = {}
    for col_val in col_vals:
        frequencies[col_val] = 0
        # We can't just use collections.Counter() because frequencies.keys() is used to determine
        # the range of possible values in other functions.
    if isinstance(data, pd.DataFrame):
        interesting_data = agg_to_data[agg_unit][col]
        for name in interesting_data:
            if name in frequencies:
                frequencies[name] = frequencies[name] + 1
    else:  # Assumes it is an np.ndarray
        for row in itertools.ifilter(lambda row : row[agg_col] == agg_unit, data):
            if row[col] in frequencies:
                frequencies[row[col]] += 1
    return frequencies, interesting_data

def _run_alg(data, agg_col, cat_cols, model, null_responses):
    """Runs an outlier detection algorithm, taking the model to use as input.
    
    Args:
        data: numpy.recarray or pandas.DataFrame containing the data.
        agg_col: string giving the name of aggregation unit column.
        cat_cols: list of the categorical column names for which outlier values should be computed.
        model: object implementing a compute_outlier_scores() method as described in the comments
            in the models section.
        null_responses: list of strings that should be considered to be null responses, i.e.,
            responses that will not be included in the frequency counts for a column.  This can
            be useful if, for example, there are response values that mean a question has been
            skipped.
    
    Returns:
        A dictionary of dictionaries, mapping (aggregation unit) -> (column name) ->
        (outlier score).
    """
    agg_units = sorted(set(data[agg_col]), key=lambda x: (str(type(x)), x))
    outlier_scores = collections.defaultdict(dict)
    agg_to_data = {}
    agg_col_to_data = {}
    for agg_unit in agg_units:
        # TODO: could this be smarter and remove data each time? maybe no savings.
        # TODO: support numpy only again
        agg_to_data[agg_unit] = data[data[agg_col] == agg_unit]
        agg_col_to_data[agg_unit] = {}
        
    for col in cat_cols:
        col_vals = sorted(set(data[col]), key=lambda x: (str(type(x)), x))
        col_vals = [c for c in col_vals if c not in null_responses]
        frequencies = {}
        for agg_unit in agg_units:
            frequencies[agg_unit],grouped = _get_frequencies(data, col, col_vals, agg_col, agg_unit, agg_to_data)
            agg_col_to_data[agg_unit][col] = grouped
        outlier_scores_for_col, expected_frequencies_for_col = model.compute_outlier_scores(frequencies)
        for agg_unit in agg_units:
            outlier_scores[agg_unit][col] = {'score': outlier_scores_for_col[agg_unit],
                                             'observed_freq': frequencies[agg_unit],
                                             'expected_freq': expected_frequencies_for_col[agg_unit]}
    return outlier_scores, agg_col_to_data


########################################## Public functions ########################################
def run_mma(data, aggregation_column, categorical_columns, null_responses=[]):
    """Runs the MMA algorithm (requires scipy module).

    Args:
        data: numpy.recarray or pandas.DataFrame containing the data.
        aggregation_column: a string giving the name of aggregation unit column.
        categorical_columns: a list of the categorical column names for which outlier values
            should be computed.
        null_responses: list of strings that should be considered to be null responses, i.e.,
            responses that will not be included in the frequency counts for a column.  This can
            be useful if, for example, there are response values that mean a question has been
            skipped.

    Returns:
        A dictionary of dictionaries, mapping (aggregation unit) -> (column name) ->
        (mma outlier score).
    """
    return _run_alg(data,
                    aggregation_column,
                    categorical_columns,
                    MultinomialModel(),
                    null_responses)