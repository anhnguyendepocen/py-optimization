# Setup user controls
def init_controls(self, _TITLEFONT, _LABELFONT, _TICKFONT):
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

    # SECOND TAB CONTENT & LAYOUT
    self.graph_options0 = [self.titlefont_size,    # TOP ROW OF SECOND TAB (CONTENT)
                           self.labelfont_size,
                           self.axistick_size]

    self.graph_options_layout = Layout(display       = 'flex',  # SECON TAB LAYOUT OPTIONS
                                       flex_flow     = 'row',
                                       align_items   = 'stretch',
                                       border        = 'none',
                                       width         = 'auto')
    self.graph_ops_box0 = Box( children = self.graph_options0,     # TOP ROW LAYOUT APPLIED
                               layout   = self.graph_options_layout )

    self.graph_options_vbox = VBox( [ self.graph_ops_box0,])       # STACK ROWS INSIDE OF A SINGLE BOX
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
        self.axistick_size.description:   self.axistick_size.value,}

    # list helps to conveniently iterate application of event listener to each control
    self.control_reference = [i for i in self.controls]+[self.titlefont_size,
                                                         self.labelfont_size,
                                                         self.axistick_size,]

    # Display the user controls
    display(self.tab)



def control_listener(self):
    [i.observe(self.on_button_clicked, 'value') for i in self.control_reference]


def on_button_clicked(self, change):
    plt = self.plt

    self.opts[change['owner'].description] = change['new']
    # play/pause button
    if change['owner'].description == self.controls[1].description and change['new'] == False:
        self.controls[1].button_style = 'success'
        self.controls[1].icon         = 'play'
        self.controls[1].description  = 'Collect Data'
        self.controls[0].disabled     = False  # only enable snapshot if paused (stability)
    elif change['owner'].description == self.controls[1].description and change['new'] == True:
        self.controls[1].button_style = 'warning'
        self.controls[1].icon         = 'pause'
        self.controls[1].description  = 'Pause Collection'
        self.controls[0].disabled     = True

    # snapshot (camera) button
    elif change['owner'].description == self.controls[0].description and change['new'] == True:
        plt.savefig('datastream_{}.png'.format(str(self.time.time()).replace(".","")))
        self.controls[0].value = False



