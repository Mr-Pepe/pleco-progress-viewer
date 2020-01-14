from plecoviewer.utils import Data, Backup, BackupSummary
from random import random
from functools import partial
from itertools import compress
import time
import numpy as np
from math import pi

import bokeh
from bokeh.layouts import column, layout
from bokeh.models import Button, Select, DatetimeTickFormatter
from bokeh.plotting import figure, curdoc, show
from bokeh.models.widgets import Slider, CheckboxGroup
from bokeh.models.sources import ColumnDataSource
from bokeh.models import HoverTool, Legend, LegendItem, Range1d

COLORS = ['red', 'blue']

def score_file_chooser_callback(attr, old, new):
    global data, score_slider, score_file_name, source
    score_file_name = new
    data = Data(summary.score_files[new])
    score_slider.end = data.max_score()
    score_slider.value = min(100, data.max_score())
    update_plot()

def score_slider_callback(attr, old, new):
    update_plot()

def update_plot():
    global p, data, source

    # Get number of cards and characters above threshold for each timestamp
    n_cards = np.zeros(len(data.timestamps))
    n_chars = np.zeros(len(data.timestamps))

    for i_timestamp, timestamp in enumerate(data.timestamps):
        n_cards[i_timestamp] = np.count_nonzero(np.array(list(data.card_scores[timestamp].values())) > score_slider.value)
        n_chars[i_timestamp] = np.count_nonzero(np.array(list(data.char_scores[timestamp].values())) > score_slider.value)
    
    source.data = dict(timestamps=data.timestamps,
                       n_cards=n_cards, 
                       n_characters=n_chars)


backups_dir = "/home/felipe/Projects/PlecoViewer/backups"

# The summary holds all relevant data
summary = BackupSummary(backups_dir)

if len(summary.score_files) == 0:
    raise Exception("Specified directory does not contain any Pleco backups.")

# data holds the preprocessed data for plotting
# Per default the first score file is selected
score_file_name = list(summary.score_files.keys())[0]
data = Data(summary.score_files[score_file_name])

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

# Create a plot and style its properties
hovertool = HoverTool(
    tooltips=[
        ('Date', '@timestamps{%F}'),
        ('Cards', '@n_cards'),
        ('Characters', '@n_characters')
    ],

    formatters={
        'timestamps': 'datetime'
    },

    mode='mouse'
)
p = figure(title="", 
           x_axis_type='datetime',
           toolbar_location='above',
           tools=[hovertool])
p.title.text_font_size = '18pt'

p.xaxis.major_label_text_font_size = '14pt'
p.xaxis.major_label_orientation = pi/4
p.yaxis.major_label_text_font_size = '14pt'

# Plot
source = ColumnDataSource(data=dict(timestamps=[], 
                                    n_cards=[], 
                                    n_characters=[]))

r = p.line('timestamps', 'n_cards', source=source, 
        line_width=4,         
        legend_label='Number of cards learned',
        color='blue')

p.line('timestamps', 'n_characters', source=source,
        line_width=4,
        legend_label='Number of characters learned',
        color='red')
    
p.y_range.start = 0

p.legend.location = 'bottom_right'

curdoc().add_root(layout([[layout([score_file_chooser, score_slider]), p]]))
update_plot()
