import psycopg
from dotenv import load_dotenv, find_dotenv
import os 

load_dotenv(find_dotenv(".env"))
connection_string = os.getenv("CONNECTION_STRING")

class SQLExecutor:
    def __init__(self,connection_string:str):

        self.connection_string=connection_string
        self.connection = None 

    def connect(self):
        self.connection = psycopg.connect(self.connection_string)
    

    def execute(self,query:str):
        try:
            with self.connection.cursor() as cursor:
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
sql_executor.connect()
query = """
SELECT DISINCT(ProductName) 
FROM products

"""
print(sql_executor.execute(query))