from pydantic import BaseModel


class PostTweet(BaseModel):
    content: str
