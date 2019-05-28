# Make plots dark
def set_dark_plots(self):
    try:
        from jupyterthemes import jtplot # make plots pretty
        jtplot.style()                   # make plots pretty
    except: None

# Set up and show the plot
def init_graph(self, figsize):
    self.plt.ion() # for real-time plotting

    if figsize == ('default','default'):     # calculate default figure size for the plot
        figsize = (8,(3*len(self.datasrc)))  # calculate default figure size for the plot

    self.ax=[]     # variable that holds each set of axes (matplotlib axes objects)
    self.fig, self.ax[0:len(self.datasrc)] = self.plt.subplots(len(self.datasrc), # generate the figure and the axes objects
                                                               1,
                                                               sharex=False,
                                                               figsize=figsize)

    self.fig.canvas.draw() # initial drawing of canvas

    # generate matplotlib line objects for graphing incoming data and format graphs
    self.line=[] # list for containing each curve (matplotlib line object)
    self.axbg=[] # list for containing caching each plot background (performance boost)
    for n, i in enumerate(self.datasrc):
        self.line.append(self.ax[n].plot( self.data['time'],
                                          self.data[i],
                                          linewidth=1,
                                          rasterized=True,
                                          antialiased=True)[0] )

        self.ax[n].set_title("Data Source {}: {}".format(self.datasrc[n], 0),
                             **{'size': self.titlefont_size.value})  # add titles
        self.ax[n].set_xlabel("Time (seconds)",
                              **{'size': self.labelfont_size.value}) # add x-axis label
        self.plt.setp(self.ax[n].get_xticklabels(),
                      fontsize=self.axistick_size.value)   # set x-axis tickmark font size
        self.plt.setp(self.ax[n].get_yticklabels(),
                      fontsize=self.axistick_size.value)   # set y-axis tickmark font size

        # set y-axis labels
        self.ax[n].set_ylabel("Observations",
                                  **{'size': self.labelfont_size.value})

        # store initial plot backgrounds for blitting process (performance boost!)
        self.axbg.append(self.fig.canvas.copy_from_bbox(self.ax[n].bbox))

    self.plt.subplots_adjust(right=1, top=0.95, bottom=0.15, wspace=0, hspace=0.75) # give each subplot


def graphing_step(self):
    for n, i in enumerate(self.key):
        # update the plot title, and plot axes limits
        if i in self.datasrc:
            n = self.datasrc.index(i) # switch from the `key` index to `self.datasrc` index in order
                                      # to access our graph objects' corresponding indices

            # Update axes and titles
            self.ax[n].set_xlim([self.data['time'][-1]-self._xwidth, self.data['time'][-1]])
            if max(self.data[i][-self._xwidth:]) > self.ax[n].get_ylim()[1]:
                new_min = min(self.data[i][-self._xwidth:])
                new_max = max(self.data[i][-self._xwidth:])
                self.ax[n].set_ylim([new_min-abs(new_min)*0.2, new_max+abs(new_max)*0.2])
            self.ax[n].set_title("Data Source {}:    [{}]".format(i, self.data[i][-1]),
                            **{'size': self.titlefont_size.value})

            # update size of axis labels
            self.ax[n].set_xlabel(self.ax[n].get_xlabel(), **{'size': self.labelfont_size.value})
            self.ax[n].set_ylabel(self.ax[n].get_ylabel(), **{'size': self.labelfont_size.value})
            self.plt.setp(self.ax[n].get_xticklabels(), fontsize=self.axistick_size.value)
            self.plt.setp(self.ax[n].get_yticklabels(), fontsize=self.axistick_size.value)

            # Update the graph data (the curve / line / points)
            self.line[n].set_data(self.data['time'][self._xwidth:], self.data[i][self._xwidth:])

    # RENDER WITH BLIT
    for n in range(len(self.datasrc)):
        self.fig.canvas.restore_region(self.axbg[n])
        self.ax[n].draw_artist(self.line[n])
        self.fig.canvas.blit(self.ax[n].bbox)
        self.plt.pause(0.00001)
    self.plt.gcf().canvas.flush_events()

def graphing_process(self):
    while True:
        while self.controls[2].value == False: # while "end process" == False
            if self.controls[1].value == True: # while "pause" == False
                self.graphing_step()
                self.sleep(0.1)
            else:  # while "pause" == True
                self.sleep(0.1)

            self.sleep(0.1)
        else:
            for i in self.control_reference:
                i.disabled=True  # disable controls when "end process" == True
