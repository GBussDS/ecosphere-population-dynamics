from Database.data_base import DataBase
from Models.video_extraction import PopulationTracker
from Database.video_utils import get_videos
import logger

MODEL_PATH = "yolo11n.pt"
MODELS_DIR = "Models/Trained"
DB_FILE = 'DataBase/Data/database.db'
VIDEO_DIR = 'DataBase/Videos/'

def main():
    logger = logger.Logger()

    logger.info("[Main] Creating video scenes")
    videos = get_videos(logger, VIDEO_DIR, "DataBase/Scenes/")

    logger.info("[Main] Initializing database")
    database = DataBase(logger, videos, db_file=DB_FILE)

    logger.info("[Main] Starting population tracking")
    tracker = PopulationTracker(logger, database, model_path=MODEL_PATH, model_dir=MODELS_DIR)

    tracker.run_analysis()