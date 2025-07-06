

from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtWidgets import QMainWindow

import sys
import time
from numpy import sin, pi
import threading
import logging

logger = logging.getLogger(__name__)

class FunctionGenerator(QMainWindow):
    def __init__(self, queue):
        super().__init__()

        self.queue = queue
        self.frequency = 100
        self.gain = 99
        self.stop_event = threading.Event()
        self.output_enable = False
        self.t = 0
        self.dt = 1 / 44100

        self.thread = threading.Thread(target=self.signal_output)
        self.thread.start()

        uic.loadUi("function_generator.ui", self)

        self.dial_gain.valueChanged.connect(self.on_gain_changed)
        self.dial_freq.valueChanged.connect(self.on_freq_changed)
        self.on_button.stateChanged.connect(self.on_on_off_changed)

    def closeEvent(self, event):
        self.stop_event.set()
        self.thread.join()
        event.accept()

    def signal_output(self):
        while not self.stop_event.is_set():
            if self.output_enable:
                output = self.gain * sin(2*pi*self.frequency*self.t)
            else:
                output = 0.0

            self.t += self.dt
            time.sleep(self.dt)
            
            logging.debug(f"Output: {output}")
            
            self.queue.put(output)
        logging.info("signal_output thread exited")

    def on_gain_changed(self, value):
        self.gain = value
        logging.info(f"Gain set to {self.gain}.")
        self.lcd_gain.display(value)

    def on_freq_changed(self, value):
        self.frequency = value
        logging.info(f"Frequency set to {self.frequency} Hz.")
        self.lcd_freq.display(value)

    def on_on_off_changed(self, state):
        if self.on_button.isChecked():
            self.output_enable = True
            logging.info("Generator output ON.")
        else:
            self.output_enable = False
            logging.info("Generator output OFF.")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = FunctionGenerator()
    window.show()
    sys.exit(app.exec_())
