import click
from echopage.echopage.drive_upload import upload_outputs
from echopage.logger import setup_logger
from echopage.scraper import scrape_chapters
from echopage.tts import generate_audio
from echopage.audio import compile_audio
from echopage.email_notifier import send_notification


logger = setup_logger()

@click.command()
@click.option('--url', prompt='Starting Chapter URL', help='The URL of the first chapter.')
@click.option('--count', prompt='Number of Chapters', type=int)
@click.option('--title', prompt='WebNovel Title', help='Used for folder and metadata.')
def run(url, count, title):
    status = "SUCCESS"
    detail = ""
    try:
        logger.info(f"Starting EchoPage: {title}, from {url}, for {count} chapters")
        chapters = scrape_chapters(url, count, title)
        audio_files = generate_audio(chapters, title)
        compile_audio(audio_files, title)
        logger.info("EchoPage process completed successfully.")
        output_path = compile_audio(audio_files, title)
        upload_outputs(title)
        logger.info("Uploaded all outputs and logs to Google Drive.")
    except Exception as e:
        status = "FAILURE"
        detail = str(e)
        logger.exception("EchoPage encountered an error.")
        logger.error(f"EchoPage process failed: {e}")
        

