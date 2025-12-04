# mediapulse/analytics.py (updated)
import pandas as pd
import numpy as np
from typing import Dict

class AnalyticsSummary:
    def compute_peak(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0
        return int(df['count'].max())

    def compute_avg(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        return float(df['count'].mean())

    def compute_trend(self, df: pd.DataFrame) -> str:
        if df.shape[0] < 2:
            return '→'
        first = df.iloc[0]['count']
        last = df.iloc[-1]['count']
        if last > first:
            return '↑'
        elif last < first:
            return '↓'
        return '→'

    def moving_average(self, df: pd.DataFrame, window: int = 3) -> pd.Series:
        return df['count'].rolling(window=window, min_periods=1).mean()

    def percent_change(self, df: pd.DataFrame) -> float:
        if df.shape[0] < 2:
            return 0.0
        start = df['count'].iloc[0] or 1
        return float(((df['count'].iloc[-1] - df['count'].iloc[0]) / start) * 100)

    def top_trending_keywords(self, df: pd.DataFrame, last_n_periods: int = 7, top_k: int = 5) -> pd.DataFrame:
        recent_periods = sorted(df['datetime'].unique())[-last_n_periods:]
        recent = df[df['datetime'].isin(recent_periods)]
        summary = recent.groupby('keyword')['count'].sum().reset_index().sort_values('count', ascending=False).head(top_k)
        return summary

    def spike_detection(self, df: pd.DataFrame, z_thresh: float = 2.5) -> pd.DataFrame:
        """
        Returns rows flagged as spikes based on z-score on counts grouped by keyword.
        """
        out = []
        for kw, g in df.groupby('keyword'):
            counts = g['count']
            mean = counts.mean()
            std = counts.std(ddof=0) or 1.0
            z = (counts - mean) / std
            spikes = g.loc[z.abs() > z_thresh].copy()
            spikes['z_score'] = z[z.abs() > z_thresh]
            if not spikes.empty:
                out.append(spikes)
        if out:
            return pd.concat(out).sort_values(['keyword','datetime'])
        else:
            return pd.DataFrame(columns=list(df.columns)+['z_score'])

    def engagement_distribution(self, df: pd.DataFrame, by: str = 'platform') -> pd.DataFrame:
        """
        Return summary statistics of engagement grouped by 'by' (platform/content_type/region)
        """
        if by not in df.columns:
            raise ValueError(f"{by} not a column")
        summary = df.groupby(by)['engagement'].agg(['count','mean','median','std','max']).reset_index()
        return summary

    def region_top_content(self, df: pd.DataFrame, region: str, top_k: int = 5) -> pd.DataFrame:
        region_df = df[df['region'].str.lower() == region.lower()]
        if region_df.empty:
            return pd.DataFrame()
        return region_df.groupby('content_type')['engagement'].sum().reset_index().sort_values('engagement', ascending=False).head(top_k)

    def compute_all(self, df: pd.DataFrame, ma_window: int = 3) -> Dict:
        return {
            'peak': self.compute_peak(df),
            'avg': round(self.compute_avg(df), 2),
            'trend': self.compute_trend(df),
            'percent_change': round(self.percent_change(df), 2),
            'moving_average': self.moving_average(df, window=ma_window).tolist()
        }
