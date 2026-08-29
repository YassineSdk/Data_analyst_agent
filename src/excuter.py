import psycopg
from dotenv import load_dotenv, find_dotenv
import os 

load_dotenv(find_dotenv(".env"))
connection_string = os.getenv("CONNECTION_STRING")

class SQLExecutor:
    def __init__(self,connection_string:str):

        self.connection_string=connection_string

    def execute(self,query:str):
        try:
            with psycopg.connect(self.connection_string) as connection:

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc.name for desc in cursor.description]
                    rows = cursor.fetchall()

            return {
                "success":True,
                "columns":columns,
                "result":rows,
                "error": None
            }
        except Exception as e :
            return {
                "success": False,
                "columns": None,
                "result": None,
                "error": str(e)
            }

sql_executor = SQLExecutor(connection_string)
# query = """
# SELECT SUM(revenue) as total_revenue 
# FROM sales 

# """
# print(sql_executor.execute(query))