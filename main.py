from Database.data_base import DataBase
from Models.video_extraction import PopulationTracker
from Database.video_utils import download_videos, get_videos
from utils import get_logger

VIDEO_SEARCH = 'Closed jar ecossystem'
MODEL_PATH = "yolo11n.pt"
MODELS_DIR = "Models/Trained"
DB_FILE = 'DataBase/Data/database.db'
VIDEO_DIR = 'DataBase/Data/Videos/'
SCENES_DIR = 'DataBase/Data/Scenes/'

def main(download=False, process_videos=True):
    logger = get_logger()
    
    if download:
        logger.info("[Main] Downloading videos")
        download_videos(logger, VIDEO_SEARCH, VIDEO_DIR)
    
    logger.info("[Main] Creating video scenes")
    videos = get_videos(logger, VIDEO_DIR, SCENES_DIR)

    if not process_videos:
        return 

    logger.info("[Main] Initializing database")
    database = DataBase(logger, videos, db_file=DB_FILE)

    logger.info("[Main] Starting population tracking")
    tracker = PopulationTracker(logger, database, model_path=MODEL_PATH, model_dir=MODELS_DIR)

    tracker.run_analysis()

if __name__ == "__main__":
    main(True, False)