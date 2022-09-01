import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from models import PostTweet

app = FastAPI()

"""
uvicorn main:app --reload --host 0.0.0.0 --port 50010
"""

INDEX_NAME = "twitter_like_app"


def launch_elasticsearch():
    es = Elasticsearch("es")
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)
    return es


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/init_posts")
def get():
    succeed = True
    status_code = 200
    formatted_posts = []
    try:
        es = launch_elasticsearch()
        res = es.search(index=INDEX_NAME, size=10000)
        posts = res["hits"]["hits"]
        for post in posts:
            formatted_posts.append(post["_source"])
    except Exception as e:
        logging.error(e)
        succeed = False
        status_code = 500
    finally:
        return JSONResponse(content={"succeed": succeed, "posts": formatted_posts}, status_code=status_code)


@app.get("/posts_by_scrolling/{scroll_id}")
def get_by_scrolling():
    es = launch_elasticsearch()
    res = es.search(index=INDEX_NAME)
    return JSONResponse(content={"res": res}, status_code=200)


@app.post("/post")
async def post(tweet: PostTweet):
    logging.info("post")
    logging.info(tweet)
    post_content = tweet.content
    try:
        es = launch_elasticsearch()
        es.index(index=INDEX_NAME, body={"content": post_content})
    except Exception as e:
        logging.error(e)
        return JSONResponse(content={"succeed": False}, status_code=500)
    return JSONResponse(content={"succeed": True}, status_code=201)
