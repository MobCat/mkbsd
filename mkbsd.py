# Licensed under the WTFPL License

import os
import time
import aiohttp
import asyncio
from urllib.parse import urlparse
url = 'https://storage.googleapis.com/panels-api/data/20240916/media-1a-i-p~s'

async def delay(ms):
    await asyncio.sleep(ms / 1000)

async def download_image(session, image_url, file_path):
    try:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download image: {response.status}")
            content = await response.read()
            with open(file_path, 'wb') as f:
                f.write(content)
    except Exception as e:
        print(f"Error downloading image: {str(e)}")

async def filterFilename(filename):
    # There are libs for this, but ~ is not a URL char sooo..
    charFilter = {
        "~": " ",
        "%2C": ",",
        "%5B": "[",
        "%5D": "]"
    }
    for old, new in charFilter.items():
        filename = filename.replace(old, new)
    return filename

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"⛔ Failed to fetch JSON file: {response.status}")
                json_data = await response.json()
                data = json_data.get('data')
                
                if not data:
                    raise Exception('⛔ JSON does not have a "data" property at its root.')

                download_dir = os.path.join(os.getcwd(), 'downloads')
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                    print(f"📁 Created directory: {download_dir}")

                file_index = 1
                for key, subproperty in data.items():
                    if subproperty and subproperty.get('dhd'):
                        image_url = subproperty['dhd']
                        print(f"🔍 Found image URL! {image_url.split('?')[0]}")
                        parsed_url = urlparse(image_url)

                        filename = await filterFilename(parsed_url.path.split("/")[-1])
                        artistName = parsed_url.path.split("/")[-2][2:].split("_")[0]
                        file_path = os.path.join(download_dir, artistName, filename)

                        if not os.path.exists(f"downloads/{artistName}"):
                            os.makedirs(f"downloads/{artistName}")

                        if not os.path.exists(file_path):
                            await download_image(session, image_url, file_path)
                            print(f"🖼️ Saved image to {file_path}\n")
                        else:
                            print(f"✔️ Image already downloaded {file_path}\n")

                        file_index += 1
                        await delay(250)

    except Exception as e:
        print(f"Error: {str(e)}")

def ascii_art():
    print("""
 /$$      /$$ /$$   /$$ /$$$$$$$   /$$$$$$  /$$$$$$$
| $$$    /$$$| $$  /$$/| $$__  $$ /$$__  $$| $$__  $$
| $$$$  /$$$$| $$ /$$/ | $$  \\ $$| $$  \\__/| $$  \\ $$
| $$ $$/$$ $$| $$$$$/  | $$$$$$$ |  $$$$$$ | $$  | $$
| $$  $$$| $$| $$  $$  | $$__  $$ \\____  $$| $$  | $$
| $$\\  $ | $$| $$\\  $$ | $$  \\ $$ /$$  \\ $$| $$  | $$
| $$ \\/  | $$| $$ \\  $$| $$$$$$$/|  $$$$$$/| $$$$$$$/
|__/     |__/|__/  \\__/|_______/  \\______/ |_______/""")
    print("")
    print("🤑 Starting downloads from your favorite sellout grifter's wallpaper app...")

if __name__ == "__main__":
    ascii_art()
    time.sleep(5)
    asyncio.run(main())
