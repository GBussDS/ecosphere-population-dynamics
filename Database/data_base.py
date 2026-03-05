import sqlite3
import pandas as pd
import time
import logger
import os
import glob

DB_FILE = os.path.join('Database', 'Data', 'database.db')
VIDEO_DIR = os.path.join('Database', 'Videos')

class DataBase:
    def __init__(self):
        self.logger = logger.Logger()
        self.timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    def save_data_to_db(self, data: pd.DataFrame, table_name: str):
        os.makedirs(DB_FILE, exist_ok=True)
        self.logger.info(f"[Data Base] Saving data to database: {table_name}")

        conn = sqlite3.connect(DB_FILE)
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
        conn = sqlite3.connect(DB_FILE)
        table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
        if table_exists.fetchone():
            self.logger.info(f"[Data Base] Getting data for table: {table_name}")
        else:
            self.logger.error(f"[Data Base] Table '{table_name}' not found in database: {DB_FILE}")
            raise ValueError(f"Table '{table_name}' not found in database: {DB_FILE}")

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

    def get_videos(self):
        self.logger.info(f"[Data Base] Getting videos from directory: {VIDEO_DIR}")
        video_files = glob.glob(os.path.join(VIDEO_DIR, "*.mp4"))
        if not video_files:
            self.logger.warning(f"[Data Base] No video files found in directory: {VIDEO_DIR}")
        else:
            self.logger.info(f"[Data Base] Found {len(video_files)} video(s) in directory: {VIDEO_DIR}")
        return video_files