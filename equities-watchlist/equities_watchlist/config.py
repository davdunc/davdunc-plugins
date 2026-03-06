import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "")
FINVIZ_API_KEY = os.environ.get("FINVIZ_API_KEY", "")
MASSIVE_S3_ACCESS_KEY = os.environ.get("MASSIVE_S3_ACCESS_KEY", "")
MASSIVE_S3_SECRET_KEY = os.environ.get("MASSIVE_S3_SECRET_KEY", "")

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Screening thresholds
MIN_RVOL = 2.0
MIN_ATR_1MIN = 1.0
MIN_PREMARKET_VOLUME = 25_000
