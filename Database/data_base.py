import sqlite3
import pandas as pd
import time
import logger
import os
import glob

class DataBase:
    def __init__(self, logger, videos, db_file):
        self.logger = logger
        self.timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.videos = videos
        self.db_file = db_file

    def save_data_to_db(self, data: pd.DataFrame, table_name: str):
        self.logger.info(f"[Data Base] Saving data to database: {table_name}")

        conn = sqlite3.connect(self.db_file)
        try:
            table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
            if table_exists.fetchone():
                data.to_sql(table_name, conn, if_exists='append', index=False)
            else:
                self.logger.info(f"[Data Base] Table '{table_name}' does not exist. It will be created.")
                data.to_sql(table_name, conn, if_exists='fail', index=False)

        except Exception as e:
            self.logger.error(f"[Data Base] Error saving data to database: {e}")
        finally:
            conn.close()
    
    def get_data(self, table_name, query=None) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_file)
        table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
        if table_exists.fetchone():
            self.logger.info(f"[Data Base] Getting data for table: {table_name}")
        else:
            self.logger.error(f"[Data Base] Table '{table_name}' not found in database: {self.db_file}")
            raise ValueError(f"Table '{table_name}' not found in database: {self.db_file}")

        if query:
            self.logger.info(f"[Data Base] Executing custom query: {query}")
            try:
                data = pd.read_sql_query(query, conn)
                self.logger.info(f"[Data Base] Custom query executed successfully")
                return data
            except Exception as e:
                self.logger.error(f"[Data Base] Error executing custom query: {e}")
                raise
            finally:
                conn.close()

        query = f"""
            SELECT * FROM {table_name}
            QUALIFY ROW_NUMBER() OVER (PARTITION BY video ORDER BY timestamp DESC) = 1
        """
        try:
            data = pd.read_sql_query(query, conn)
            self.logger.info(f"[Data Base] Latest data retrieved successfully for table: {table_name}")
        except Exception as e:
            self.logger.error(f"[Data Base] Error retrieving latest data: {e}")
            raise
        finally:            
            conn.close()
        
        return data