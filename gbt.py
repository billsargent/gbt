import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote


def find_max_pages(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element with class "last"
    last_element = soup.find('li', class_='last')

    # Extract the text from the "last" element
    last_text = last_element.find('a').text.strip()

    # Convert the text to an integer to get the maximum number of pages
    max_pages = int(last_text)

    return max_pages


def get_video_links(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with class "item-wrapper"
    item_wrappers = soup.find_all('div', class_='item-wrapper')

    # Extract video links from each item wrapper
    video_links = []
    for item_wrapper in item_wrappers:
        # Find the anchor tag with class "title" within each item wrapper
        video_link = item_wrapper.find('a', class_='title')
        # Extract the href attribute, which contains the video page URL
        video_url = video_link['href']
        # Append the video URL to the list of video links
        video_links.append(video_url)

    return video_links


def download_videos(video_links, download_location):
    # Check if the download location directory exists
    if not os.path.exists(download_location):
        os.makedirs(download_location)
    elif not os.path.isdir(download_location):
        print(f"Error: '{download_location}' is not a directory.")
        return

    for video_link in video_links:
        # Extract filename from the original URL
        filename = video_link.split('/')[-1] + ".mp4"

        # Send a GET request to the video page URL
        response = requests.get(video_link)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the video element
        video_element = soup.find('video', id='play-video')

        if video_element:
            # Find the source element within the video element
            source_element = video_element.find('source')
            if source_element:
                # Extract the source URL of the video
                video_url = source_element['src']
                # Trim off everything in the URL past ".mp4"
                video_url = video_url[:video_url.index(".mp4") + 4]

                # Create the path for storing the video file
                filepath = os.path.join(download_location, filename)

                # Download the video and save it to the file
                video_response = requests.get(video_url)
                with open(filepath, 'wb') as f:
                    f.write(video_response.content)

                print(f"Downloaded: {filename}")


def main():
    parser = argparse.ArgumentParser(description="GayBoysTube Scraper")
    parser.add_argument("url", help="The URL of the GayBoysTube page to scrape")
    parser.add_argument("download_location", help="The directory where the videos will be downloaded")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to scrape (default: all)")
    args = parser.parse_args()

    url = args.url
    max_pages = args.max_pages if args.max_pages else find_max_pages(url)
    print("Maximum pages:", max_pages)
    video_links = get_video_links(url)

    # Scrape videos for the specified page range or all pages if max-pages is not provided
    for page_num in range(1, max_pages + 1):
        print(f"Scraping videos on page {page_num}/{max_pages}")
        if page_num > 1:
            url_with_page = f"{url}/page{page_num}"
            video_links += get_video_links(url_with_page)

    download_videos(video_links, args.download_location)


if __name__ == "__main__":
    main()
