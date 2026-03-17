from scenedetect import detect, ContentDetector, split_video_ffmpeg
import imageio_ffmpeg as iio_ffmpeg
from pytubefix.contrib.search import Search, Filter
import glob
import os
import re

def sanitize_filename(name, max_len=200):
    safe = re.sub(r'[\\/*?:"<>|]', '_', name)
    safe = safe.replace(' ', '_')
    return safe[:max_len].strip()

def download_videos(logger, search_query, output_dir, max_results=10):
    logger.info(f"[Video] Downloading videos for search query: '{search_query}' into directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    filters = (
        Filter.create()
        .type(Filter.Type.VIDEO)
        .feature([Filter.Features.CREATIVE_COMMONS])
        .sort_by(Filter.SortBy.VIEW_COUNT)
    )

    search = Search(search_query, filters=filters)
    results = search.results[:max_results]

    if not results:
        logger.warning(f"[Video] No videos found for search query: '{search_query}'")
        return

    for video in results:
        try:
            stream = video.streams.filter(file_extension='mp4').first()
            if stream:
                video_title = sanitize_filename(video.title)

                if video_title in glob.glob(os.path.join(output_dir, "*.mp4")):
                    logger.info(f"[Video] Skipping download for '{video.title}': already exists in {output_dir}")
                    continue

                stream.download(output_path=output_dir, filename=video_title + ".mp4")
                logger.info(f"[Video] Downloaded video: {video.title} to {output_dir}")
            else:
                logger.warning(f"[Video] No mp4 stream found for video: {video.title}")
        except Exception as e:
            logger.error(f"[Video] Error downloading video '{video.title}': {e}")

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

    # ensure scenedetect finds an ffmpeg binary by prepending imageio-ffmpeg's exe dir to PATH
    ffmpeg_exe = iio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + old_path
    
    for video_path in video_paths:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        out_dir = os.path.join(scenes_dir, base_name)

        if os.path.isdir(out_dir):
            existing = glob.glob(os.path.join(out_dir, "*.mp4"))
            if existing:
                logger.info(f"[Video] Skipping {video_path}: scenes already exist in {out_dir} ({len(existing)} files)")
                continue

        logger.info(f"[Video] Processing video: {video_path}")
        scene_list = []
        try:
            scene_list = detect(video_path, ContentDetector())
            logger.info(f"[Video] Scenes detected for {video_path}: {len(scene_list)}")
        except Exception as e:
            logger.error(f"[Video] Error processing video {video_path}: {e}")

        os.makedirs(out_dir, exist_ok=True)
    
        split_video_ffmpeg(video_path, scene_list, output_dir=out_dir)
