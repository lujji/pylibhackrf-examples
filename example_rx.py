from pylibhackrf import py_hackrf
from time import sleep
import matplotlib.pyplot as plt
import numpy as np

# sample rate 2MHz, frequency 433.92MHz
F_S = 2e6
freq = 433.92e6

# initialize hackrf, FIFO is not used
hackrf = py_hackrf.hackrf(0)

# vga = 32, lna = 24
hackrf.set_rx_gain(24, 16)

# set sample rate
hackrf.set_sample_rate(int(F_S))

# tune to frequency
hackrf.set_freq(int(freq))

# rx for 10ms (x2 due to I and Q parts)
hackrf.start_rx(2 * int(F_S/1000))
while hackrf.busy():
    sleep(0.1)
hackrf.stop_transfer()

# read buffer
rx = hackrf.read()
rx = np.frombuffer(rx, dtype=np.int8)

rx2 = hackrf.read()
print(rx2)

# extract I and Q components
re = rx[0::2]
im = rx[1::2]

# plot I and Q signals
plt.plot(re)
plt.plot(im)
plt.show()
