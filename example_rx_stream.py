import time
import numpy as np
from scipy import signal
from itertools import groupby
from collections import deque
from pylibhackrf import py_hackrf
from ook import OOK

def to_complex(data : bytearray):
    '''
    Convert bytearray into complex np.array
    '''
    v = np.frombuffer(data, dtype=np.int8)

    rx_real = v[0::2]
    rx_imag = v[1::2]

    # remove DC bias
    rx_real = rx_real - np.mean(rx_real)
    rx_imag = rx_imag - np.mean(rx_imag)

    # convert to complex
    return rx_real + 1j * rx_imag

def to_bits(rx_sig, symbol_len, fs, min_thres):
    # moving average
    # window_size = 16
    # filtered = abs(np.convolve(rx_sig, np.ones(window_size) / window_size, mode='valid'))

    # low-pass filter
    b, a =  signal.iirfilter(1, Wn=[8 * fs/symbol_len], fs=fs, btype='low', ftype='butter', output='ba')
    filtered = signal.filtfilt(b, a, abs(rx_sig))

    # calculate maximums of abs(sig)
    a = sorted(filtered)
    threshold = (a[-len(a)//32] - a[len(a)//32]) / 2
    if threshold < min_thres:
        return [], ''

    print(f'threshold: {threshold}')

    # threshold detector
    symbols = [1 if abs(value) > threshold else 0 for value in filtered]

    # decoder
    bits = []
    for k, g in groupby(''.join(str(x) for x in symbols)):
        n = len(list(g))
        if n >= symbol_len:
            bits.append(k * round(n / symbol_len))

    return symbols, ''.join(bits)

def decode_pkt(encoding: dict, bits: str, sync: str):
    start = bits.find(sync)
    if start == -1:
        print('preamble not found')
        return ''

    return OOK.decode(bits, encoding, start)


sync = '100000000'
encoding = {'1110': '1', '1000': '0'}
sym_len = 700
thres = 1.5
f_s = int(2e6)

capture_time_sec = 0.5
capture_len = int(f_s * 2 * capture_time_sec) # x2 for I and Q

hackrf = py_hackrf.hackrf(1024)
hackrf.set_rx_gain(24, 16)
hackrf.set_sample_rate(f_s)
hackrf.set_freq(int(433.92e6))

hackrf.start_rx_stream()
rx_data = None

print('waiting for packet..')
while hackrf.busy():
    rx = hackrf.pop(100)
    if not rx:
        continue

    if rx_data:
        rx = bytearray(rx)
        rx_data.extend(rx)
        if len(rx_data) >= capture_len:
            sig = to_complex(rx_data)
            syms, bits = to_bits(sig, sym_len, f_s, thres)

            # decode packet
            pkt = decode_pkt(encoding, bits, sync)
            if pkt and any(len(i) > 4 for i in pkt):
                print('VALID PACKET!')
                print([hex(int(i, 2)) for i in pkt])
                break

            rx_data = None
    else:
        sig = to_complex(rx)
        _, bits = to_bits(sig, sym_len, f_s, thres)
        if '1' in bits:
            print('got 1')
            rx_data = bytearray(rx)

print('stop xfer')
hackrf.stop_transfer()
