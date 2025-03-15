import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from FileManager import FileManager


class Visualiser:
    def __init__(self, mainfile=None, files=None):
        self._mainfile_name = mainfile
        self._files = files
        self._manager = FileManager(mainfile, files)

    def _make_df(self):
        """
        :return: DataFrame for constructing visuals
        """
        time_points = []
        x, y, z = [], [], []

        # dealing with main file data
        x_, y_, z_ = self._manager.spit_file_data(self._mainfile_name)
        npoints = len(x_)  # number of points in a frame
        time_points += [0 for _ in range(npoints)]
        x += x_
        y += y_
        z += z_

        # dealing with other files
        for i, fname in enumerate(self._files):
            x_, y_, z_ = self._manager.spit_file_data(fname)
            time_points += [i+1 for _ in range(npoints)]
            x += x_
            y += y_
            z += z_

        # making DF
        df = pd.DataFrame({
            'time': time_points,
            'x': x,
            'y': y,
            'z': z,
        })

        #  df['marker_color'] = df['time'].apply(lambda t: 'red' if t == 0 else 'blue')
        return df

    def make_visuals(self):
        df = self._make_df()
        fig = px.scatter_3d(df, x='x', y='y', z='z')

        # animation frames
        frames = [
            dict(
                data=[
                    dict(
                        type='scatter3d',
                        x=df.loc[df['time'] == time_group, 'x'],
                        y=df.loc[df['time'] == time_group, 'y'],
                        z=df.loc[df['time'] == time_group, 'z'],
                        mode='markers',
                        marker=dict(
                            size=5,
                        ),
                        name=f"Time {time_group}"
                    )
                ],
                name=str(time_group),
                layout=dict(
                    annotations=[dict(
                        x=1.05,  # annotation position
                        y=0.5,
                        text=f"Кадр {time_group}",  # уникальная аннотация для кадра
                        showarrow=False,
                        font=dict(size=12, color="black"),
                        align="right",
                        bordercolor="black",
                        borderwidth=1,
                        bgcolor="white",
                        opacity=0.8
                    )]
                )
            )
            for time_group in df['time'].unique()
        ]
        fig.frames = frames

        df_time_0 = df[df['time'] == 0]
        fig.add_trace(
            go.Scatter3d(
                x=df_time_0['x'],
                y=df_time_0['y'],
                z=df_time_0['z'],
                mode='markers',
                marker=dict(size=5, color='red'),
                name="Точки в состоянии покоя"
            )
        )

        # Get fixed ranges
        x_range = [df['x'].min() - 1, df['x'].max() + 1]
        y_range = [df['y'].min() - 1, df['y'].max() + 1]
        z_range = [df['z'].min() - 1, df['z'].max() + 1]

        # "play" button
        fig.update_layout(
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[dict(
                    label='▶',
                    method='animate',
                    args=[None, dict(frame=dict(duration=100, redraw=True),
                                     fromcurrent=True)]
                )]
            )],
            sliders=[dict(
                active=0,
                currentvalue=dict(prefix="Кадр: "),
                steps=[dict(
                    label=str(time_group),
                    method='animate',
                    args=[[str(time_group)], dict(frame=dict(duration=100, redraw=True))],
                ) for time_group in df['time'].unique()]
            )],
            plot_bgcolor='black',  # Цвет фона графика
            paper_bgcolor='black',  # Цвет фона вокруг графика
            font=dict(color='white'),  # Цвет текста на графике
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Z",
                aspectmode='cube',
                xaxis=dict(
                    backgroundcolor='rgb(50, 55, 54)',
                    gridcolor='white',
                    range=x_range,
                    #fixedrange=True,  # фиксированный диапазон
                ),
                yaxis=dict(
                    backgroundcolor='rgb(50, 55, 54)',
                    gridcolor='white',
                    range=y_range,
                    #fixedrange=True,  # фиксированный диапазон
                ),
                zaxis=dict(
                    backgroundcolor='rgb(50, 55, 54)',
                    gridcolor='white',
                    range=z_range,
                    #fixedrange=True,  # фиксированный диапазон
                ),
            ),
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')




