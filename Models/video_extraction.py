from ultralytics import YOLO
from Database.data_base import DataBase
import pandas as pd
import logger
import glob
import os

class PopulationTracker:
    def __init__(self, logger, database, model_path=None, model_dir=None, use_last_trained_model=False):
        self.logger = logger
        self.database = database

        if use_last_trained_model:
            model_path = model_dir
            
            list_of_files = glob.glob(os.path.join(model_dir, "*.pt"))
            if not list_of_files:
                self.logger.warning(f"No models found in {model_dir}. Using default: {model_path}")
                model_to_use = model_path
            else:
                model_to_use = max(list_of_files, key=os.path.getmtime)
                self.logger.info(f"Using latest trained model: {model_to_use}")
        else:
            model_to_use = model_path

        self.model = YOLO(model_to_use)
    
    def run_analysis(self):
        self.logger.info("[Population Tracker] Starting video extraction")

        results = []
        try:
            for video_path in self.database.get_videos():
                self.logger.info(f"[Population Tracker] Processing video: {video_path}")
                result = self.model.track(
                    source=video_path, 
                    persist=True, 
                    tracker="bytetrack.yaml", 
                    show=True
                )
                results.append(result)

            videos_data = []
            for result in results:
                for frame in result:
                    if frame.boxes.id is not None:
                        ids = frame.boxes.id.int().cpu().tolist()
                        classes = frame.boxes.cls.int().cpu().tolist()
                        confidences = frame.boxes.conf.cpu().tolist()

                    for obj_id, obj_cls, conf in zip(ids, classes, confidences):
                        videos_data.append({
                            "timestamp": pd.Timestamp.now(),
                            "video": video_path,
                            "object_id": obj_id,
                            "species": self.model.names[obj_cls],
                            "confidence": conf
                        })

            self.logger.info(f"[Population Tracker] Extracted data for {len(videos_data)} objects from videos")
            if len(videos_data) > 0:
                extracted_video_df = pd.DataFrame(videos_data)
                self.database.save_data_to_db(extracted_video_df, table_name="video_data")

        except Exception as e:
            self.logger.error(f"[Population Tracker] An error occurred: {e}")
        finally:
            self.logger.info("[Population Tracker] Video extraction completed")
    
    def view_video(self, video_path):
        self.logger.info(f"[Population Tracker] Viewing video: {video_path}")
        self.model.predict(source=video_path, show=True)