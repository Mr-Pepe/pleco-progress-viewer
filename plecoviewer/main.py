from plecoviewer.utils import Data, Backup, BackupSummary
from random import random
from functools import partial
from itertools import compress
import time
import numpy as np

import bokeh
from bokeh.layouts import column, layout
from bokeh.models import Button, Select, DatetimeTickFormatter
from bokeh.plotting import figure, curdoc, show
from bokeh.models.widgets import Slider
from bokeh.models.sources import ColumnDataSource


def score_file_chooser_callback(attr, old, new):
    global data, score_file_name, score_slider
    score_file_name = new
    data = Data(summary.score_files[new])
    score_slider.end = data.max_score()
    score_slider.value = min(100, data.max_score())
    update_plot()


def score_slider_callback(attr, old, new):
    update_plot()


def update_plot():
    global p, data, source

    # Get number of cards above threshold for each timestamp
    y = np.zeros(len(data.timestamps))

    for i_timestamp, timestamp in enumerate(data.timestamps):
        y[i_timestamp] = np.count_nonzero(data.scores[timestamp] > score_slider.value)
    
    source.data = dict(x=data.timestamps,
                       y1=y,
                       y2=np.zeros_like(y))


backups_dir = "/home/felipe/Projects/PlecoViewer/backups"

# The summary holds all relevant data
summary = BackupSummary(backups_dir)

if len(summary.score_files) == 0:
    raise Exception("Specified directory does not contain any Pleco backups.")

# data holds the preprocessed data for plotting
# Per default the first score file is selected
score_file_name = list(summary.score_files.keys())[0]
data = Data(summary.score_files[score_file_name])

# create a plot and style its properties
p = figure(title="Number of cards learned", 
           x_axis_type='datetime',
           toolbar_location=None)

# Add a menu to select the score file
score_file_names = [fname for fname in summary.score_files.keys()]
score_file_chooser = Select(title='Score file', value='', options=score_file_names)
score_file_chooser.on_change("value", score_file_chooser_callback)

# Add a slider to select when a card is considered as learned
score_slider = Slider(title="Cards with score above ", 
                           start=0, 
                           end=data.max_score(), 
                           value=min(100, data.max_score()), 
                           step=100,
                           callback_policy='throttle',
                           callback_throttle=500)

score_slider.on_change("value_throttled", score_slider_callback)

source = ColumnDataSource(data=dict(x=[], y1=[], y2=[]))
p.varea('x', 'y1', 'y2', source=source)
update_plot()
curdoc().add_root(layout([[layout([score_file_chooser, score_slider]), p]]))

