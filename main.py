from function_generator import FunctionGenerator

from PyQt5 import uic, QtWidgets, QtCore

from PyQt5.QtWidgets import QMainWindow

import sys
from numpy import sin, pi
import sounddevice as sd
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
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

        self.generators = []
        self.generator_id_counter = 0

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.consumer)
        self.thread.start()

    def closeEvent(self, event):
        self.stop_event.set()
        self.thread.join()
        event.accept()

    def consumer(self, output_filename="output.wav"):

        file = sf.SoundFile(output_filename, mode='w', samplerate=self.samplerate,
                        channels=1, subtype='PCM_16')

        def mix_audio(frames):
            try:
                if not self.generators:
                    return np.zeros((frames, 1), dtype=np.float32)

                chunks = [gen.get_data(frames) for gen in self.generators]
                
                if not all(chunk.shape == chunks[0].shape for chunk in chunks):
                    raise ValueError("Inconsistent chunk shapes from generators.")
                
                return np.sum(chunks, axis=0)
            except Exception as e:
                logging.exception("Error while mixing audio")
                return np.zeros((frames, 1), dtype=np.float32)

        
        def callback(outdata, frames, time, status):
            if status:
                logging.error(f"Stream status: {status}")
            outdata[:] = mix_audio(frames)

        logging.info("Starting audio stream with %d generators", len(self.generators))

        with sd.OutputStream(device=None,
                            channels=1,
                            callback=callback,
                            samplerate=self.samplerate):
            try:
                while not self.stop_event.is_set():
                    time.sleep(0.1)
            finally:
                logging.info("Audio stream stopped.")


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
