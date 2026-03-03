import sqlite3
import pandas as pd
import time
import logger
import os
import glob

DB_FILE = os.path.join('Data', 'Files')

class DataOrchestrator:
    def __init__(self):
        self.logger = logger.Logger()

    def save_data_to_db(self, data, table_name):
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.logger.info(f"[Data Orchestrator] Saving data to database: {table_name}")

        file = os.path.join(DB_FILE, f"{table_name}_{timestamp}.db")

        conn = sqlite3.connect(file)
        data.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()

        self.logger.info(f"[Data Orchestrator] Data saved to database: {file}")
    
    def get_data(self, table_name, file_path=None) -> pd.DataFrame:
        time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if file_path:
            data = self.load_data(file_path)
        else:
            data = self.get_latest_data(table_name)
        
        return data

    def get_latest_data(self, table_name) -> pd.DataFrame:
        self.logger.info(f"[Data Orchestrator] Getting latest data for table: {table_name}")
        
        pattern = os.path.join(DB_FILE, f"{table_name}_*.db")
        candidates = glob.glob(pattern)

        if not candidates:
            self.logger.info(f"[Data Orchestrator] No database files found for table: {table_name}")
            raise FileNotFoundError(f"No saved database files for table '{table_name}' in {DB_FILE}")

        latest_file = max(candidates, key=os.path.getmtime)

        data = self.load_data(latest_file)

        return data

    def load_data(self, file_path) -> pd.DataFrame:
        self.logger.info(f"[Data Orchestrator] Loading data from: {file_path}")
        if not os.path.exists(file_path):
            self.logger.error(f"[Data Orchestrator] File not found: {file_path}")
            raise FileNotFoundError(file_path)

        conn = sqlite3.connect(file_path)
        try:
            tables_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
            if tables_df.empty:
                raise ValueError(f"No tables found in database: {file_path}")
            table = tables_df['name'].iloc[0]
            data = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
        finally:
            conn.close()

        self.logger.info(f"[Data Orchestrator] Data loaded: {file_path} (table: {table})")
        return data