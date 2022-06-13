#!/usr/bin/env python3

#########################################################
#   MAPD module B // University of Padua, AY 2021/22
#   Group 2202 / Barone Nagaro Ninni Valentini
#
#  This is the monitor dashboard for the cosmic rays
#  telescope, reading live data from Kafka topic.
#
#  launch with    bokeh serve --show bin/mydash/
#--------------------------------------------------------
#  coder: Barone Francesco, last edit: 12 jun 2022
#  Open Access licence
#--------------------------------------------------------

from kafka import KafkaConsumer
from datetime import datetime
from threading import Thread
from queue import Queue
import json
import numpy as np

from bokeh.layouts import column, row, layout, grid
from bokeh.models import ColumnDataSource, Div, Paragraph, Range1d, Slider
from bokeh.plotting import curdoc, figure

from bokeh.server.server import Server
from bokeh.models import Button, Dropdown, Label, Span, RadioButtonGroup
from bokeh.models.widgets import Tabs, Panel


KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092',]
TOPIC='cosmo-results'

chamber_colors = ["#ff2b24", "#ffcc00", "#00cc33", "#004ecc"]


class mykafka_consumer(Thread):
    
    def __init__(self):
        Thread.__init__(self) 
        
        # setup kafka consumer        
        consumer = KafkaConsumer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                 consumer_timeout_ms=10000
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
        self.button = None
        self.last_timestamp = 'never'
        print('kafka setup!')
        
    def set_button_obj(self, bt):
        self.button = bt
    
    def toggle_semaphore(self):
        self.semaphore = not self.semaphore
        if self.button is not None:
            if self.semaphore:
                self.button.button_type='success'
            else: self.button.button_type='warning'
        return self.semaphore
    
    def run(self):
        for msg in self.kc:
            if self.queue.full():
                print(' ERROR: Queue is full, should you be faster?')
                break
            self.last_datetime = datetime.now()
            self.last_timestamp = self.last_datetime.strftime("%H:%M:%S %d-%m-%Y")
            if self.semaphore:
                self.queue.put(msg)
                #print('received msg')
            else:
                pass
                #print('received msg - plot is paused')

            
## break down the message into its main components
#for message in consumer:
#    print ("%d:%d [%s] k=%s v=%s" % (message.partition,
#                          message.offset,
#                          datetime.fromtimestamp(message.timestamp/1000).time(),
#                          message.key,
#                          message.value))


# start simulator process
kc = mykafka_consumer()
kc.daemon = True # let the main thread exit even though the workers are blocking
kc.start()

print('Kafka consumer online!')



###########################
# use BOKEH WEB INTERFACE #
###########################

def update_graphs():  # read data from buffer & update plotsz
    global kc
    
    # update timestamp
    div_last_data.text = div_last_data_strbase.format( kc.last_timestamp ) # update data timestamp
    
    if kc.queue.empty():
        #print('Queue empty, not updating')
        return 1
    
    dd = json.loads( kc.queue.get().value )
    
    # update if new data is provided
    cleansed = dd['cleansed']
    div_proc_hits.text = div_proc_hits_strbase % (cleansed[0], cleansed[1], cleansed[2], cleansed[3], dd['tot_hits'])
    div_last_refresh.text = div_last_refresh_strbase.format( datetime.now().strftime("%H:%M:%S %d-%m-%Y") )
    cds_tdc_history.stream( dict( t=[kc.last_datetime], ch0=[cleansed[0]], ch1=[cleansed[1]], 
                                  ch2=[cleansed[2]], ch3=[cleansed[3]])
                          )
    
    # update plots data
    active_orb = dd['active_orbit']
    cds_tdc_orb.data =  {'x': np.arange(len(active_orb[0])), 'ch0': active_orb[0], 'ch1': active_orb[1],
                  'ch2': active_orb[2], 'ch3': active_orb[3]}
    
    active_tdc = dd['active_tdc']
    cds_tdc_active.data =  {'x': np.arange(64), 'ch0': active_tdc[0], 'ch1': active_tdc[1],
                  'ch2': active_tdc[2], 'ch3': active_tdc[3]}
    
    active_sci = dd['active_scint']
    cds_tdc_scint.data =  {'x': np.arange(64), 'ch0': active_sci[0], 'ch1': active_sci[1],
                  'ch2': active_sci[2], 'ch3': active_sci[3]}
    
    dtimes = dd['driftimes']
    edges = np.arange(0,1.1,0.1)
    hist0, _ = np.histogram(dtimes[0], bins=edges)
    hist1, _ = np.histogram(dtimes[1], bins=edges)
    hist2, _ = np.histogram(dtimes[2], bins=edges)
    hist3, _ = np.histogram(dtimes[3], bins=edges)
    cds_drifts.data = { 'ch0': hist0, 'ch1': hist1, 'ch2': hist2, 'ch3': hist3,
                       'edgel':edges[:-1], 'edger':edges[1:]}
    return 0

    
###############
# bokeh plots #
###############

cds_tdc_orb = ColumnDataSource( {'x':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[]} )
cds_tdc_active = ColumnDataSource( {'x':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[]} )
cds_tdc_scint = ColumnDataSource( {'x':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[]} )
cds_drifts = ColumnDataSource( { 'ch0': [], 'ch1': [], 'ch2': [], 'ch3': [], 'edgel':[], 'edger':[]} )
cds_tdc_history = ColumnDataSource( {'t':[], 'ch0':[], 'ch1':[], 'ch2':[], 'ch3':[]} )

# active TDC vs orbits for each detector
plot_TDC_orbits = figure( #width=900,
                         sizing_mode="stretch_width",
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
hist_drift0 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch0')
hist_drift0.quad(source=cds_drifts, top="ch0", bottom=0, left="edgel", right="edger")
hist_drift1 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch1')
hist_drift1.quad(source=cds_drifts, top="ch1", bottom=0, left="edgel", right="edger")
hist_drift2 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch2')
hist_drift2.quad(source=cds_drifts, top="ch2", bottom=0, left="edgel", right="edger")
hist_drift3 = figure(plot_width=250,  plot_height=320, tools="pan,reset,save", title='Ch3')
hist_drift3.quad(source=cds_drifts, top="ch3", bottom=0, left="edgel", right="edger")

plot_TDC_history = figure( 
        plot_width=900, plot_height=320, tools="pan,reset,save",
        x_axis_type='datetime', sizing_mode="stretch_width")
plot_TDC_history.xaxis.axis_label = "time"
plot_TDC_history.yaxis.axis_label = "TDC counts"
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch0", line_width = 2, line_color = chamber_colors[0])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch1", line_width = 2, line_color = chamber_colors[1])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch2", line_width = 2, line_color = chamber_colors[2])
plot_TDC_history.line(source=cds_tdc_history, x="t", y="ch3", line_width = 2, line_color = chamber_colors[3])

##########
#  misc  #
##########

# styles
notsobig = {"font-size": "120%", "font-weight": "bold"}
big = {"font-size": "150%", "font-weight": "bold"}
bigger = {"font-size": "200%", "font-weight": "bold"}

# header & footer
head_text = [ Div(text=r"dashboard ver 0.0") ]
footer = Div( text="bokeh footer", width=1600, height=20, align='center')

# button to start/stop simulation
bt = Button(label='pause', button_type="success", width=100,  sizing_mode="fixed", align='center')
bt.on_click(kc.toggle_semaphore) # TODO
kc.set_button_obj(bt) # link button to data reader obj

# graph selector
graph_type_tdc_labels = ["Histogram", "Heatmap"]
graph_type_tdc = RadioButtonGroup(labels=graph_type_tdc_labels, active=0)

# dropdown
menu = [("Item 1", "item_1"), ("Item 2", "item_2"), None, ("Item 3", "item_3")]
dropdown = Dropdown(label="Dropdown button", button_type="warning", menu=menu)
#dropdown.js_on_event("menu_item_click", CustomJS(code="console.log('dropdown: ' + this.item, this.toString())"))



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
                       graph_type_tdc,                       # select type of plot
                       [ column(Div(text="Processed hits (cleansed) per chamber", style = notsobig), hist_TDC_active, sizing_mode="stretch_width"),
                         column(Div(text="Active TDC with scintillator signal", style = notsobig), hist_TDC_scint, sizing_mode="stretch_width")
                       ],
                       Div(text="active TDC in orbits per detector", style = notsobig, sizing_mode="stretch_width"), plot_TDC_orbits,
                       Div(text="Drift times per detector", style = notsobig, sizing_mode="stretch_width"),
                       [ hist_drift0, hist_drift1, hist_drift2, hist_drift3 ],
                     ], sizing_mode="stretch_width")
panel_tab1 = Panel(child=graphs_tab1, title="Live")

graphs_tab2 = layout([ Div(text="TDC hits", style = notsobig, sizing_mode="stretch_width"),
                       plot_TDC_history
                     ], sizing_mode="stretch_width")
panel_tab2 = Panel(child=graphs_tab2, title="History")

lyt = grid([ head_text,
             row( column(bt, div_last_refresh, div_last_data, width= 260, sizing_mode="fixed"),
                  Tabs(tabs=[ panel_tab1, panel_tab2 ], sizing_mode="stretch_width") ,
                  sizing_mode="stretch_width"),
             #footer
           ], sizing_mode='stretch_width')

doc.add_root(lyt)

# TODO   set server https://docs.bokeh.org/en/latest/docs/user_guide/server.html
#server = Server({'/': doc}, num_procs=4)
#server.start()
#
#if __name__ == '__main__':
#    print('Opening Bokeh application on http://localhost:5006/')
#
#    server.io_loop.add_callback(server.show, "/")
#    server.io_loop.start()