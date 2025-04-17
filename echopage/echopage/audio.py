import os
from pathlib import Path
import ffmpeg
from zipfile import ZipFile

from echopage.logger import setup_logger

logger = setup_logger()

def compile_audio(audio_files: list, novel_title: str) -> str:
    """
    Merge MP3 files into one .m4b; if that fails, zip the MP3s.
    
    Args:
        audio_files: List of paths to chapter .mp3 files.
        novel_title: Used for naming the output file and folder.
    
    Returns:
        Path to the generated .m4b or .zip file.
    """
    # Prepare output paths
    safe_novel = novel_title.replace(" ", "_")
    output_dir = Path("output") / safe_novel
    output_dir.mkdir(parents=True, exist_ok=True)
    
    m4b_path = output_dir / f"{safe_novel}.m4b"
    zip_path = output_dir / f"{safe_novel}.zip"
    
    try:
        logger.info("Starting M4B compilation with ffmpeg.")
        
        # Create ffmpeg input streams
        streams = [ffmpeg.input(f) for f in audio_files]
        # Concatenate audio only (v=0, a=1)
        joined = ffmpeg.concat(*streams, v=0, a=1)
        
        # Output in ipod format, which produces .m4b
        joined = joined.output(str(m4b_path), format="ipod", acodec="aac")
        joined.run(overwrite_output=True)
        
        logger.info(f"Successfully created M4B: {m4b_path}")
        return str(m4b_path)
    
    except Exception as e:
        logger.error(f"M4B compilation failed: {e}")
        logger.info("Falling back to ZIP of individual MP3s.")
        
        # Create ZIP of MP3s
        with ZipFile(zip_path, "w") as zipf:
            for mp3 in audio_files:
                zipf.write(mp3, Path(mp3).name)
        logger.info(f"Created ZIP archive: {zip_path}")
        return str(zip_path)

# def combine_audio_to_m4b(mp3_files, output_path):
#     """
#     Combines multiple MP3 files into a single M4B audiobook file.

#     Args:
#         mp3_files (list): List of MP3 file paths to combine.
#         output_path (str): The file path to save the M4B output.
#     """
#     command = [
#         "ffmpeg",
#         "-i", f"concat:{'|'.join(mp3_files)}",
#         "-c:a", "aac",
#         "-b:a", "128k",
#         "-movflags", "+faststart",
#         output_path
#     ]
#     subprocess.run(command, check=True)

# def zip_audio_files(mp3_files, output_zip):
#     """
#     Zips multiple MP3 files into a single ZIP archive.

#     Args:
#         mp3_files (list): List of MP3 file paths to include in the ZIP.
#         output_zip (str): The file path to save the ZIP archive.
#     """
#     with zipfile.ZipFile(output_zip, 'w') as zipf:
#         for file in mp3_files:
#             zipf.write(file, os.path.basename(file))