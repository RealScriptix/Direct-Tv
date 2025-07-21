from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import asyncio
from enum import Enum
import pytz
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ProgramType(str, Enum):
    NEWS = "news"
    SPORTS = "sports"
    MOVIE = "movie"
    SERIES = "series"
    DOCUMENTARY = "documentary"
    ENTERTAINMENT = "entertainment"
    MUSIC = "music"
    KIDS = "kids"

class Region(str, Enum):
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA = "asia"
    OCEANIA = "oceania"
    AFRICA = "africa"
    SOUTH_AMERICA = "south_america"

# Models
class Channel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_number: int
    name: str
    region: Region
    logo_url: Optional[str] = None
    description: str
    language: str
    timezone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Program(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: ProgramType
    duration_minutes: int
    rating: Optional[str] = "PG"
    genre: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    release_year: Optional[int] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Schedule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_id: str
    program_id: str
    start_time: datetime
    end_time: datetime
    timezone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CurrentShow(BaseModel):
    channel: Channel
    current_program: Optional[Program] = None
    next_program: Optional[Program] = None
    current_start_time: Optional[datetime] = None
    current_end_time: Optional[datetime] = None
    next_start_time: Optional[datetime] = None
    progress_percentage: float = 0.0
    time_remaining_minutes: int = 0

# Channel Create Models
class ChannelCreate(BaseModel):
    channel_number: int
    name: str
    region: Region
    description: str
    language: str
    timezone: str
    logo_url: Optional[str] = None

class ProgramCreate(BaseModel):
    title: str
    description: str
    type: ProgramType
    duration_minutes: int
    rating: Optional[str] = "PG"
    genre: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    release_year: Optional[int] = None
    thumbnail_url: Optional[str] = None

class ScheduleCreate(BaseModel):
    channel_id: str
    program_id: str
    start_time: datetime
    timezone: str

# Initialize sample data
async def init_sample_data():
    # Check if data already exists
    existing_channels = await db.channels.count_documents({})
    if existing_channels > 0:
        return
    
    # Sample channels for different regions
    sample_channels = [
        # North America
        {"channel_number": 1, "name": "Global News Network", "region": "north_america", "description": "24/7 Breaking News", "language": "English", "timezone": "America/New_York"},
        {"channel_number": 2, "name": "Sports Central", "region": "north_america", "description": "Live Sports Coverage", "language": "English", "timezone": "America/New_York"},
        {"channel_number": 3, "name": "Movie Palace", "region": "north_america", "description": "Classic and Modern Movies", "language": "English", "timezone": "America/New_York"},
        
        # Europe
        {"channel_number": 101, "name": "Euro News 24", "region": "europe", "description": "European News Channel", "language": "English", "timezone": "Europe/London"},
        {"channel_number": 102, "name": "Continental Sports", "region": "europe", "description": "European Sports Network", "language": "English", "timezone": "Europe/London"},
        {"channel_number": 103, "name": "EuroFix Cinema", "region": "europe", "description": "European Film Channel", "language": "English", "timezone": "Europe/London"},
        
        # Asia
        {"channel_number": 201, "name": "Asia Today", "region": "asia", "description": "Asian News and Current Affairs", "language": "English", "timezone": "Asia/Tokyo"},
        {"channel_number": 202, "name": "Asia Sports Network", "region": "asia", "description": "Asian Sports Coverage", "language": "English", "timezone": "Asia/Tokyo"},
        {"channel_number": 203, "name": "Asian Cinema Plus", "region": "asia", "description": "Best of Asian Cinema", "language": "English", "timezone": "Asia/Tokyo"},
        
        # Oceania
        {"channel_number": 301, "name": "Pacific News", "region": "oceania", "description": "Oceania News Network", "language": "English", "timezone": "Australia/Sydney"},
        {"channel_number": 302, "name": "Pacific Sports", "region": "oceania", "description": "Sports from Down Under", "language": "English", "timezone": "Australia/Sydney"},
        
        # Africa
        {"channel_number": 401, "name": "Africa Live", "region": "africa", "description": "African News and Culture", "language": "English", "timezone": "Africa/Johannesburg"},
        {"channel_number": 402, "name": "Safari Sports", "region": "africa", "description": "African Sports Channel", "language": "English", "timezone": "Africa/Johannesburg"},
        
        # South America
        {"channel_number": 501, "name": "Americas News", "region": "south_america", "description": "South American News", "language": "English", "timezone": "America/Sao_Paulo"},
        {"channel_number": 502, "name": "Latino Sports", "region": "south_america", "description": "Latin American Sports", "language": "English", "timezone": "America/Sao_Paulo"},
    ]
    
    # Insert channels
    channels = []
    for ch_data in sample_channels:
        channel = Channel(**ch_data)
        await db.channels.insert_one(channel.dict())
        channels.append(channel)
    
    # Sample programs
    sample_programs = [
        # News Programs
        {"title": "Morning News", "description": "Daily morning news update", "type": "news", "duration_minutes": 60},
        {"title": "Evening Report", "description": "Comprehensive evening news", "type": "news", "duration_minutes": 30},
        {"title": "Breaking News Special", "description": "Live breaking news coverage", "type": "news", "duration_minutes": 45},
        {"title": "World Update", "description": "International news roundup", "type": "news", "duration_minutes": 30},
        
        # Sports Programs
        {"title": "Sports Tonight", "description": "Daily sports highlights and analysis", "type": "sports", "duration_minutes": 60},
        {"title": "Live Match Coverage", "description": "Live sports event broadcast", "type": "sports", "duration_minutes": 120},
        {"title": "Sports Weekly", "description": "Weekly sports recap", "type": "sports", "duration_minutes": 30},
        {"title": "Championship Highlights", "description": "Best moments from recent championships", "type": "sports", "duration_minutes": 45},
        
        # Movies
        {"title": "Action Hero", "description": "Thrilling action movie", "type": "movie", "duration_minutes": 120, "genre": "Action", "release_year": 2023},
        {"title": "Romantic Comedy", "description": "Feel-good romantic comedy", "type": "movie", "duration_minutes": 95, "genre": "Comedy", "release_year": 2024},
        {"title": "Sci-Fi Adventure", "description": "Futuristic adventure film", "type": "movie", "duration_minutes": 140, "genre": "Sci-Fi", "release_year": 2024},
        {"title": "Classic Drama", "description": "Award-winning drama", "type": "movie", "duration_minutes": 110, "genre": "Drama", "release_year": 2022},
        
        # Series
        {"title": "Detective Series", "description": "Crime investigation series", "type": "series", "duration_minutes": 45, "episode_number": 1, "season_number": 1},
        {"title": "Comedy Show", "description": "Weekly comedy series", "type": "series", "duration_minutes": 30, "episode_number": 5, "season_number": 2},
        {"title": "Drama Series", "description": "Dramatic storyline series", "type": "series", "duration_minutes": 60, "episode_number": 8, "season_number": 1},
        
        # Entertainment
        {"title": "Talk Show Tonight", "description": "Celebrity interviews and entertainment", "type": "entertainment", "duration_minutes": 60},
        {"title": "Game Show Fun", "description": "Interactive game show", "type": "entertainment", "duration_minutes": 30},
        {"title": "Variety Show", "description": "Music, comedy, and entertainment", "type": "entertainment", "duration_minutes": 90},
        
        # Documentaries
        {"title": "Nature Documentary", "description": "Wildlife and nature exploration", "type": "documentary", "duration_minutes": 50},
        {"title": "History Channel Special", "description": "Historical events documentary", "type": "documentary", "duration_minutes": 60},
        {"title": "Science Explorer", "description": "Scientific discoveries and innovations", "type": "documentary", "duration_minutes": 45},
        
        # Music
        {"title": "Music Video Hour", "description": "Latest music videos", "type": "music", "duration_minutes": 60},
        {"title": "Concert Special", "description": "Live concert broadcast", "type": "music", "duration_minutes": 90},
        
        # Kids
        {"title": "Kids Adventure", "description": "Educational kids show", "type": "kids", "duration_minutes": 30},
        {"title": "Cartoon Time", "description": "Animated entertainment for children", "type": "kids", "duration_minutes": 25},
    ]
    
    # Insert programs
    programs = []
    for prog_data in sample_programs:
        program = Program(**prog_data)
        await db.programs.insert_one(program.dict())
        programs.append(program)
    
    # Generate schedules for the next 24 hours for each channel
    for channel in channels:
        current_time = datetime.utcnow()
        # Start from the current hour
        schedule_start = current_time.replace(minute=0, second=0, microsecond=0)
        
        current_slot = schedule_start
        for _ in range(48):  # 48 hours of programming
            # Pick a random program
            program = random.choice(programs)
            
            schedule = Schedule(
                channel_id=channel.id,
                program_id=program.id,
                start_time=current_slot,
                end_time=current_slot + timedelta(minutes=program.duration_minutes),
                timezone=channel.timezone
            )
            
            await db.schedules.insert_one(schedule.dict())
            current_slot = schedule.end_time

# Routes
@api_router.get("/")
async def root():
    return {"message": "Global TV Station System API"}

@api_router.post("/channels", response_model=Channel)
async def create_channel(channel_data: ChannelCreate):
    channel = Channel(**channel_data.dict())
    await db.channels.insert_one(channel.dict())
    return channel

@api_router.get("/channels", response_model=List[Channel])
async def get_channels(region: Optional[Region] = None):
    query = {}
    if region:
        query["region"] = region.value
    
    channels = await db.channels.find(query).sort("channel_number", 1).to_list(1000)
    return [Channel(**channel) for channel in channels]

@api_router.get("/channels/{channel_id}", response_model=Channel)
async def get_channel(channel_id: str):
    channel = await db.channels.find_one({"id": channel_id})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return Channel(**channel)

@api_router.post("/programs", response_model=Program)
async def create_program(program_data: ProgramCreate):
    program = Program(**program_data.dict())
    await db.programs.insert_one(program.dict())
    return program

@api_router.get("/programs", response_model=List[Program])
async def get_programs(
    type: Optional[ProgramType] = None,
    limit: int = Query(default=50, le=100)
):
    query = {}
    if type:
        query["type"] = type.value
    
    programs = await db.programs.find(query).limit(limit).to_list(limit)
    return [Program(**program) for program in programs]

@api_router.get("/live-guide")
async def get_live_guide(region: Optional[Region] = None):
    """Get current live TV guide with currently playing shows"""
    # Get channels for the region
    query = {}
    if region:
        query["region"] = region.value
    
    channels = await db.channels.find(query).sort("channel_number", 1).to_list(1000)
    current_time = datetime.utcnow()
    
    live_guide = []
    
    for channel_data in channels:
        channel = Channel(**channel_data)
        
        # Find current program
        current_schedule = await db.schedules.find_one({
            "channel_id": channel.id,
            "start_time": {"$lte": current_time},
            "end_time": {"$gt": current_time}
        })
        
        # Find next program
        next_schedule = await db.schedules.find_one({
            "channel_id": channel.id,
            "start_time": {"$gt": current_time}
        }, sort=[("start_time", 1)])
        
        current_program = None
        next_program = None
        current_start_time = None
        current_end_time = None
        next_start_time = None
        progress_percentage = 0.0
        time_remaining_minutes = 0
        
        if current_schedule:
            current_program_data = await db.programs.find_one({"id": current_schedule["program_id"]})
            if current_program_data:
                current_program = Program(**current_program_data)
                current_start_time = current_schedule["start_time"]
                current_end_time = current_schedule["end_time"]
                
                # Calculate progress
                total_duration = (current_end_time - current_start_time).total_seconds()
                elapsed_duration = (current_time - current_start_time).total_seconds()
                progress_percentage = min((elapsed_duration / total_duration) * 100, 100) if total_duration > 0 else 0
                
                # Calculate time remaining
                time_remaining_seconds = (current_end_time - current_time).total_seconds()
                time_remaining_minutes = max(int(time_remaining_seconds / 60), 0)
        
        if next_schedule:
            next_program_data = await db.programs.find_one({"id": next_schedule["program_id"]})
            if next_program_data:
                next_program = Program(**next_program_data)
                next_start_time = next_schedule["start_time"]
        
        current_show = CurrentShow(
            channel=channel,
            current_program=current_program,
            next_program=next_program,
            current_start_time=current_start_time,
            current_end_time=current_end_time,
            next_start_time=next_start_time,
            progress_percentage=progress_percentage,
            time_remaining_minutes=time_remaining_minutes
        )
        
        live_guide.append(current_show)
    
    return live_guide

@api_router.get("/schedule/{channel_id}")
async def get_channel_schedule(
    channel_id: str,
    hours: int = Query(default=24, le=168)  # Max 1 week
):
    """Get schedule for a specific channel"""
    current_time = datetime.utcnow()
    end_time = current_time + timedelta(hours=hours)
    
    schedules = await db.schedules.find({
        "channel_id": channel_id,
        "start_time": {"$gte": current_time, "$lt": end_time}
    }).sort("start_time", 1).to_list(1000)
    
    schedule_with_programs = []
    for schedule_data in schedules:
        program_data = await db.programs.find_one({"id": schedule_data["program_id"]})
        if program_data:
            # Remove MongoDB _id field to avoid serialization issues
            schedule_clean = {k: v for k, v in schedule_data.items() if k != '_id'}
            program_clean = {k: v for k, v in program_data.items() if k != '_id'}
            
            schedule_with_programs.append({
                **schedule_clean,
                "program": Program(**program_clean)
            })
    
    return schedule_with_programs

@api_router.get("/regions")
async def get_regions():
    """Get all available regions with channel counts"""
    pipeline = [
        {"$group": {"_id": "$region", "channel_count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.channels.aggregate(pipeline).to_list(1000)
    
    regions = []
    for result in results:
        regions.append({
            "region": result["_id"],
            "channel_count": result["channel_count"]
        })
    
    return regions

@api_router.post("/init-data")
async def initialize_sample_data():
    """Initialize the system with sample data"""
    await init_sample_data()
    return {"message": "Sample data initialized successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize sample data on startup"""
    await init_sample_data()
    logger.info("Global TV Station System started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()