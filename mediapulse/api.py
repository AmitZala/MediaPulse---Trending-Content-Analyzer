# mediapulse/api.py (updated)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mediapulse.fetcher import DataFetcher
from mediapulse.processor import DataProcessor
from mediapulse.analytics import AnalyticsSummary
import pandas as pd
from typing import List, Optional

app = FastAPI(title="MediaPulse API - Enhanced")

fetcher = DataFetcher()
processor = DataProcessor()
analytics = AnalyticsSummary()

class AnalyzeRequest(BaseModel):
    keywords: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    freq: str = 'D'
    start: str = None
    end: str = None
    engagement_weighted: bool = False
    ma_window: int = 3

@app.post("/analyze_multi")
def analyze_multi(req: AnalyzeRequest):
    df = fetcher.fetch()
    df = processor.clean(df)
    filtered = processor.filter_multi(df, keywords=req.keywords, platforms=req.platforms, content_types=req.content_types, regions=req.regions, start=req.start, end=req.end)
    if filtered.empty:
        raise HTTPException(status_code=404, detail="No data for filters")
    agg = processor.aggregate(filtered, freq=req.freq, by_cols=['platform','content_type','region'], engagement_weighted=req.engagement_weighted)
    # return top keywords & stats
    keywords = sorted(filtered['keyword'].unique().tolist())
    stats = {}
    for kw in keywords:
        kw_df = agg[agg['keyword'].str.lower() == kw.lower()].sort_values('datetime')
        stats[kw] = analytics.compute_all(kw_df, ma_window=req.ma_window)
    # spikes
    spikes = analytics.spike_detection(agg)
    spikes_json = spikes.to_dict(orient='records') if not spikes.empty else []
    return {
        "filters": {
            "keywords": req.keywords, "platforms": req.platforms, "content_types": req.content_types, "regions": req.regions
        },
        "agg_preview": agg.head(50).to_dict(orient='records'),
        "stats": stats,
        "spikes": spikes_json
    }

@app.get("/region_summary/{region}")
def region_summary(region: str):
    df = fetcher.fetch()
    df = processor.clean(df)
    summary = analytics.region_top_content(df, region)
    if summary.empty:
        raise HTTPException(status_code=404, detail="No data for region")
    return {"region": region, "top_content_types": summary.to_dict(orient='records')}

