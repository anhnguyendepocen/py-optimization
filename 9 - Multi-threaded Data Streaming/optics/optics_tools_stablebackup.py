class CollectOpticsData():
    
    """    
    
    THE FOLLOWING INITIAL VALUES CAN BE SET IN THE FUNCTION CALL. THESE ARE THE DEFAULT VALUES:

      FPGA_port_num = 2,          # which com port to listen to
      dark_plots    = True,       # True/False = Dark/Light plot theme
      _titlefont = 18,            # plot title font size
      _labelfont = 14,            # axis-label font size
      _tickfont  = 12,            # size of the tickmark labels
      _smooth    = False,         # option to smooth the graph with b-spline interpolation
      _markers   = False,         # add data point markers to line graph when smoothing is off
      _sharex    = False,         # option to share x-axis labels between graphs
      _timestep  = 0.1,           # how long to wait between each recorded timestep
      _xwidth     = 30,           # how many seconds of data to show on x-axis at any moment?
      figsize    = ('default',    # fig size is dynamically set by default: (int, int)
                    'default'), 
      detectors  = ['A','B',      # which detector data to record & graph
                    'A_','B_', 
                    'C1','C2',
                    'C3','C4'],  ):
    
    ---------------------------------------------------------------------------
    
    EXAMPLE 1: Use all default values.
    ----------
      ex1 = CollectOpticsData()
    
    
    EXAMPLE 2: Change how many seconds of data to show on x-axis, turn off dark plot theme, use COM3 port..
    ----------
      ex2 = CollectOpticsData(FPGA_port_num=3, dark_plots=False, _xwidth=60)
      
      
    EXAMPLE 3:  **Important** Retrieving your data.
    ----------
      ex3 = CollectOpticsData()
      
      # Once you've hit the "End Process" button you can retrieve your data. 
      # Create a new cell and call the `data` property on your OpticsDataCollection variable:
      
      fresh_data = ex3.data
      
      
    EXAMPLE 4: Choose which detectors to observe.
    ----------
      # The FPGA has 8 channels that send out data. Set this list based on which channels your experiment is using.
      
      ex1 = CollectOpticsData(detectors = ['A', 'B', 'B_', 'C1'])
      
    
    IMPORTANT:
    ----------
      When youre done collecting data for a particular run, HIT THE END PROCESS BUTTON.
    
    ---------------------------------------------------------------------------
    """
    
    # 0. import all necessary packages, modules, libraries
    import serial as ps              # open and read serial port data
    import struct                    # decode data from FPGA
    import time                      # time tracking
    from time import sleep           # making loops "sleep" (making them wait)
    import numpy as np               # matrices / arrays for data storing
    import matplotlib.pyplot as plt  # plotting
    import matplotlib as mpl         # plotting
    import scipy.interpolate as interpolate # BSpline (smooth curve) interpolation

    
    #mpl.rcParams['figure.dpi']= 72
    #mpl.rc("savefig", dpi=dpi)
    
    
    # Make plots dark
    def set_dark_plots(self):
        try:
            from jupyterthemes import jtplot # make plots pretty
            jtplot.style()                   # make plots pretty
        except: None
    
    # 1. Setup user controls
    def init_controls(self, _TITLEFONT, _LABELFONT, _TICKFONT, _SMOOTH, _MARKERS, _SHAREX, _TIMESTEP):
        import ipywidgets as widgets     # user control GUI tools
        from ipywidgets import Layout, Button, Box, VBox, ToggleButton   # user control GUI tools


        # (FIRST TAB) CONTROL BUTTONS
        self.options = [('Save Snapshot', 'info', 'camera'), 
                        ('Collect Data', 'success', 'play'),
                        ('End Process', 'danger', 'stop')]

        self.controls = [ ToggleButton( layout       = Layout( width='100%'),
                                        value        = False,
                                        description  = option[0], 
                                        button_style = option[1],
                                        icon         = option[2] ) for option in self.options ]

        self.control_box_layout = Layout( display     = 'flex',
                                          flex_flow   = 'row',
                                          align_items = 'stretch',
                                          border      = 'none',
                                          width       = 'auto' )

        self.control_box = Box( children = self.controls, 
                                layout   = self.control_box_layout )



        # (SECOND TAB) GRAPHING OPTIONS
        self.titlefont_size = widgets.BoundedIntText( value  = _TITLEFONT,
                                                 min=0,  max=42,  step=1,
                                                 description = 'Title Font Size:',
                                                 disabled    = False )
        self.labelfont_size = widgets.BoundedIntText( value  = _LABELFONT,
                                                 min=0,  max=36,  step=1,
                                                 description = 'Axis Label Size:',
                                                 disabled    = False )
        self.axistick_size  = widgets.BoundedIntText( value  = _TICKFONT,
                                                 min=0,  max=22,  step=1,
                                                 description = 'Axis Tick Size:',
                                                 disabled    = False )
        self.button_layout = Layout( width = 'auto' )
        self.smooth_button = widgets.ToggleButton(
                            value        = _SMOOTH,
                            description  = 'Smooth Curve',
                            disabled     = False,
                            button_style = 'primary',
                            tooltip      = 'Toggle to show Smooth Curve Interpolation',
                            icon         = 'paint-brush',
                            layout       = self.button_layout )
        self.marker_button = widgets.ToggleButton(
                            value        = _MARKERS,
                            description  = 'Markers',
                            disabled     = False,
                            button_style = 'primary',
                            tooltip      = 'Toggle to show Datapoint Markers (smooth curve interpolation must be disabled)',
                            icon         = 'map-marker',
                            layout       = self.button_layout )

        self.sharex_button = widgets.ToggleButton(
                            value        = _SHAREX,
                            description  = 'Share x-Axis Labels',
                            disabled     = False,
                            button_style = 'primary',
                            tooltip      = 'Toggle to share x-axis labels',
                            icon         = 'tag',
                            layout       = self.button_layout )
        self.timestep_slider = widgets.FloatSlider(
                              value= _TIMESTEP,
                              min=0, max=0.5, step=0.05,
                              description       = 'Timestep (sec):',
                              disabled          = False,
                              continuous_update = False,
                              readout_format    = '.1c',)
        # SECOND TAB CONTENT & LAYOUT
        self.graph_options0 = [self.titlefont_size,    # TOP ROW OF SECOND TAB (CONTENT)
                               self.labelfont_size, 
                               self.axistick_size]
        
        self.graph_options1 = [self.timestep_slider,   # BOTTOM ROW OF SECOND TAB (CONTENT)
                               self.smooth_button, 
                               self.marker_button, 
                               self.sharex_button]
        self.graph_options_layout = Layout(display       = 'flex',  # SECON TAB LAYOUT OPTIONS
                                           flex_flow     = 'row',
                                           align_items   = 'stretch',
                                           border        = 'none',
                                           width         = 'auto')
        self.graph_ops_box0 = Box( children = self.graph_options0,     # TOP ROW LAYOUT APPLIED
                                   layout   = self.graph_options_layout )
        
        self.graph_ops_box1 = Box( children = self.graph_options1,     # BOTTOM ROW LAYOUT APPLIED
                                   layout   = self.graph_options_layout ) 
        self.graph_options_vbox = VBox( [ self.graph_ops_box0,       # STACK TOP AND BOTTOM ROWS
                                          self.graph_ops_box1 ] )    # INSIDE OF A SINGLE BOX
        # INITIALIZE AND CONSTRUCT TABS
        self.children = [("Controls", self.control_box), 
                         ("Graph Options", self.graph_options_vbox)]
        self.tab = widgets.Tab()
        self.tab.children = [i[1] for i in self.children]
        for i, val in enumerate(self.children):
            self.tab.set_title(i, val[0])
            
        # dictionary for storing values of each control/option for the graph
        self.opts = {
            # CONTROLS (TAB 1)
            self.controls[0].description: self.controls[0].value, # snapshot button
            self.controls[1].description: self.controls[1].value, # play/pause button
            self.controls[2].description: self.controls[2].value, # stop button
            # GRAPH OPTIONS (TAB2 TOP ROW)
            self.titlefont_size.description:  self.titlefont_size.value,
            self.labelfont_size.description:  self.labelfont_size.value,
            self.axistick_size.description:   self.axistick_size.value,
            # GRAPH OPTIONS (TAB2 BOTTOM ROW)
            self.smooth_button.description:   self.smooth_button.value,
            self.marker_button.description:   self.marker_button.value,
            self.sharex_button.description:   self.sharex_button.value,
            self.timestep_slider.description: self.timestep_slider.value}

        # list helps to conveniently iterate application of event listener to each control
        self.control_reference = [i for i in self.controls]+[self.titlefont_size,
                                                             self.labelfont_size,
                                                             self.axistick_size,
                                                             self.smooth_button,
                                                             self.marker_button,
                                                             self.sharex_button,
                                                             self.timestep_slider]
    
        # Display the user controls
        display(self.tab)
    
    # Setup variable for storing all incoming data
    def init_data(self, detectors, width):
        np = self.np
        
        self.data = {}
        for n in detectors: 
            self.data[n] = np.zeros(width)
        self.data['time'] = np.zeros(width)
        
        # initial timestamp for tracking time
        self.tstart = self.time.time() 
        
        
    # Set up and show the plot
    def init_graph(self, detectors, figsize, sharex, markers, smooth):
        plt = self.plt
        plt.ion() # for real-time graphing
        data = self.data
        
        if figsize == ('default','default'): # calculate default figure size for the plot
            figsize = (8,(2.5*len(detectors)))      # calculate default figure size for the plot
        
        self.ax=[]     # variable that holds each set of axes (matplotlib axes objects)
        self.fig, self.ax[0:len(detectors)] = plt.subplots(len(detectors), # generate the figure and the axes objects
                                                           1,
                                                           sharex=sharex, 
                                                           figsize=figsize)
        
        self.fig.canvas.draw() # initial drawing of canvas
        
        # generate matplotlib line objects for graphing incoming data and format graphs
        self.line=[] # list for containing each curve (matplotlib line object)
        self.axbg=[] # list for containing caching each plot background (performance boost)
        for n, i in enumerate(detectors):

            #self.ax[n].grid(False) # disable grid in plot background
            
            # add markers if smoothing is turned off and markers are turned on
            if markers==True and smooth==False: 
                self.line.append( self.ax[n].plot(data['time'], 
                                  self.data[i], 
                                  marker='o', 
                                  markersize=4)[0] )
            else:
                self.line.append(self.ax[n].plot( data['time'], 
                                                 self.data[i],
                                                 linewidth=1,
                                                 rasterized=True,
                                                 antialiased=True)[0] )
            
            
            self.ax[n].set_title("Detector {}: {}".format(detectors[n], 0),
                                 **{'size': self.titlefont_size.value})  # add titles
            self.ax[n].set_xlabel("Time (seconds)", 
                                  **{'size': self.labelfont_size.value}) # add x-axis label
            self.plt.setp(self.ax[n].get_xticklabels(), 
                          fontsize=self.axistick_size.value)   # set x-axis tickmark font size
            self.plt.setp(self.ax[n].get_yticklabels(), 
                          fontsize=self.axistick_size.value)   # set y-axis tickmark font size

            # set y-axis labels for coincidence and photon counts
            if detectors[n][0]=='C': 
                self.ax[n].set_ylabel("Coincidence Count", 
                                      **{'size': self.labelfont_size.value})
            else: 
                self.ax[n].set_ylabel("Photon Count", 
                                      **{'size': self.labelfont_size.value})
            
            # store initial plot backgrounds for blitting process (performance boost!)
            self.axbg.append(self.fig.canvas.copy_from_bbox(self.ax[n].bbox))
            
        plt.subplots_adjust(right=1, top=0.95, bottom=0.15, wspace=0, hspace=0.75) # give each subplot nice margins        
        
        
        
    def init_serial_port(self, FPGA_port_num):
        # Define the serial port
        ps = self.ps
        try:
            self.FPGA = ps.Serial('COM{}'.format(FPGA_port_num),
                                 baudrate=19200,
                                 timeout=2.0,
                                 parity=ps.PARITY_NONE,
                                 stopbits=ps.STOPBITS_ONE,
                                 bytesize=ps.EIGHTBITS)
        except:
            print("""
It appears as if COM{} (FPGA) was left open by another process, or that it simply does not exist.
                  
If you are in Jupyter Notebook try restarting the kernel (Toolbar > Kernel (menu) > Restart) and ensure that no other programs are attempting to read serial port data on COM{}.
                  """.format(FPGA_port_num, FPGA_port_num))
                
        # Ensure that serial port is open
        if self.FPGA.isOpen() == False:
            print("OPENING FPGA port.")
            self.FPGA.open()

    
    
    
    # Actions to perform on each step of data collection & graphing
    t_new = 0
    t_old = 0
    def graphing_step(self, key, detectors, data, fig, ax, line, width):
            # Read in data
        rawdata = self.FPGA.read(41)

        # Make sure we're getting whole strings from the FPGA
            # check that the final byte is terminal character 255
            # make sure the line is 41 bytes long
        if rawdata[-1]==255 and  len(rawdata)==41:

            # Append new timestamps
            dt = self.time.time() - self.tstart
            data['time'] = self.np.append(data['time'], [dt])

            # Update our DATA and our graphs with new incoming data
            for n, i in enumerate(key): # we use `key` to ensure that we iterate over the incoming
                                        # byte strings correctly because the FPGA returns data for
                                        # all possible detectors regardless of which ones we are
                                        # interested in. `key` contains the names of ALL of the
                                        # detectors, whereas the 'detectors' variable contains
                                        # names of the particular detectors we are interested in
            
                # pause process if saving snapshot so renderer doesn't become confused  
                while self.fig.canvas.is_saving():  sleep(1)
                    
                # Save new data points, update the plot title, and plot axes limits
                if i in detectors:
                    # Save new data points
                    data[i] = self.np.append(data[i], [self.struct.unpack('L', rawdata[(n*5) : 4+(n*5)])[0]] ) 
                    n = detectors.index(i) # switch from the `key` index to `detectors` index in order
                                           # to access our graph objects' corresponding indices

                    # Update axes and titles
                    ax[n].set_xlim([data['time'][-1]-width,    # update x-axes limits
                                    data['time'][-1]]) 
                    if data[i][-1:] > ax[n].get_ylim()[1]: # update y-axis limits if detector is generating data
                        ax[n].set_ylim([0, data[i][-1:]*1.2]) 

                    ax[n].set_title("Detector {}:    [{}]".format(i, data[i][-1]), # update plot title with count 
                                    **{'size': self.titlefont_size.value})                  

                    ax[n].set_xlabel(ax[n].get_xlabel(), **{'size': self.labelfont_size.value}) # update x-axis label size
                    ax[n].set_ylabel(ax[n].get_ylabel(), **{'size': self.labelfont_size.value})
                    self.plt.setp(ax[n].get_xticklabels(), fontsize=self.axistick_size.value)   # update x-axis tickmark font size
                    self.plt.setp(ax[n].get_yticklabels(), fontsize=self.axistick_size.value)   # update y-axis tickmark font size
                    
                    # Update the curves / lines
                    line[n].set_data(data['time'][width:], # update x-data
                                     data[i][width:])      # update y-data
    
            # RENDER WITH BLIT
            for n in range(len(detectors)):
                self.fig.canvas.restore_region(self.axbg[n])
                self.ax[n].draw_artist(self.line[n])
                self.fig.canvas.blit(self.ax[n].bbox)
                self.plt.pause(0.01)
            
            
            # Draw the new data (WITHOUT BLIT)
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #self.sleep(self.timestep_slider.value)
        else: 
            print("Just reeived malformed data. Problem has been handled.")
            self.FPGA.close()
            self.sleep(0.01)
            self.FPGA.open()
            pass # if we didnt get a whole, well-formed string from the FPGA skip this iteration     

        
        
    def on_button_clicked(self, change): 
        plt = self.plt
        
        self.opts[change['owner'].description] = change['new']
        # play/pause button
        if change['owner'].description == self.controls[1].description and change['new'] == False:
            self.controls[1].button_style = 'success'
            self.controls[1].icon         = 'play'
            self.controls[1].description  = 'Collect Data'
            self.controls[0].disabled     = False  # only enable snapshot while graph is paused (for stability)
        elif change['owner'].description == self.controls[1].description and change['new'] == True:
            self.controls[1].button_style = 'warning'
            self.controls[1].icon         = 'pause'
            self.controls[1].description  = 'Pause Collection'
            self.controls[0].disabled     = True  # disable snapshot while graph is running (for stability)
        
        # snapshot (camera) button
        elif change['owner'].description == self.controls[0].description and change['new'] == True:
            plt.savefig('optics_lab_{}.png'.format(str(self.time.time()).replace(".","")))
            self.controls[0].value = False
                
            
    def control_listener(self):
        [i.observe(self.on_button_clicked, 'value') for i in self.control_reference]         

    
    def graphing_process(self):        
        detectors, _xwidth = self.detectors, self._xwidth
        
        while True:
            while self.controls[2].value == False: # while the "end process" button has not been pushed
                if self.controls[1].value == True: # while data collection is NOT paused
                    self.graphing_step(self.key, detectors, self.data, self.fig, self.ax, self.line, self._xwidth)
                
                else:  # while data collection IS paused
                    self.sleep(0.1)
            else:
                for i in self.control_reference:
                    i.disabled=True  # disable all controls once the proess has been stopped
                self.FPGA.close()    # close the COM port

                # perform final data preparation
                for n, i in enumerate(detectors): # remove most recent counts from final plot title
                    self.ax[n].set_title("Detector {}:".format(i), {'size': self.titlefont_size.value})
                for n in detectors+['time']: # drop first 200 placeholder values
                    self.data[n] = self.np.delete(self.data[n], [i for i in range(_xwidth)])

                break  # break out of the loops & terminate the thread
            

    def __call__( self, 
                  FPGA_port_num = 2,          # which com port to listen to
                  dark_plots    = True,       # True/False = Dark/Light plot theme
                  _titlefont = 18,            # plot title font size
                  _labelfont = 14,            # axis-label font size
                  _tickfont  = 12,            # size of the tickmark labels
                  _smooth    = False,         # option to smooth the graph with b-spline interpolation
                  _markers   = False,         # add data point markers to line graph when smoothing is off
                  _sharex    = False,         # option to share x-axis labels between graphs
                  _timestep  = 0.1,           # how long to wait between each recorded timestep
                  _xwidth    = 30,            # how many seconds of data to show on x-axis at any moment?
                  figsize    = ('default',    # fig size is dynamically set by default: (int, int)
                                'default'), 
                  detectors  = ['A','B',      # which detector data to record & graph
                                'A_','B_', 
                                'C1','C2',
                                'C3','C4'],  ):
        
        self.key = ['A','B','A_','B_', 'C1','C2','C3','C4'] # list of all possible detectors
        self.detectors, self._xwidth = detectors, _xwidth
        
        if dark_plots == True: self.set_dark_plots()
        self.init_controls(_titlefont, _labelfont, _tickfont, _smooth, 
                           _markers, _sharex, _timestep)  # initialize all user-control objects (buttons etc.) and their values
        self.init_data(detectors, _xwidth)                # initialize variables for storing experiment data
        self.init_graph(detectors, figsize, _sharex, _markers, _smooth) # setup graphs and display interface
        self.init_serial_port(FPGA_port_num)              # initialize FPGA serial port connection
        
        import threading
        t1 = threading.Thread(target=self.control_listener) # CONTROL LISTENER THREAD
        t1.start()
        self.sleep(0.1)

        t2 = threading.Thread(target=self.graphing_process) # GRAPHING & DATA COLLECTION THREAD
        t2.start()  

def make_csv(data, filename="optics_data_CURRENTTIME"):
    """
    This function takes a Python dictionary and outputs a CSV file containing the data.
    
    Optionally you can give the file a custom name, otherwise a name is automatically
    formatted.
    
    
    Example 1:
    ---------
      run1 = CollectOpticsData()
      my_data = run1.data
      make_csv(my_data)   # filename is automatically generated
      
      
    Example 2:
    ---------
      run2 = CollectOpticsData()
      make_csv(run2.data, "Best_Filename_Ever")   # custom file name
    
    """
    import pandas as pd
    import time
    
    if filename=="optics_data_CURRENTTIME":
        cur_time = str(time.time()).replace(".","")
        filename = "optics_data_{}".format(cur_time)

    pd.DataFrame(data).to_csv('{}.csv'.format(filename), index=False)

def test_com_ports(ports_to_test=[1,2,3,4]):
    
    """
    This function takes a list of integers as its argument.
    
    For example, if you want to test COM ports 1 - 4:
    
      test_com_ports([1,2,3,4])
    
    """

    import serial as ps
    for i in ports_to_test:
        try:
            ser = ps.Serial('COM{}'.format(str(i)),
                            baudrate=19200,timeout=2.0,
                            parity=ps.PARITY_NONE, 
                            stopbits=ps.STOPBITS_ONE, 
                            bytesize=ps.EIGHTBITS)  
            data = ser.read(41)
            if len(data)>0:
                print("**COM{} IS CONNECTED to something and IS receiving data. \n\n".format(str(i)))
            else: 
                print("COM{} is NOT receiving data. \n\n".format(str(i)))
        except: print("COM{} definitely isn't receiving any data and might not exist. \n\n".format(str(i)))
    try: ser.close()
    except: None