from simple_settings import settings
from os import error
import sys
import outlierdetect
import numpy as np
import pyarrow
import pandas as pd
import sqlalchemy

def generate_df_from_sql_query(table, cnx):
    """Returns a dataframe from specified SQL table.

    Args:
        table: the form to parse.
        test: boolean that indicates limiting the number of rows.
        cnx: the connection to the SQL db.


    Returns:
        a dataframe containing the specified number of submissions for the given form.

    """
    sql_query = ('SELECT * FROM "outlier_detect"."{table}"'.format(
        table=table))
    df = pd.read_sql_query(sql_query, con=cnx)

    return df

if __name__ == '__main__':
    
    cnx = sqlalchemy.create_engine(f'postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_ADDRESS}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DBNAME}')

    # Specify a start and end date to filter form data by time.
    #start_date = ''
    #date = '2020-07-01'

    for form in settings.FORMS[:1]:

        print("FORM: ", form)

        form_data_path = 'data/forms/' + settings.DB + '/' + form + '.gzip'

        try:
            data = pd.read_parquet(form_data_path)

        except FileNotFoundError:
            # Connect using given properties.
            data = generate_df_from_sql_query(form, cnx)
            # First time calls should save output in csv to eliminate need for future calls for the same data.
            data.to_parquet(form_data_path, compression='gzip', index=False)

        print(data["case.@case_id"].head())