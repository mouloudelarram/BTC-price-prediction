from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Post(BaseModel):
    """Unified data model for social media posts across all platforms"""
    
    platform: str = Field(..., description="Platform source: 'twitter', 'reddit', 'farcaster', 'lens'")
    content: str = Field(..., description="Post/tweet/comment body text")
    author: str = Field(..., description="Username or author handle")
    timestamp: datetime = Field(..., description="Post creation time")
    engagement: Dict[str, int] = Field(default_factory=dict, description="Likes, retweets, scores, etc.")
    url: str = Field(..., description="Direct link to the post")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return self.dict()
