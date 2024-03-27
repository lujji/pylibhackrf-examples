from pylibhackrf import py_hackrf
from time import sleep

# initialize hackrf, FIFO is not used
hackrf = py_hackrf.hackrf(0)

# frequency = 433.92MHz, sample rate = 2MSPS
hackrf.set_sample_rate(2000000)
hackrf.set_freq(433920000)

# fill tx buffer with dummy data (must be I and Q samples)
payload = bytearray([0xff]*32)

# start tx and wait for it to finish
hackrf.start_tx(payload)
while hackrf.busy():
    sleep(0.1)

# stop_transfer must be called after each tx
hackrf.stop_transfer()
