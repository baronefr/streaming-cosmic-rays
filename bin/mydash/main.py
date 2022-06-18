#!/usr/bin/env python3

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 10 / Barone Nagaro Ninni Valentini
#
#  This is the monitor dashboard for the cosmic rays
#  telescope, reading live data from Kafka topic.
#
#  launch with    bokeh serve --show bin/mydash/ ...
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 17 jun 2022
#  Open Access licence
#--------------------------------------------------------

from datetime import datetime
from threading import Thread
from kafka import KafkaConsumer
from queue import Queue
import json
import numpy as np
import sys
import configparser
from configparser import ExtendedInterpolation

from bokeh.layouts import column, row, layout, grid
from bokeh.models import ColumnDataSource, Div, Paragraph, Range1d, Slider
from bokeh.plotting import curdoc, figure

from bokeh.server.server import Server
from bokeh.models import Button, Dropdown, Label, Span, RadioButtonGroup, CheckboxGroup
from bokeh.models.widgets import Tabs, Panel


DEBUG_LEVEL = 0
# 0  -  errors only
# 1  -  warnings only
# 2  -  user actions
# 4  -  full info


# parsing settings
if len(sys.argv) > 1:
    print('-- environment mode, target:', sys.argv[1])
    
    # read config file
    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(sys.argv[1])
    try:
        KAFKA_BOOTSTRAP_SERVER = str( config['KAFKA']['KAFKA_BOOTSTRAP'] ).replace('\'', '')
        TOPIC = str(config['KAFKA']['TOPIC_RES']).replace('\'', '')
    except Exception as e:
        print('ERROR: config file error')
        print(e)
        sys.exit(1)
else:
    print('-- standalone mode')
    KAFKA_BOOTSTRAP_SERVER = 'localhost:9092'
    TOPIC = 'cosmo-results'

print('[info] configuration:')
print(f' server {KAFKA_BOOTSTRAP_SERVER} on topic {TOPIC}')

#########################################################

chamber_colors = ["#ff2b24", "#ffcc00", "#00cc33", "#004ecc"]
TIMESTAMP_FORMAT = "%H:%M:%S %d-%m-%Y"

#########################################################

class mykafka_consumer(Thread):
    
    def __init__(self):
        Thread.__init__(self) 
        
        # setup kafka consumer        
        consumer = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
                                 consumer_timeout_ms=30000
                                )
        consumer.subscribe(TOPIC)
        print( consumer.subscription() )
        
        # polling strategy
        consumer.poll(timeout_ms=0,         #<<--- do not enable dead-times before one poll to the next
                      max_records=None,     #<<--- do not limit the number of records to consume at once 
                      update_offsets=True   #<<--- update the reading offsets on this topic
                     )
        #consumer.seek_to_beginning()  # you like to rewind?
        
        self.kc = consumer
        
        # Initializing a queue
        self.queue = Queue(maxsize = 20)
        self.semaphore = True
        self.pause_button = None
        self.pause_type = None
        self.last_timestamp = 'never'
        print('kafka setup!')
        
    def set_pause_callback(self, bt, cb):
        self.pause_button = bt
        self.pause_type = cb
        
    def pause_keep_buffer(self):
        # note:  if (0 in self.pause_type.active) is True -> checkbox is active
        return (0 in self.pause_type.active)
    
    def toggle_semaphore(self):
        self.semaphore = not self.semaphore
        if self.pause_button is not None:
            if self.semaphore: self.pause_button.button_type = 'success'
            else:              self.pause_button.button_type = 'warning'
        return self.semaphore
    
    def run(self):
        for msg in self.kc:
            if self.queue.full():
                print(' ERROR: Queue is full, should you be faster?')
                break
            self.last_datetime = datetime.now()
            self.last_timestamp = self.last_datetime.strftime(TIMESTAMP_FORMAT)
            
            if self.semaphore or ( self.pause_keep_buffer() ):
                self.queue.put(msg)
            
            if(DEBUG_LEVEL >= 3):
                print('received msg')


# start simulator process
kc = mykafka_consumer()
kc.daemon = True # let the main thread exit even though the workers are blocking
kc.start()

print('Kafka consumer online!')



###########################
# use BOKEH WEB INTERFACE #
###########################

def filler(dd, shift = 0, key = 'edg', val = 'cnt'):
    outs = np.zeros(64)
    outs[ [x - shift for x in dd[key]] ] = dd[val]
    return outs

def filler_group(dd, shift = 0, key = 'edg', val = 'cnt'):
    mtx = np.concatenate([ np.array(xx[key]) for xx in dd ])
    all_min = np.min(mtx);  all_max = np.max(mtx);
    outs = np.zeros( (len(dd), int(all_max-all_min+1)) )
    for i in range(len(dd)):
        outs[i][ [x - all_min for x in dd[i][key]] ] = dd[i][val]
    return np.arange(all_min, all_max +1), outs

def update_graphs():  # read data from buffer & update plotsz
    global kc
    
    # update data timestamp
    div_last_data.text = div_last_data_strbase.format( kc.last_timestamp )
    
    # if queue is empty...
    if kc.queue.empty():
        if(DEBUG_LEVEL >= 3): print('Queue empty, not updating')
        return 1
    
    # ... or if there is new data
    dd = json.loads( kc.queue.get().value )
    
    ## update history
    cds_tdc_history.stream( dict( t=[kc.last_datetime], ch0=[dd['ch0']], ch1=[dd['ch1']], 
                                  ch2=[dd['ch2']], ch3=[dd['ch3']], tot=[dd['n']])
                          )
    
    if not kc.semaphore:
        # do not update main tab
        return 0
    
    ## update main tab
    div_proc_hits.text = div_proc_hits_strbase % (dd['ch0'], dd['ch1'], dd['ch2'], dd['ch3'],
                                                  np.sum([dd['ch0'], dd['ch1'], dd['ch2'], dd['ch3']]) )
    div_last_refresh.text = div_last_refresh_strbase.format( datetime.now().strftime(TIMESTAMP_FORMAT) )
    
    # 4 | TDC_CHANNEL in each ORBIT_CNT, per chamber
    x, cnt = filler_group( [dd['ch0_orb_hist'], dd['ch1_orb_hist'], dd['ch2_orb_hist'], dd['ch3_orb_hist']] )
    cds_tdc_orb.data =  {'x': x, 'ch0': cnt[0], 'ch1': cnt[1], 'ch2': cnt[2], 'ch3': cnt[3]}
    
    # 3 | active TDC_CHANNEL, per chamber
    cds_tdc_active.data =  {'x': np.arange(64),
                            'ch0': filler(dd['ch0_tdc_hist']),
                            'ch1': filler(dd['ch1_tdc_hist'], shift=64),
                            'ch2': filler(dd['ch2_tdc_hist']),
                            'ch3': filler(dd['ch3_tdc_hist'], shift=64)}
    
    # 5 | active TDC_CHANNEL, per chamber, with scintillator
    cds_tdc_scint.data =  {'x': np.arange(64),
                           'ch0': filler(dd['ch0_tdc_hist_scint']),
                           'ch1': filler(dd['ch0_tdc_hist_scint'], shift=64),
                           'ch2': filler(dd['ch0_tdc_hist_scint']),
                           'ch3': filler(dd['ch0_tdc_hist_scint'], shift=64)}
    
    # 6 | drift time plot
    edges = np.arange(0,390,30) # set here the binning property
    hist0, _ = np.histogram(dd['ch0_drifts'], bins=edges)
    hist1, _ = np.histogram(dd['ch1_drifts'], bins=edges)
    hist2, _ = np.histogram(dd['ch2_drifts'], bins=edges)
    hist3, _ = np.histogram(dd['ch3_drifts'], bins=edges)
    cds_drifts.data = { 'ch0': hist0, 'ch1': hist1, 'ch2': hist2, 'ch3': hist3,
                       'edgel':edges[:-1], 'edger':edges[1:]}
    return 0

    
###############
# bokeh plots #
###############

cds_tdc_orb = ColumnDataSource( {'x':[], 'ch0':[],'ch1':[],'ch2':[],'ch3':[]} )
cds_tdc_active = ColumnDataSource( {'x':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[]} )
cds_tdc_scint = ColumnDataSource( {'x':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[]} )
cds_drifts = ColumnDataSource( { 'ch0': [], 'ch1': [], 'ch2': [], 'ch3': [], 'edgel':[], 'edger':[]} )
cds_tdc_history = ColumnDataSource( {'t':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[], 'tot':[]} )

# active TDC vs orbits for each detector
plot_TDC_orbits = figure(sizing_mode="stretch_width",
                         plot_height=320, tools="pan,reset,save"
        #toolbar_location=None
    )
plot_TDC_orbits.xaxis.axis_label = "orbits"
plot_TDC_orbits.yaxis.axis_label = "active TDC"
plot_TDC_orbits.line(source=cds_tdc_orb, x="x", y="ch0", line_width = 2, line_color = chamber_colors[0])
plot_TDC_orbits.line(source=cds_tdc_orb, x="x", y="ch1", line_width = 2, line_color = chamber_colors[1])
plot_TDC_orbits.line(source=cds_tdc_orb, x="x", y="ch2", line_width = 2, line_color = chamber_colors[2])
plot_TDC_orbits.line(source=cds_tdc_orb, x="x", y="ch3", line_width = 2, line_color = chamber_colors[3])

# TDC histograms per channel (active + scintillator aided)
hist_TDC_active = figure(plot_width=450,  plot_height=320, tools="pan,reset,save")
hist_TDC_active.xaxis.axis_label = "TDC"
hist_TDC_active.vbar_stack(['ch0', 'ch1','ch2','ch3'], x='x', width=0.9, source=cds_tdc_active, color = chamber_colors)
hist_TDC_scint = figure(plot_width=450,  plot_height=320, tools="pan,reset,save")
hist_TDC_scint.xaxis.axis_label = "TDC"
hist_TDC_scint.vbar_stack(['ch0', 'ch1','ch2','ch3'], x='x', width=0.9, source=cds_tdc_scint, color = chamber_colors)

# drift time histo
hist_drift0 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch0', toolbar_location=None)
hist_drift0.quad(source=cds_drifts, top="ch0", bottom=0, left="edgel", right="edger", color = chamber_colors[0])
hist_drift1 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch1', toolbar_location=None)
hist_drift1.quad(source=cds_drifts, top="ch1", bottom=0, left="edgel", right="edger", color = chamber_colors[1])
hist_drift2 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch2', toolbar_location=None)
hist_drift2.quad(source=cds_drifts, top="ch2", bottom=0, left="edgel", right="edger", color = chamber_colors[2])
hist_drift3 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch3', toolbar_location=None)
hist_drift3.quad(source=cds_drifts, top="ch3", bottom=0, left="edgel", right="edger", color = chamber_colors[3])

plot_TDC_history = figure( 
        plot_width=900, plot_height=320, tools="pan,reset,save",
        x_axis_type='datetime', sizing_mode="stretch_width")
plot_TDC_history.xaxis.axis_label = "time"
plot_TDC_history.yaxis.axis_label = "streamed events"
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch0", line_width = 2,
                      legend_label="Ch0 hits", line_color = chamber_colors[0])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch1", line_width = 2, 
                      legend_label="Ch1 hits", line_color = chamber_colors[1])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch2", line_width = 2,
                      legend_label="Ch2 hits",line_color = chamber_colors[2])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch3", line_width = 2,
                      legend_label="Ch3 hits", line_color = chamber_colors[3])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="tot", line_width = 2,
                      legend_label="Spark buffer", line_color = 'purple')
plot_TDC_history.legend.location = "top_left"
##########
#  misc  #
##########

# styles
notsobig = {"font-size": "120%", "font-weight": "bold"}
big = {"font-size": "150%", "font-weight": "bold"}
bigger = {"font-size": "200%", "font-weight": "bold"}

# header
head_text = [ Div(text=r"dashboard ver 1.0") ]

# button to start/stop simulation
pause_bt = Button(label='pause', button_type="success", width=100, sizing_mode="fixed", align='center')
pause_bt.on_click( kc.toggle_semaphore )
pause_cbox = CheckboxGroup(labels=['keep history updated in pause'], active=[0], align='center')

kc.set_pause_callback(pause_bt, pause_cbox) # set callback objects



# graph selector  # dismissed
#graph_type_tdc_labels = ["Histogram", "Heatmap"]
#graph_type_tdc = RadioButtonGroup(labels=graph_type_tdc_labels, active=0)


# divs
div_proc_hits_strbase = """<br><style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;}
.tg td{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  overflow:hidden;padding:10px 5px;word-break:normal;}
.tg th{border-color:black;border-style:solid;border-width:1px;font-family:Arial, sans-serif;font-size:14px;
  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
.tg .tg-x028{background-color:#000000;border-color:#000000;color:#ffffff;font-weight:bold;text-align:center;vertical-align:top;height:5px}
.tg .tg-z2n5{background-color:#004ecc;border-color:#000000;color:#ffffff;font-weight:bold;text-align:center;vertical-align:top;height:5px}
.tg .tg-wp8o{border-color:#000000;text-align:center;vertical-align:top}
.tg .tg-04g2{background-color:#ff2b24;border-color:#000000;color:#ffffff;font-weight:bold;text-align:center;vertical-align:top;height:5px}
.tg .tg-mqa1{border-color:#000000;font-weight:bold;text-align:center;vertical-align:top}
.tg .tg-byd0{background-color:#ffcc00;border-color:#000000;font-weight:bold;text-align:center;vertical-align:top;height:5px}
.tg .tg-pwog{background-color:#00cc33;border-color:#000000;color:#ffffff;font-weight:bold;text-align:center;vertical-align:top;height:5px}
</style>
<table class="tg">
<thead>
  <tr style="height:5px;">
    <th class="tg-mqa1" colspan="4">Processed hits (cleansed)</th>
    <th class="tg-mqa1">Total hits</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td class="tg-wp8o">%d</td>
    <td class="tg-wp8o">%d</td>
    <td class="tg-wp8o">%d</td>
    <td class="tg-wp8o">%d</td>
    <td class="tg-wp8o">%d</td>
  </tr>
  <tr style="height:5px;">
    <td class="tg-04g2">Ch0</td>
    <td class="tg-byd0">Ch1</td>
    <td class="tg-pwog">Ch2</td>
    <td class="tg-z2n5">Ch3</td>
    <td class="tg-x028">all</td>
  </tr>
</tbody>
</table>
<br>
<br>
<br>
"""
div_last_refresh_strbase = "<b>Last refresh</b><br>{}"
div_last_data_strbase = "<b>Last data poll</b><br>{}"

div_proc_hits = Div( text=div_proc_hits_strbase, width=120, height=120, style = {"font-size": "120%"}, align='center')
div_last_refresh = Div( text=div_last_refresh_strbase.format('never'), width=260, height=30, align='center')
div_last_data = Div( text=div_last_data_strbase.format('never'), width=260, height=30, align='center')






# CREATE PAGE
doc = curdoc()
doc.add_periodic_callback(update_graphs, 500)

graphs_tab1 = layout([ div_proc_hits, Div(text='<br><br>'),  # table with processed hit counter
                       #graph_type_tdc,                       # select type of plot  (DISMISSED)
                       [ column(Div(text="Processed hits (cleansed) per chamber", style = notsobig), hist_TDC_active, sizing_mode="stretch_width"),
                         column(Div(text="Active TDC with scintillator signal", style = notsobig), hist_TDC_scint, sizing_mode="stretch_width")
                       ],
                       Div(text="active TDC in orbits per detector", style = notsobig, sizing_mode="stretch_width"), plot_TDC_orbits,
                       Div(text="Drift times per detector", style = notsobig, sizing_mode="stretch_width"),
                       [ hist_drift0, hist_drift1, hist_drift2, hist_drift3 ],
                     ], sizing_mode="stretch_width")
panel_tab1 = Panel(child=graphs_tab1, title="Data quality")

graphs_tab2 = layout([ pause_cbox,
                       Div(text="Event stream", style = notsobig, sizing_mode="stretch_width"),
                       plot_TDC_history
                     ], sizing_mode="stretch_width")
panel_tab2 = Panel(child=graphs_tab2, title="Monitor")

lyt = grid([ head_text,
             row( column(pause_bt, div_last_refresh, div_last_data, width= 260, sizing_mode="fixed"),
                  Tabs(tabs=[ panel_tab1, panel_tab2 ], sizing_mode="stretch_width") ,
                  sizing_mode="stretch_width"),
           ], sizing_mode='stretch_width')

doc.add_root(lyt)
doc.title = "COSMO dashboard"

# TODO   set server https://docs.bokeh.org/en/latest/docs/user_guide/server.html