from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import requests
import os
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

class SearchRequest(BaseModel): 
    keyword: str 
    numSearches: int

class CommentRequest(BaseModel): 
    videoId: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
def home():
    return {"message": "YouTube Trend API"}

@app.get("/trends")
def get_trends():
    return {
        "trends": [
            "AIエージェント",
            "Claude Code",
            "自動化"
        ]
    }


@app.post("/search")
def search_youtube(request: SearchRequest):

    print("検索ワード:", request.keyword) 
    print("表示件数:", request.numSearches)

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": request.keyword,
        "type": "video",
        "maxResults": request.numSearches,
        "key": API_KEY,
    }

    search_response = requests.get(url, params=params)

    # return search_response.json()

    search_data = search_response.json()

    video_ids = [
        item["id"]["videoId"]
        for item in search_data["items"]
    ]

    print("video_ids",video_ids)


    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    videos_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": API_KEY,
    }

    videos_response = requests.get(
        videos_url,
        params=videos_params
    )

    # print(videos_response.json())

    return videos_response.json()


@app.post("/comments")
def getComments(videoId:CommentRequest):

    print(videoId)

    comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"

    comments_params = {
        "part": "snippet",
        "videoId": videoId.videoId,
        "maxResults":10,
        "textFormat": "plainText",
        "key": API_KEY,
    }

    comments_response = requests.get(
        comments_url,
        params=comments_params
    )
    
    data = comments_response.json()

    print("data",data)

    print("item",data.get("items", []))

    comments = []
    for item in data.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "textDsp": comment["textDisplay"],
            # "textOrg": comment["textOriginal"],
            "likeCount": comment["likeCount"],
        })
    print("count",len(comments))
    print("comments",comments)

    return {
        "count": len(comments),
        "comments": comments
    }