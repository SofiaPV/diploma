import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from Calculator import Calculator


class Visualiser:
    def __init__(self, mainfile=None, files=None):
        self._mainfile_name = mainfile
        self._files = files
        self._calculator = Calculator(mainfile, files)


    @property
    def mainfile_name(self):
        return self._mainfile_name

    @mainfile_name.setter
    def mainfile_name(self, new):
        self._calculator.mainfile = new
        self._mainfile_name = new

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, new):
        self._files = new
        self._calculator.files = new

    @staticmethod
    def spit_data(data=None):
        """
        :param data: array [[x1, y1, z1], ...]-like to split, if None than
                     must give a filename with data
        :return: x:List, y:List, z:List
        """
        if data is None:
            return

        x, y, z = [], [], []
        for line in data:
            x.append(line[0])
            y.append(line[1])
            z.append(line[2])
        return x, y, z

    def _make_df(self, data):
        """
        :return: DataFrame for constructing visuals
        """

        time_points = []
        x, y, z = [], [], []

        # dealing with main file data
        x_, y_, z_ = self.spit_data(data[0])
        npoints = len(x_)  # number of points in a frame
        time_points += [0 for _ in range(npoints)]
        x += x_
        y += y_
        z += z_

        # dealing with other files
        for i, frame in enumerate(data[1:]):

            x_, y_, z_ = self.spit_data(data=frame)
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

        return df

    def visualize_calculations(self):
        self._calculator.calculate()
        orig = self._calculator.original_points
        moved = self._calculator.moved_points

        df = self._make_df_calculated(orig, moved)
        fig = px.scatter_3d(df, x='x', y='y', z='z', animation_frame="time", color='group')

        frames = []
        for time_group in df['time'].unique():

            df_frame = df[df['time'] == time_group]
            groups = df_frame['group'].unique()

            traces = []
            for group in groups:
                traces.append(
                    dict(
                        type='scatter3d',
                        x=df_frame[df_frame['group'] == group]['x'],
                        y=df_frame[df_frame['group'] == group]['y'],
                        z=df_frame[df_frame['group'] == group]['z'],
                        mode='markers',
                        marker=dict(
                            size=5,
                            color='red' if group == 'red' else 'blue',
                        ),
                        legendgroup=group,
                        name="Точки в состоянии покоя" if group == 'red' else "Точки в процессе эксперимента",
                        showlegend=True
                    )
                )

            frames.append(
                dict(
                    name=str(time_group),
                    data=traces,
                    layout=dict(
                        annotations=[dict(
                            x=1.075,
                            y=0.5,
                            text=f"Кадр {time_group}",
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
            )

        fig.frames = frames

        x_range = [df['x'].min() - 1, df['x'].max() + 1]
        y_range = [df['y'].min() - 1, df['y'].max() + 1]
        z_range = [df['z'].min() - 1, df['z'].max() + 1]

        # Настройка кнопки "play" для анимации
        fig.update_layout(
            margin=dict(
                r=250,  # Отступ справа
            ),
            sliders=[dict(
                active=0,
                currentvalue=dict(prefix="Кадр: "),
                steps=[dict(
                    label=str(time_group),
                    method='animate',
                    args=[[str(time_group)], dict(frame=dict(duration=100, redraw=True))],
                ) for time_group in df['time'].unique()],
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
                ),
                yaxis=dict(
                    backgroundcolor='rgb(50, 55, 54)',
                    gridcolor='white',
                    range=y_range,
                ),
                zaxis=dict(
                    backgroundcolor='rgb(50, 55, 54)',
                    gridcolor='white',
                    range=z_range,
                ),
            ),
            legend=dict(
                title=None, #  "Группы точек",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=1.,
                yanchor="bottom"
            )
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    def _flatten(self, data):
        time_points = []
        x, y, z = [], [], []
        npoints = len(data[0])

        for i, frame in enumerate(data):
            x_, y_, z_ = self.spit_data(data=frame)
            time_points += [i for _ in range(npoints)]
            x += x_
            y += y_
            z += z_
        return time_points, x, y, z

    def _make_df_calculated(self, orig, moved):
        """
        :return: DataFrame for constructing visuals
        """
        time_point, x, y, z = self._flatten(orig)
        group = ['red' for _ in x]
        buf = self._flatten(moved)
        time_point += buf[0]
        x += buf[1]; y += buf[2]; z += buf[3]
        group += ['blue' for _ in buf[0]]

        # making DF
        df = pd.DataFrame({
            'time': time_point,
            'x': x,
            'y': y,
            'z': z,
            'group': group
        })

        return df

    def visualize_original_data(self):
        data = [self._calculator.mainframe] + self._calculator.original_points
        df = self._make_df(data)
        fig = px.scatter_3d(df, x='x', y='y', z='z', animation_frame="time")

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
                            color='blue',
                        ),
                        name=f"Точки в процессе эксперимента",
                        showlegend=True,
                    )
                ],
                name=str(time_group),
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
            legend=dict(
                title=None,  # "Группы точек",
                orientation="h",
                x=0.5,
                xanchor="center",
                y=1.,
                yanchor="bottom"
            ),
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')




