import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd

class ChartRenderer:
    def plotly_time_series(self, df: pd.DataFrame, keyword: str, moving_avg: list = None, color_col: str = None, title: str = None):
        dfp = df.copy()
        dfp = dfp.sort_values('datetime')
        fig = go.Figure()
        if color_col and color_col in dfp.columns:
            for k, grp in dfp.groupby(color_col):
                fig.add_trace(go.Scatter(x=grp['datetime'], y=grp['count'], mode='lines+markers', name=str(k)))
        else:
            fig.add_trace(go.Scatter(x=dfp['datetime'], y=dfp['count'], mode='lines+markers', name=f'{keyword}'))
        if moving_avg is not None:
            fig.add_trace(go.Scatter(x=dfp['datetime'], y=moving_avg, mode='lines', name='Moving Avg', line=dict(dash='dash')))
        fig.update_layout(title=title or f"{keyword} — Trend", template='plotly_dark', xaxis_title='Date', yaxis_title='Count')
        return fig

    def plotly_stacked_area(self, df: pd.DataFrame, date_col='datetime', category_col='platform'):
        """
        df must be aggregated: columns [date_col, category_col, count]
        Returns stacked area chart per category.
        """
        dfp = df.copy()
        dfp[date_col] = pd.to_datetime(dfp[date_col])
        fig = px.area(dfp, x=date_col, y='count', color=category_col, line_group=category_col)
        fig.update_layout(template='plotly_dark')
        return fig

    def plotly_region_heatmap(self, df: pd.DataFrame, region_col='region'):
        """
        Creates a simple choropleth-ready dataframe (region->value). If regions are countries or states,
        you can pass to px.choropleth by mapping names to ISO codes externally.
        """
        summary = df.groupby(region_col)['count'].sum().reset_index().rename(columns={region_col: 'region', 'count': 'value'})
        # return data - visualization choice depends on region granularity
        fig = px.bar(summary.sort_values('value', ascending=False), x='region', y='value', title='Engagement by Region')
        fig.update_layout(template='plotly_dark', xaxis_tickangle=-45)
        return fig

    def plotly_box_engagement(self, df: pd.DataFrame, by='platform'):
        if by not in df.columns:
            raise ValueError("grouping column not present")
        fig = px.box(df, x=by, y='engagement', points='outliers', title=f'Engagement distribution by {by}')
        fig.update_layout(template='plotly_dark')
        return fig

    def matplotlib_export(self, df: pd.DataFrame, keyword: str, filepath: str):
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(pd.to_datetime(df['datetime']), df['count'], marker='o', label=keyword)
        ax.set_title(f"{keyword} Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Count")
        ax.legend()
        fig.autofmt_xdate()
        fig.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close(fig)
        return filepath
