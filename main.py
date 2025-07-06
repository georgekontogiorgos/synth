from function_generator import FunctionGenerator

from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtWidgets import QMainWindow

import sys
from numpy import sin, pi
import sounddevice as sd
import threading
import queue
import numpy
import sounddevice as sd
import time
import logging

logging.basicConfig(
    level=logging.INFO,
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

        self.generator_window = []
        self.list_queues = []

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.consumer)
        self.thread.start()

    def closeEvent(self, event):
        self.stop_event.set()
        self.thread.join()
        event.accept()

    def consumer(self):

        fs = 44100
        # We will accumulate samples into small chunks to play
        chunk_size = 256
        buffer = []

        def callback(outdata, frames, time_info, status):
            if not self.list_queues:
                outdata[:] = numpy.zeros((frames, 1), dtype=numpy.float32)
                return

            out = numpy.zeros((frames, 1), dtype=numpy.float32)
            q = self.list_queues[0]

            for i in range(frames):
                try:
                    out[i] = q.get()
                except queue.Empty:
                    out[i] = 0.0

            outdata[:] = out
            logging.info(f"{outdata}")

        with sd.OutputStream(channels=1, callback=callback, samplerate=fs, blocksize=256):
            while not self.stop_event.is_set():
                time.sleep(0.1)
        logging.info("Consumer thread exited")

    def on_click_func_gen(self):
        q = queue.Queue(maxsize=1024)
        generator = FunctionGenerator(q)
        self.generator_window.append(generator)
        self.list_queues.append(q)
        generator.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainPanel()
    window.show()
    sys.exit(app.exec_())
