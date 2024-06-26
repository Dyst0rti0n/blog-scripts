from googleapiclient.discovery import build

def get_latest_video_description(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(part='snippet', channelId=channel_id, order='date', maxResults=1)
    response = request.execute()
    
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_request = youtube.videos().list(part='snippet', id=video_id)
        video_response = video_request.execute()
        
        if video_response['items']:
            return video_response['items'][0]['snippet']['description']
    return None

def main():
    api_key = 'YOUR_YOUTUBE_API_KEY'
    channel_id = 'YOUR_YOUTUBE_CHANNEL_ID'
    
    command = get_latest_video_description(api_key, channel_id)
    if command:
        print(f"Command: {command}")

if __name__ == "__main__":
    main()
