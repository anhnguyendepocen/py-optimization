class LivestreamData():
  # import all necessary packages, modules, libraries
    import math
    import time                      # time tracking
    from time import sleep           # making loops "sleep" (making them wait)
    import numpy as np
    import matplotlib.pyplot as plt  # plotting
    import matplotlib as mpl         # plotting

    import heatflow_graph as hfg
    set_dark_plots = hfg.set_dark_plots
    init_graph = hfg.init_graph
    graphing_step = hfg.graphing_step
    graphing_process = hfg.graphing_process

    import heatflow_data as hfd
    init_data = hfd.init_data
    data_collection_step = hfd.data_collection_step
    data_collector = hfd.data_collector
    finalize_data = hfd.finalize_data

    import heatflow_controls as hfc
    init_controls = hfc.init_controls
    control_listener = hfc.control_listener
    on_button_clicked = hfc.on_button_clicked


    def __call__( self,
                  dark_plots = True,          # True/False = Dark/Light plot theme
                  _titlefont = 18,            # plot title font size
                  _labelfont = 14,            # axis-label font size
                  _tickfont  = 12,            # size of the tickmark labels
                  _xwidth    = 30,            # how many seconds of data to show on x-axis at any moment?
                  figsize    = ('default', 'default'),         # fig size is dynamically set by default: (int, int)
                  ):

        self._xwidth = _xwidth

        if dark_plots == True: self.set_dark_plots()
        self.init_controls(_titlefont, _labelfont, _tickfont)  # initialize all user-controls
        self.init_data()    # initialize variables for storing experiment data
        self.init_graph(figsize)   # setup graphs and display interface

        import threading
        t1 = threading.Thread(target=self.control_listener) # CONTROL LISTENER THREAD
        t1.start()
        self.sleep(0.1)

        t2 = threading.Thread(target=self.data_collector) # DATA GATHERING THREAD
        t2.start()
        self.sleep(0.1)

        t3 = threading.Thread(target=self.graphing_process) # GRAPHING & DATA COLLECTION THREAD
        t3.start()









    """
    THE FOLLOWING INITIAL VALUES CAN BE SET IN THE FUNCTION CALL. THESE ARE THE DEFAULT VALUES:

      dark_plots    = True,       # True/False = Dark/Light plot theme
      _titlefont = 18,            # plot title font size
      _labelfont = 14,            # axis-label font size
      _tickfont  = 12,            # size of the tickmark labels
      _xwidth     = 30,           # how many seconds of data to show on x-axis at any moment?
      figsize    = ('default','default'),             # fig size is dynamically set by default: (int, int)
      datasrc  = ['src1', 'src2', 'src3', 'src4'],    # which input sources to listen to


    ---------------------------------------------------------------------------

    EXAMPLE 1: Use all default values.
    ----------
      ex1 = LivestreamData()


    EXAMPLE 2: Change how many seconds of data to show on x-axis, turn off dark plot theme, use COM3 port..
    ----------
      ex2 = LivestreamData(dark_plots=False, _xwidth=60)


    EXAMPLE 3:  **Important** Retrieving your data.
    ----------
      ex3 = LivestreamData()

      # Once you've hit the "End Process" button you can retrieve your data.
      # Create a new cell and call the `data` property on your LivestreamData variable:

      fresh_data = ex3.data


    EXAMPLE 4: Choose which data sources to observe.
    ----------

      ex1 = LivestreamData(datasrc = ['src1', 'src2', 'src3', 'src4'])


    IMPORTANT:
    ----------
      When youre done collecting data for a particular run, HIT THE END PROCESS BUTTON.

    ---------------------------------------------------------------------------
    """