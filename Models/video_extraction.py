from ultralytics import YOLO
from Database.data_base import DataBase
import pandas as pd
import logger

MODEL_PATH = "yolo11n.pt"
MODELS_DIR = "Models/Trained"

class PopulationTracker:
    def __init__(self, use_last_trained_model=False):
        if use_last_trained_model:
            model_path = MODELS_DIR
            
            #TO DO find last trained model in MODELS_DIR
        else:
            self.model = YOLO(model_path)

        self.logger = logger.Logger()
        self.database = DataBase()
    
    def run_analysis(self):
        self.logger.info("[Population Tracker] Starting video extraction")

        try:
            for video_path in self.database.get_videos():
                self.logger.info(f"[Population Tracker] Processing video: {video_path}")

                results = self.model.track(
                    source=video_path, 
                    persist=True, 
                    tracker="bytetrack.yaml", 
                    show=True
                )

                for result in results:
                    if result.boxes.id is not None:
                        ids = result.boxes.id.int().cpu().tolist()
                        classes = result.boxes.cls.int().cpu().tolist()
                        confidences = result.boxes.conf.cpu().tolist()

                        for obj_id, obj_cls, conf in zip(ids, classes, confidences):
                            species = self.model.names[obj_cls]

                            extracted_video_df = pd.DataFrame({
                                "timestamp": pd.Timestamp.now(),
                                "video": video_path,
                                "object_id": obj_id,
                                "species": species,
                                "confidence": conf,
                                "box": result.boxes.xyxy.cpu().tolist()
                            }, index=[0])

                            self.database.save_data_to_db(extracted_video_df, table_name="video_data")

        except Exception as e:
            self.logger.error(f"[Population Tracker] An error occurred: {e}")
        finally:
            self.logger.info("[Population Tracker] Video extraction completed")
    
    def view_video(self, video_path):
        self.logger.info(f"[Population Tracker] Viewing video: {video_path}")
        self.model.predict(source=video_path, show=True)