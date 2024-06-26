import feedparser
import time

def get_latest_post(feed_url):
    """
    Fetch the latest blog post from a given Medium RSS feed URL.

    Parameters:
    feed_url (str): The URL of the Medium RSS feed.

    Returns:
    str: The title of the latest blog post if available, otherwise None.
    """
    feed = feedparser.parse(feed_url)
    if feed.entries:
        return feed.entries[0].title
    return None

def main():
    # URL of the Medium RSS feed
    feed_url = 'https://medium.com/feed/@your_account'
    
    # Fetch the latest command from the blog post title
    command = get_latest_post(feed_url)
    
    if command:
        print(f"Command: {command}")
    else:
        print("No commands found.")

    # Polling interval in seconds
    polling_interval = 60
    
    # Continuously fetch commands at the specified interval
    while True:
        command = get_latest_post(feed_url)
        if command:
            print(f"Command: {command}")
        else:
            print("No new commands found.")
        time.sleep(polling_interval)

if __name__ == "__main__":
    main()
