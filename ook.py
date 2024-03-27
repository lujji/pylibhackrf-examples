import numpy as np

class OOK:
    def __init__(self, F_S, F, symbol_len, pause_len=0, amp=127):
        '''
        Initialize OOK processor

            Parameters:
                F_S (int): sample rate in Hz
                F (int): carrier frequency in Hz
                symbol_len (int): symbol length in samples
                pause_len (int): pause ('p') length in samples
                amp (int): signal amplitude
        '''
        self.F_S = F_S
        self.F = F
        self.symbol_len = symbol_len * 2
        self.pause_len = pause_len * 2

        phi = np.pi / 2
        lut = np.array([amp * np.exp(-1j * (2 * np.pi * i * F/F_S + phi))
                        for i in range(round(F_S/F))])
        self.sine_lut = np.array([int(round(i))
                        for _ in list(zip(lut.real, lut.imag)) for i in _])

        self.symbol_0 = np.zeros(self.symbol_len, dtype=int)
        self.symbol_p = np.zeros(self.pause_len, dtype=int)
        self.symbol_map = { '1': self.sine_lut, '0': self.symbol_0, 'p': self.symbol_p }

    @staticmethod
    def encode(message: str, encoding: dict) -> str:
        '''
        Encode payload based on provided encoding

            Parameters:
                message: message to be encoded
                encoding: dictionary used for encoding

            Returns:
                encoded message based on provided encoding,
                unknown symbols are left as is
        '''
        return ''.join(encoding[i] if i in encoding else i for i in message)

    @staticmethod
    def decode(message: str, encoding: dict, start=0) -> str:
        '''
        Decode payload based on provided encoding

            Parameters:
                message: message to be decoded
                encoding: dictionary used for decoding
                start: start decoding from this index

            Returns:
                decoded message based on provided encoding,
                messages are split when unknown symbol is encountered
        '''
        sorted_encoding = np.array(sorted(list(encoding.keys()), reverse=True), dtype='U')

        decoded = []
        msg = []
        i = start
        while i < len(message):
            substr = sorted_encoding[np.char.startswith(message[i:], sorted_encoding)]
            if len(substr) > 0:
                msg.append(encoding[substr[0]])
                i += len(substr[0])
            else:
                i += 1
                if msg:
                    decoded.append(''.join(msg))
                    msg = []

        return decoded

    def generate(self, packet: str) -> list:
        '''
        Generate OOK payload

            Packet may contain following symbols:
            '1' - logical 1
            '0' - logical 0
            'p' - pause (logical 0 with pause_len duration)

            Unknown symbols are ignored
        '''
        payload = []
        for symbol in packet:
            if symbol in self.symbol_map:
                payload.extend(np.tile(self.symbol_map[symbol], self.symbol_len // len(self.symbol_map[symbol])))
            elif symbol != ' ':
                print("unknown symbol:", symbol)

        return payload

def de_bruijn(k, n):
    '''
    generate de Bruijn sequence for given alphabet and subsequences of length n
    https://en.wikipedia.org/wiki/De_Bruijn_sequence

        Example:
        # generate binary codes with a length of 8
        msg = de_bruijn("01", 8)
    '''
    v = [0] * k * n

    def db(t, p):
        nonlocal v, n

        if t > n:
            if n % p == 0:
                for j in range(1, p + 1):
                    yield v[j]
        else:
            v[t] = v[t - p]
            yield from db(t + 1, p)
            for j in range(v[t - p] + 1, k):
                v[t] = j
                yield from db(t + 1, t)

    yield from db(1, 1)
