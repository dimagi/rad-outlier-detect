#!/usr/bin/env python
# encoding: utf-8
"""
analyze_results.py

Created by Faisal M. Lalani on March 2021.
flalani@dimagi.com

Used to connect to a SQL database.
"""

from simple_settings import settings
import sqlalchemy

def connect_to_sql():
    """Handles the necessary functionality to connect to SQL.

    Args:
        address: postgres address.
        port: postgres address.
        username: postgres address.
        password: postgres address.
        dbname: postgres address.

    Returns:
        the connection engine to read SQL queries.

    """
    username = settings.POSTGRES_USERNAME
    password = settings.POSTGRES_PASSWORD
    ipaddress = settings.POSTGRES_ADDRESS
    port = settings.POSTGRES_PORT
    dbname = settings.POSTGRES_DBNAME
    
    postgres_url = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(username=username,
                    password=password, ipaddress=ipaddress, port=port, dbname=dbname))
    cnx = sqlalchemy.create_engine(postgres_url)

    return cnx