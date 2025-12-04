# mediapulse/processor.py  (updated)
import pandas as pd
import numpy as np
from dateutil import parser
from typing import Tuple, List

class DataProcessor:
    def __init__(self, datetime_formats=None):
        self.datetime_formats = datetime_formats

    def parse_datetime(self, s):
        try:
            return parser.parse(s)
        except Exception:
            return pd.NaT

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # parse datetimes
        if 'datetime_raw' in df.columns:
            df['datetime'] = df['datetime_raw'].apply(self.parse_datetime)
            df = df.drop(columns=['datetime_raw'])
        else:
            # if datetime already present
            df['datetime'] = df['datetime'].apply(self.parse_datetime) if df['datetime'].dtype == object else pd.to_datetime(df['datetime'])
        # normalize categorical columns
        for col in ['platform', 'content_type', 'region']:
            if col not in df.columns:
                df[col] = 'unknown'
            else:
                df[col] = df[col].fillna('unknown').astype(str).str.strip()
        # engagement: prefer numeric engagement_level, fallback to engagement/likes/shares or 0
        eng_cols = [c for c in df.columns if c.lower() in ('engagement_level', 'engagement', 'likes', 'shares', 'engagement_score')]
        if eng_cols:
            df['engagement'] = pd.to_numeric(df[eng_cols[0]], errors='coerce').fillna(0)
        else:
            df['engagement'] = 0.0
        # counts
        if 'count' not in df.columns:
            df['count'] = 1
        df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
        df = df.dropna(subset=['datetime', 'keyword'])
        df['keyword'] = df['keyword'].astype(str).str.strip()
        return df

    def aggregate(self, df: pd.DataFrame, freq: str = 'D', by_cols: List[str] = None, engagement_weighted: bool = False) -> pd.DataFrame:
        """
        Aggregates with optional grouping by additional columns (platform/content_type/region)
        engagement_weighted: if True, use 'engagement' as the metric (sum) instead of 'count'
        """
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['datetime'])
        if freq == 'D':
            df['period'] = df['datetime'].dt.floor('D')
        elif freq == 'W':
            df['period'] = df['datetime'].dt.to_period('W').apply(lambda r: r.start_time)
        elif freq == 'M':
            df['period'] = df['datetime'].dt.to_period('M').apply(lambda r: r.start_time)
        else:
            df['period'] = df['datetime'].dt.floor(freq)

        metric = 'engagement' if engagement_weighted else 'count'
        group_cols = ['keyword', 'period'] + (by_cols if by_cols else [])
        # aggregate by the temporary 'period' column
        agg = df.groupby(group_cols, as_index=False)[metric].sum().rename(columns={metric: 'count', 'period': 'datetime'})
        # after renaming 'period' -> 'datetime' update the sort columns accordingly
        sort_cols = ['datetime' if c == 'period' else c for c in group_cols]
        agg = agg.sort_values(sort_cols)
        return agg

    def filter_multi(self, df: pd.DataFrame, keywords=None, platforms=None, content_types=None, regions=None, start=None, end=None):
        d = df.copy()
        if keywords:
            d = d[d['keyword'].str.lower().isin([k.lower() for k in keywords])]
        if platforms:
            d = d[d['platform'].str.lower().isin([p.lower() for p in platforms])]
        if content_types:
            d = d[d['content_type'].str.lower().isin([c.lower() for c in content_types])]
        if regions:
            d = d[d['region'].str.lower().isin([r.lower() for r in regions])]
        if start:
            d = d[d['datetime'] >= pd.to_datetime(start)]
        if end:
            d = d[d['datetime'] <= pd.to_datetime(end)]
        return d.sort_values('datetime')
