# myapp.py
from plecoviewer.utils import Backup, BackupSummary, get_backups
# from plecoviewer.callbacks import score_file_chooser_callback
from random import random
from functools import partial

import bokeh
from bokeh.layouts import column, layout
from bokeh.models import Button, Select, DatetimeTickFormatter
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc


def score_file_chooser_callback(attr, old, new):
    global data
    data = summary.score_files[new]
    update_plot()


def update_plot():
    global p
    x = [[ts for ts in sorted(data[card]['scores'])] for (card, scores) in data.items()]
    y = [[score for (timestamp, score) in sorted(data[card]['scores'].items())] for (card, scores) in data.items()]
    p.multi_line(x, y)


backups_dir = "/home/felipe/Projects/PlecoViewer/backups"

# The summary holds all relevant data
summary = BackupSummary(backups_dir)

if len(summary.score_files) == 0:
    raise Exception("Specified directory does not contain any Pleco backups.")

# data selects the data to be plotted from the summary
# Per default the first score file is selected
data = summary.score_files[list(summary.score_files.keys())[0]]

# create a plot and style its properties
p = figure(x_axis_type='datetime', toolbar_location=None, title='Test')
x = [[ts for ts in sorted(data[card]['scores'])] for (card, scores) in data.items()]
y = [[score for (timestamp, score) in sorted(data[card]['scores'].items())] for (card, scores) in data.items()]
p.multi_line(x, y)
p.border_fill_color = 'white'
p.background_fill_color = 'grey'
p.outline_line_color = None
p.grid.grid_line_color = None

# Add a menu to select the score file
score_file_names = [fname for fname in summary.score_files.keys()]
score_file_chooser = Select(title='Score file', value='', options=score_file_names)
score_file_chooser.on_change("value", score_file_chooser_callback)

# inputs = column(select)
curdoc().add_root(layout([[score_file_chooser, p]]))
