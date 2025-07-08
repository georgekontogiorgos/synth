

from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtWidgets import QMainWindow

import sys
import time
import numpy as np
import threading
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class FunctionGenerator(QMainWindow):
    def __init__(self, main):
        super().__init__()


        # self.id = id

        self.main = main

        

        self.omega = 628.318530718 # 100 Hz
        self.amplitude = 0.5
        self.output_enable = False
        self.start_index = 0
        self.samplerate = main.samplerate

        uic.loadUi("function_generator.ui", self)

        self.dial_gain.valueChanged.connect(self.on_amplitude_changed)
        self.dial_freq.valueChanged.connect(self.on_freq_changed)
        self.on_button.stateChanged.connect(self.on_on_off_changed)

    def get_data(self, frames):
        if self.output_enable:
            t = (self.start_index + np.arange(frames)) / self.samplerate
            t = t.reshape(-1, 1)
            self.start_index += frames
            return self.amplitude*np.sin(self.omega*t)
        else:
            return np.zeros(frames).reshape(-1,1)
        
        
    def on_amplitude_changed(self, value):
        self.amplitude = value/100
        self.lcd_gain.display(value)

    def on_freq_changed(self, value):
        self.omega = 2*np.pi*value
        self.lcd_freq.display(value)

    def on_on_off_changed(self, state):
        if self.on_button.isChecked():
            self.output_enable = True
        else:
            self.output_enable = False

    def get_id(self):
        return self.id

    def closeEvent(self, event):
        self.main.remove_generator(self)
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = FunctionGenerator()
    window.show()
    sys.exit(app.exec_())
