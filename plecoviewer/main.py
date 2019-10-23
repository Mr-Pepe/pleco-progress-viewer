# myapp.py
from plecoviewer.utils import get_max_score, Backup, BackupSummary, get_backups, Container
# from plecoviewer.callbacks import score_file_chooser_callback
from random import random
from functools import partial

import bokeh
from bokeh.layouts import column, layout
from bokeh.models import Button, Select, DatetimeTickFormatter
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc
from bokeh.models.widgets import RangeSlider
from bokeh.models.sources import ColumnDataSource

def score_file_chooser_callback(attr, old, new):
    global data, score_file_name, max_score, p, score_slider
    score_file_name = new
    data = summary.score_files[new]
    max_score = get_max_score(data)
    score_slider.end = max_score
    score_slider.value = (0, max_score)
    update_plot()

def score_slider_callback(attr, old, new):
    update_plot()

def update_plot():
    global p, source
    x = []
    y = []

    for card in data:
        # Only show cards that have a high enough score
        
        if sorted(data[card]['scores'].items())[-1][1] >= score_slider.value[0] and \
           sorted(data[card]['scores'].items())[-1][1] <= score_slider.value[1]:
            x.append([])
            y.append([])

            for (timestamp, score) in sorted(data[card]['scores'].items()):
                x[-1].append(timestamp)
                y[-1].append(score)

    # x = [[ts for ts in sorted(data[card]['scores'])] for (card, scores) in data.items()]
    # y = [[score for (timestamp, score) in sorted(data[card]['scores'].items())] for (card, scores) in data.items()]
    
    source.data = dict(x=x, y=y)


backups_dir = "/home/felipe/Projects/PlecoViewer/backups"

# The summary holds all relevant data
summary = BackupSummary(backups_dir)

if len(summary.score_files) == 0:
    raise Exception("Specified directory does not contain any Pleco backups.")

# data selects the data to be plotted from the summary
# Per default the first score file is selected
score_file_name = list(summary.score_files.keys())[0]
data = summary.score_files[score_file_name]
max_score = get_max_score(data)

# create a plot and style its properties
p = figure(x_axis_type='datetime', toolbar_location=None, title='Test')
# x = [[ts for ts in sorted(data[card]['scores'])] for (card, scores) in data.items()]
# y = [[score for (timestamp, score) in sorted(data[card]['scores'].items())] for (card, scores) in data.items()]
# p.multi_line(x, y)
p.border_fill_color = 'white'
p.background_fill_color = 'grey'
p.outline_line_color = None
p.grid.grid_line_color = None

# Add a menu to select the score file
score_file_names = [fname for fname in summary.score_files.keys()]
score_file_chooser = Select(title='Score file', value='', options=score_file_names)
score_file_chooser.on_change("value", score_file_chooser_callback)

# Add a slider to select when a card is considered as learned
score_slider = RangeSlider(title="Show cards with score in range ", start=0, end=max_score, value=(0, max_score), step=1)
score_slider.on_change("value", score_slider_callback)

source = ColumnDataSource(data=dict(x=[[]], y=[[]]))
update_plot()
p.multi_line('x', 'y', source=source)
curdoc().add_root(layout([[layout([score_file_chooser, score_slider]), p]]))

