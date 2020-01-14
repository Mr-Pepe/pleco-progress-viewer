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
    global data, score_slider, score_file_name
    score_file_name = new
    data = Data(summary.score_files[new])
    score_slider.end = data.max_score()
    score_slider.value = min(100, data.max_score())
    update_plot()

def score_slider_callback(attr, old, new):
    update_plot()

def update_plot():
    global data, source_learned, source_reviewed

    # Get number of cards and characters above threshold for each timestamp
    n_cards = np.zeros(len(data.timestamps))
    n_chars = np.zeros(len(data.timestamps))

    for i_timestamp, timestamp in enumerate(data.timestamps):
        n_cards[i_timestamp] = np.count_nonzero(np.array(list(data.card_scores[timestamp].values())) > score_slider.value)
        n_chars[i_timestamp] = np.count_nonzero(np.array(list(data.char_scores[timestamp].values())) > score_slider.value)
    
    source_learned.data = dict(timestamps=data.timestamps,
                                n_cards=n_cards, 
                                n_characters=n_chars)

    source_reviewed.data = dict(timestamps=data.timestamps,
                                    n_reviews=np.array([data.reviewed[timestamp] for timestamp in data.timestamps]))


backups_dir = "./backups"

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
                           step=50,
                           callback_policy='throttle',
                           callback_throttle=500)

score_slider.on_change("value_throttled", score_slider_callback)

# Create a plot for the number of learned cards and characters and style its properties
hovertool_learned = HoverTool(
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
p_learned = figure(title="Number of learned words and characters", 
           x_axis_type='datetime',
           toolbar_location='above',
           tools=[hovertool_learned])
p_learned.title.text_font_size = '18pt'

p_learned.xaxis.major_label_text_font_size = '14pt'
p_learned.xaxis.major_label_orientation = pi/4
p_learned.yaxis.major_label_text_font_size = '14pt'

# Plot learned words and characters
source_learned = ColumnDataSource(data=dict(timestamps=[], 
                                    n_cards=[], 
                                    n_characters=[]))

p_learned.line('timestamps', 'n_cards', source=source_learned, 
        line_width=4,         
        legend_label='Number of cards learned',
        color='blue')

p_learned.line('timestamps', 'n_characters', source=source_learned,
        line_width=4,
        legend_label='Number of characters learned',
        color='red')
    
p_learned.y_range.start = 0

p_learned.legend.location = 'bottom_right'

# Create plot for number of reviews
hovertool_learned = HoverTool(
    tooltips=[
        ('Date', '@timestamps{%F}'),
        ('Reviews', '@n_reviews'),
    ],

    formatters={
        'timestamps': 'datetime'
    },

    mode='mouse'
)
p_reviewed = figure(title="Number of total reviews", 
           x_axis_type='datetime',
           toolbar_location='above',
           tools=[hovertool_learned])
p_reviewed.title.text_font_size = '18pt'

p_reviewed.xaxis.major_label_text_font_size = '14pt'
p_reviewed.xaxis.major_label_orientation = pi/4
p_reviewed.yaxis.major_label_text_font_size = '14pt'

# Plot number of reviews
source_reviewed = ColumnDataSource(data=dict(timestamps=[], 
                                            n_reviews=[]))

p_reviewed.line('timestamps', 'n_reviews', source=source_reviewed, 
                line_width=4,         
                legend_label='Number of total reviews',
                color='blue')       

p_reviewed.y_range.start = 0

p_reviewed.legend.location = 'bottom_right'
                                 

curdoc().add_root(layout([[layout([score_file_chooser, score_slider]), [[p_learned, p_reviewed]]]]))
update_plot()
