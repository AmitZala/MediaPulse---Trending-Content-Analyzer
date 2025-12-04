# mediapulse/fetcher.py
from pathlib import Path
import pandas as pd
from dateutil import parser

class DataFetcher:
    """
    Loads the CSV dataset from disk. Assumes dataset has at least:
      - a datetime column (name guessed from common names)
      - a keyword/topic column
      - optionally a count column (mentions) otherwise will default to 1 per row (implicit mention)
    """

    def __init__(self, csv_path: str = "D:\\MediaPulse - Trending Content Analyzer\\data\\Viral_Social_Media_Trends_with_DateTime.csv"):
        self.csv_path = Path(csv_path)

    def _guess_columns(self, df: pd.DataFrame):
        # heuristics to find datetime, keyword, count columns
        cols = [c.lower() for c in df.columns]
        dt_candidates = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
        kw_candidates = [c for c in df.columns if 'keyword' in c.lower() or 'topic' in c.lower() or 'hashtag' in c.lower()]
        count_candidates = [c for c in df.columns if 'count' in c.lower() or 'mentions' in c.lower() or 'volume' in c.lower()]

        return {
            'datetime': dt_candidates[0] if dt_candidates else df.columns[0],
            'keyword': kw_candidates[0] if kw_candidates else (df.columns[1] if len(df.columns) > 1 else df.columns[0]),
            'count': count_candidates[0] if count_candidates else None
        }

    def fetch(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found at {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        cols = self._guess_columns(df)
        # standardize core column names
        rename_map = {cols['datetime']: 'datetime_raw', cols['keyword']: 'keyword'}

        # detect optional columns and normalize names so downstream code can use them
        def _find(col_keywords):
            for c in df.columns:
                cl = c.lower()
                for kw in col_keywords:
                    if kw in cl:
                        return c
            return None

        platform_col = _find(['platform', 'source', 'site'])
        content_col = _find(['content_type', 'content type', 'content', 'type'])
        region_col = _find(['region', 'country', 'location'])
        engagement_col = _find(['engagement_level', 'engagement', 'likes', 'shares', 'engagement_score'])

        if platform_col:
            rename_map[platform_col] = 'platform'
        if content_col:
            rename_map[content_col] = 'content_type'
        if region_col:
            rename_map[region_col] = 'region'
        if engagement_col:
            # normalize engagement to a single name so analytics can rely on it
            rename_map[engagement_col] = 'engagement'

        df = df.rename(columns=rename_map)

        if cols['count']:
            df = df.rename(columns={cols['count']: 'count'})
        else:
            # treat each row as 1 mention if no count column
            df['count'] = 1

        # parse datetimes lazily - leave parsing to processor for robust handling
        out_cols = ['datetime_raw', 'keyword', 'count']
        for optional in ('platform', 'content_type', 'region', 'engagement'):
            if optional in df.columns:
                out_cols.append(optional)

        return df[out_cols].copy()
