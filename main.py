import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from TTS.api import TTS
from moviepy.editor import *

# File path
base_path = 'C:/Users/ryanq/Documents/autoTube'

# Web scraping function with URL validation and correction
def scrape_images(url, folder):
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

    os.chdir(folder)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    images = soup.find_all('img')
    for idx, image in enumerate(images):
        # Check if the 'src' attribute exists in the image tag
        if 'src' in image.attrs:
            link = image['src']
            # Check if the URL is valid and complete
            if not urlparse(link).scheme:
                # If the URL is relative, make it absolute by joining it with the base URL
                link = urljoin(url, link)
            with open(f'image_{idx}.jpg', 'wb') as f:
                im = requests.get(link)
                f.write(im.content)
                print(f'Writing image_{idx}.jpg')
        else:
            print(f"Image {idx} does not have a 'src' attribute.")

# Text to Speech function
def text_to_speech(text, output_path):
    tts = TTS(model_name="tts_models/en/vctk/vits")
    tts.tts_to_file(
        text=text,
        speaker=tts.speakers[63],
        file_path=output_path
    )

# Scrape images
website_url = 'https://time.com/6315607/bryan-johnsons-quest-for-immortality/'  # Replace with the website URL you want to scrape
image_folder = os.path.join(base_path, 'images')  # Construct the image folder path
scrape_images(website_url, image_folder)

# Generate text-to-speech audio
script = '''
In Venice, California, tech entrepreneur Bryan Johnson is on an audacious mission to conquer death using his Blueprint life-extension 
system, an extravagant regimen involving 111 daily pills, unique devices, and data-driven health management. Johnson believes that 
death is optional, never to be embraced. While other wealthy individuals like Jeff Bezos and Peter Thiel invest in anti-aging ventures,
Johnson stands out by relinquishing his body's control to a meticulously designed algorithm. His journey, accompanied by his devoted 
assistant Kate Tolo, blurs the boundaries between dedication and fanaticism. As Johnson envisions a future where algorithms govern our 
bodies, this story raises profound questions about the essence of humanity and the value of life's unpredictability and desires.
'''
audio_output = os.path.join(base_path, 'output_audio.wav')  # Construct the audio output path
text_to_speech(script, audio_output)

# Create video from images and audio
clips = []
image_files = os.listdir(image_folder)
image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.png', '.jpeg'))]  # Filter only image files
image_files.sort()

# Skip the first 4 images, ONLY NEEDED THIS FOR EXAMPLE DUE TO THIS SPECIFIC WEBSITE'S FORMATTING
image_files = image_files[4:]

for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    image_duration = 6  # Adjust the duration as needed
    clip = ImageClip(image_path).set_duration(image_duration)
    clips.append(clip)

video_clip = concatenate_videoclips(clips, method='compose')
video_clip = video_clip.set_audio(AudioFileClip(audio_output))
output_video_path = os.path.join(base_path, 'output_video.mp4')  # Construct the output video path
video_clip.write_videofile(output_video_path, fps=24, remove_temp=True, codec="libx264", audio_codec="aac")