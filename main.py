import json
import hashlib
import psycopg2
import os
import logging
import ast


LOGGER = logging.getLogger()
LOGGER.setLevel(os.environ["LOG_LEVEL"])

CHECK_IF_URL_EXISTS = \
    """
        SELECT SHORTENED_URL
        FROM SHORTENED_URLS
        WHERE ORIGINAL_URL='{input_url}';
    """

INSERT_PAIR = \
    """
       INSERT INTO SHORTENED_URLS
       (ORIGINAL_URL, SHORTENED_URL)
       VALUES ('{original_url}', '{shortened_url}'); 
    """


def connect_to_postgres_db(env_variables):
    connection = cursor = None
    LOGGER.info("Initiating DB connection")
    try:
        connection = psycopg2.connect(
            user=env_variables['username'],
            password=env_variables['password'],
            host=env_variables['host'],
            port=env_variables['port'],
            database=env_variables['database']
        )
        cursor = connection.cursor()
    except Exception as exception:
        LOGGER.info("Error occured while connecting")
        LOGGER.info(exception)
    LOGGER.info("Connected to DB successfully")
    return connection, cursor


def add_to_db(connection, cursor, input_url, shortened_url):
    try:
        LOGGER.info("Inserting new value into table...")
        cursor.execute(INSERT_PAIR.format(original_url=input_url, shortened_url=shortened_url))
        connection.commit()
        LOGGER.info("Insertion successful")
    except Exception as exception:
        LOGGER.info("Unable to insert into table. Exception raised: ")
        LOGGER.info(exception)


def close_connection(connection, cursor):
    LOGGER.info("Closing DB connection...")
    cursor.close()
    connection.close()
    LOGGER.info("Connection terminated successfully")


def check_if_present(connection, cursor, input_url):
    rows = None
    try:
        cursor.execute(CHECK_IF_URL_EXISTS.format(input_url=input_url))
    except Exception as exception:
        LOGGER.info("Error occured while executing query")
        LOGGER.info(CHECK_IF_URL_EXISTS)
        LOGGER.info(exception)
    rows = cursor.fetchall()
    if len(rows):
        return True, rows[0]
    return False, None


def get_shortened_url(input_url):
    root = 'https://lilurl.com/'
    result = hashlib.md5(input_url.encode())
    shortened_url = root + result.hexdigest()
    return shortened_url


def lambda_handler(event, context):
    env_variables = ast.literal_eval(os.environ["ENV_VARIABLES"])
    shortened_url = None
    connection, cursor = connect_to_postgres_db(env_variables)
    input_url = ast.literal_eval(event['body'])['input_url']
    LOGGER.info("Input URL=" + input_url)
    is_present, row = check_if_present(connection, cursor, input_url)
    if is_present:
        shortened_url = row[0]
    else:
        shortened_url = get_shortened_url(input_url)
        add_to_db(connection, cursor, input_url, shortened_url)
    LOGGER.info("SHORTENED URL IS: " + shortened_url)
    response = {
        'shortened_url': shortened_url
    }
    close_connection(connection, cursor)
    return response
