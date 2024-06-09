import os
import aiohttp
import yt_dlp
from yt_dlp.utils import download_range_func
import google.generativeai as genai
import logging
from functools import partial
import json
import ast

from moviepy.editor import *


BASE_TWELVE_URL = "https://api.twelvelabs.io/v1.2"
TWELVE_LABS_API_KEY = os.getenv("TWELVE_LABS_API_KEY")
TWELVE_LABS_INDEX = os.getenv("TWELVE_LABS_INDEX")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def fetch_video_title(video_url: str) -> tuple:
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get("title", None)
        video_id = info_dict.get("id", None)

    return video_title, video_id


async def get_video_id_from_twelve_labs_index(file_name: str) -> str:
    url = f"{BASE_TWELVE_URL}/indexes/{TWELVE_LABS_INDEX}/videos?page=1&page_limit=10&sort_by=created_at&sort_option=desc"
    headers = {
        "accept": "application/json",
        "x-api-key": f"{TWELVE_LABS_API_KEY}",
        "Content-Type": "application/json",
    }

    logging.info("Getting video id from twelve labs index")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                try:
                    result = await response.text()
                    result_as_dict = json.loads(result).get("data")
                    video_id = next(
                        item["_id"]
                        for item in result_as_dict
                        if item["metadata"]["filename"] == file_name
                    )
                    return video_id
                except Exception as e:
                    logging.exception(e)
            else:
                logging.info(response.status)


async def generate_segment_itinerary(video_id: str) -> str:
    url = f"{BASE_TWELVE_URL}/generate"
    payload = {
        "prompt": "Given the following video, segment the videos and provide corresponding timestamps based on the different activities and places that the subject does and visits so that the segmented videos can later be used to build an itinerary.\nMake the response concise & precise.",
        "video_id": f"{video_id}",
        "temperature": 0.4,
    }
    headers = {
        "accept": "application/json",
        "x-api-key": TWELVE_LABS_API_KEY,
        "Content-Type": "application/json",
    }

    logging.info("Generating segmented itinerary")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                try:
                    result = await response.text()
                    segmented_itinerary = json.loads(result).get("data")
                    return segmented_itinerary
                except Exception as e:
                    logging.exception(e)
            else:
                logging.info(response.status)


async def parse_segment_itinerary_into_json(segment_itinerary: str) -> str:
    prompt = (
        """Parse the following text into json, with this schema: {"itinerary": List[{"segment": str, "description": str, "time_range": {"from": int, "to": int}}]}:\n\n"""
        + f"'''{segment_itinerary}'''"
    )
    model = genai.GenerativeModel(
        "gemini-1.5-flash", generation_config={"response_mime_type": "application/json"}
    )

    logging.info("Parsing segmented itinerary into json")
    response = await model.generate_content_async(prompt)

    return json.loads(response.text)


def yt_dlp_monitor(results, d):
    if d["status"] == "finished":
        results.append(d.get("info_dict").get("_filename"))


async def select_segments_of_interest(segment_json: dict, video_url: str) -> dict:
    prompt = f"""From the given list of segments, choose three segments that can be considered to be most engaging and yield high entertainment value:\n\n'''{segment_json}'''\n\nMake the response as concise and precise as possible with this schema: List[str]."""
    model = genai.GenerativeModel(
        "gemini-1.5-flash", generation_config={"response_mime_type": "application/json"}
    )

    logging.info("Selecting segments of interest and downloading the segments")
    response = await model.generate_content_async(prompt)
    response_as_list = ast.literal_eval(response.text)

    selected_segments = [
        item for item in segment_json if item["segment"] in response_as_list
    ]

    results = []
    yt_progress_hooks_partial = partial(yt_dlp_monitor, results)
    yt_opts = {
        "format": "best[ext=mp4]",
        "download_ranges": download_range_func(
            None,
            [
                (segment["time_range"].get("from"), segment["time_range"].get("to"))
                for segment in selected_segments
                if segment.get("time_range")
            ],
        ),
        "force_keyframes_at_cuts": True,
        "outtmpl": "/mock_storage/%(id)s_%(section_start)s-%(section_end)s.%(ext)s",
        "progress_hooks": [yt_progress_hooks_partial],
    }

    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        ydl.download(video_url)

    return results


def stitch_segments_into_single_video(segments: list, output_path: str) -> str:
    logging.info("Merging segments into a reel")

    video_clips = [VideoFileClip(video_file) for video_file in segments]

    final_clip = concatenate_videoclips(video_clips)
    final_clip = final_clip.resize(height=1920)
    final_clip = final_clip.crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    final_clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_bitrate="448k",
        threads=24,
        logger=None,
        preset="superfast",
        ffmpeg_params=["-crf", "18"],
    )
    final_clip.close()

    logging.info("Merge done")

    return output_path


async def generate_hashtags(text: str) -> str:
    pass
