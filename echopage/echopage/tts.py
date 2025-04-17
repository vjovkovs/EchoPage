import os
import asyncio
from time import sleep
from pathlib import Path
from dotenv import load_dotenv
from edge_tts import Communicate

from echopage.logger import setup_logger

# Load .env variables
load_dotenv()
logger = setup_logger()

# TTS settings (override in .env if desired)
VOICE = os.getenv("TTS_VOICE", "en-GB-SoniaNeural")
RATE  = os.getenv("TTS_RATE", "1.0")
VOLUME = os.getenv("TTS_VOLUME", "0%")

async def _synthesize(text: str, output_path: str):
    """Asynchronous helper to run edge-tts synthesis."""
    communicate = Communicate(text, voice=VOICE, rate=RATE, volume=VOLUME)
    await communicate.save(output_path)

def generate_audio(chapters: list, novel_title: str) -> list:
    """
    Convert each chapter text file into an MP3 using edge-tts.
    
    Args:
        chapters: List of dicts with keys 'number', 'title', 'filepath'.
        novel_title: Used to name the audio output directory.
    
    Returns:
        List of file paths to the generated .mp3 files.
    """
    audio_dir = Path("output") / novel_title.replace(" ", "_") / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    audio_files = []
    
    for chap in chapters:
        num   = chap["number"]
        title = chap["title"]
        txt_path = chap["filepath"]
        safe_name = f"{num:03d}_{title.replace(' ', '_').replace('/', '-')}.mp3"
        out_path = audio_dir / safe_name
        
        logger.info(f"Synthesizing Chapter {num}: {title}")
        
        try:
            # Read the chapter text
            text = Path(txt_path).read_text(encoding="utf-8")
            
            # Run the async TTS and save to MP3
            asyncio.run(_synthesize(text, str(out_path)))
            
            audio_files.append(str(out_path))
            logger.debug(f"Saved audio to {out_path}")
            
            # be polite to the TTS service
            sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to generate audio for chapter {num}: {e}")
            # No retries; skip to next chapter
        
    logger.info(f"Generated audio for {len(audio_files)}/{len(chapters)} chapters.")
    return audio_files

# def text_to_speech(text, output_path):
#     """
#     Converts the given text to speech and saves it as an MP3 file.

#     Args:
#         text (str): The text to convert to speech.
#         output_path (str): The file path to save the MP3 output.
#     """
#     async def _convert():
#         communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
#         await communicate.save(output_path)

#     asyncio.run(_convert())