import psycopg2
from enum import Enum

CONNECTION = {
    "host": "containers-us-west-100.railway.app",
    "port": "7529",
    "database": "railway",
    "user": "postgres",
    "password": "O4MfUYqXnTJJWSqfJy3I"
}


def open_connection(func):
    def wrapper(*args, **kwargs):
        try:
            conn = psycopg2.connect(**CONNECTION)
            return_value = func(*args, conn=conn, **kwargs)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error opening connection: {error}")
        finally:
            conn.close()

        return return_value
    return wrapper


@open_connection
def execute_select(query, conn=None):
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing select: {error}")

    finally:
        cursor.close()


@open_connection
def execute_command(query, conn=None):
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing command: {error}")

    finally:
        cursor.close()


class DbTable(Enum):
    twitch_user_thumbnails = "twitch_user_thumbnails",
    youtube_channels = "youtube_channels",


def values_to_string(values):
    values = ', '.join([f"'{value}'" for value in values])
    return f"({values})"


def insert_values(table, values):
    command = ""
    for value in values:
        command += f"INSERT INTO {table.value[0]} VALUES {values_to_string(value)};"

    execute_command(command)


def select_all(table):
    return execute_select(f"SELECT * FROM {table.value[0]};")


def get_twitch_user_thumbnails_by_ids(user_ids):
    return execute_select(f"SELECT * FROM {DbTable.twitch_user_thumbnails.value[0]} WHERE user_id in {values_to_string(user_ids)};")


def insert_twitch_user_thumbnails(values):
    insert_values(DbTable.twitch_user_thumbnails, values)


def insert_youtube_channels(values):
    insert_values(DbTable.youtube_channels, values)


def get_twitch_user_thumbnails():
    return select_all(DbTable.twitch_user_thumbnails)


def get_youtube_channels():
    return select_all(DbTable.youtube_channels)
