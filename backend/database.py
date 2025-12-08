from db_connection import mongo_client


database = mongo_client.subjects


def mongo_database():
    return database