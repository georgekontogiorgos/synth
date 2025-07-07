from function_generator import FunctionGenerator

from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtWidgets import QMainWindow

import sys
from numpy import sin, pi
import sounddevice as sd
import threading
import queue
import numpy as np
import sounddevice as sd
import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s][%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class MainPanel(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)

        self.func_gen_button.clicked.connect(self.on_click_func_gen)

        self.samplerate = sd.query_devices(None, 'output')['default_samplerate']
        print(f"sample rate: {self.samplerate}")

        self.generators = []
        self.generator_id_counter = 0

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.consumer)
        self.thread.start()

    def closeEvent(self, event):
        self.stop_event.set()
        self.thread.join()
        event.accept()

    def consumer(self):

        def callback(outdata, frames, time, status):

            if status:
                logging.debug(f"{status}")
            
            waves = []
            
            if self.generators:
                for generator in self.generators:
                    waves.append(generator.signal_output(frames))

                outdata[:] = waves[0]
            else:
                outdata[:] = np.zeros(frames).reshape(-1,1)


        with sd.OutputStream(device=None, channels=1, callback=callback,
                             samplerate=self.samplerate):
            while not self.stop_event.is_set():
                time.sleep(0.1)

    def on_click_func_gen(self):
        generator = FunctionGenerator(self)
        self.generators.append(generator)
        logging.debug(f"{self.generators}")
        generator.show()

    def remove_generator(self, target):
        try:
            self.generators.remove(target)
        except ValueError:
            logging.error(f"'{target}' not found in the list.")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainPanel()
    window.show()
    sys.exit(app.exec_())
