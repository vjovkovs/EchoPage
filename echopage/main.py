import os
from echopage.cli import parse_arguments
from echopage.logger import get_logger
from echopage.scraper import scrape_chapter
from echopage.tts import text_to_speech
from echopage.audio import combine_audio_to_m4b, zip_audio_files

logger = get_logger("EchoPage")

def main():
    args = parse_arguments()

    # Prepare directories
    output_dir = os.path.join(os.getcwd(), args.title)
    os.makedirs(output_dir, exist_ok=True)

    # Initialize variables
    current_url = args.url
    selectors = {
        'title': args.selectors[0],
        'content': args.selectors[1],
        'next': args.selectors[2]
    } if args.selectors else None
    mp3_files = []

    for i in range(args.chapters):
        try:
            logger.info(f"Scraping chapter {i + 1} from {current_url}")
            chapter = scrape_chapter(current_url, selectors)

            # Save chapter text
            chapter_file = os.path.join(output_dir, f"chapter_{i + 1}.txt")
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(chapter['content'])

            # Convert to MP3
            mp3_file = os.path.join(output_dir, f"chapter_{i + 1}.mp3")
            text_to_speech(chapter['content'], mp3_file)
            mp3_files.append(mp3_file)

            # Update URL for next chapter
            current_url = chapter['next_url']
            if not current_url:
                logger.info("No next chapter URL found. Stopping.")
                break

        except Exception as e:
            logger.error(f"Error processing chapter {i + 1}: {e}")
            break

    # Combine or zip audio files
    if mp3_files:
        try:
            m4b_file = os.path.join(output_dir, f"{args.title}.m4b")
            combine_audio_to_m4b(mp3_files, m4b_file)
            logger.info(f"M4B audiobook created at {m4b_file}")
        except Exception as e:
            logger.error(f"Error creating M4B file: {e}")

        try:
            zip_file = os.path.join(output_dir, f"{args.title}.zip")
            zip_audio_files(mp3_files, zip_file)
            logger.info(f"ZIP archive created at {zip_file}")
        except Exception as e:
            logger.error(f"Error creating ZIP file: {e}")

if __name__ == "__main__":
    main()