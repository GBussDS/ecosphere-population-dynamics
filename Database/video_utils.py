from scenedetect import detect, ContentDetector, split_video_ffmpeg
import glob
import os

def get_videos(logger, video_dir, scenes_dir):
    logger.info(f"[Video] Creating scenes for videos in directory: {video_dir}")
    os.makedirs(scenes_dir, exist_ok=True)

    split_scenes(logger, video_dir, scenes_dir)

    video_files = glob.glob(os.path.join(scenes_dir, "**", "*.mp4"), recursive=True)
    if not video_files:
        logger.warning(f"[Video] No video files found in directory: {scenes_dir}")
    else:
        logger.info(f"[Video] Found {len(video_files)} video(s) in directory: {scenes_dir}")

    return video_files

def split_scenes(logger, videos_folder, scenes_dir):
    video_paths = glob.glob(os.path.join(videos_folder, "*.mp4"))
    for video_path in video_paths:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        out_dir = os.path.join(scenes_dir, base_name)
        
        if os.path.isdir(out_dir):
            existing = glob.glob(os.path.join(out_dir, "*.mp4"))
            if existing:
                logger.info(f"[Video] Skipping {video_path}: scenes already exist in {out_dir} ({len(existing)} files)")
                continue

        logger.info(f"[Video] Processing video: {video_path}")
        try:
            scene_list = detect(video_path, ContentDetector())
            logger.info(f"[Video] Scenes detected for {video_path}: {len(scene_list)}")
        except Exception as e:
            logger.error(f"[Video] Error processing video {video_path}: {e}")

        os.makedirs(out_dir, exist_ok=True)
    
        split_video_ffmpeg(video_path, scene_list, output_dir=out_dir)
