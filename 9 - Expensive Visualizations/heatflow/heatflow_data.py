class data_collector:
    # Setup variable for storing all incoming data
    def init_data(self):
        self.data = {}
        for n in self.datasrc:
            self.data[n] =  [0 for i in range(self._xwidth)] #self.np.zeros(self._xwidth)
        self.data['time'] = [0 for i in range(self._xwidth)] #self.np.zeros(self._xwidth)

        # initial timestamp for tracking time
        self.tstart = self.time.time()

    def __init__(self):
        pass

    def __call__(self):
        while True:
            while self.controls[2].value == False: # while "end process" == False
                if self.controls[1].value == True: # while "pause" == False
                    self.data_collection_step()
                else:  # while "pause" == True
                    self.sleep(0.1)

                self.sleep(0.1)
            else:
                self.finalize_data()
                break  # break out of the loops & terminate the thread


    def data_collection_step(self):
        dt = self.time.time() - self.tstart
        #self.data['time'] =
        self.data['time'].append(dt)
        # Update our DATA and our graphs with new incoming data
        for n, i in enumerate(self.key):
            # Save new data points
            if i in self.datasrc:
                #self.data[i] =
                self.data[i].append(self.math.sin(dt)+self.np.random.rand())


    def finalize_data(self):
        # perform final data preparation
        for n, i in enumerate(self.datasrc): # remove photon count from title
            self.ax[n].set_title("Data Source {}:".format(i),
                                {'size': self.titlefont_size.value})
        for n in self.datasrc+['time']: # drop first 200 placeholder values
            self.data[n] = self.np.asarray(self.data[n][self._xwidth::])
