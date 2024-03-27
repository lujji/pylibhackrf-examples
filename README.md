# pylibhackrf-examples
Collection of [pylibhackrf](https://github.com/lujji/pylibhackrf) examples.

```
git clone --recurse-submodules https://github.com/lujji/pylibhackrf-examples
cd pylibhackrf && python3 setup.py build_ext --inplace
```

## scripts
Install dependencies first: `pip install numpy scipy matplotlib`.

- example_tx.py - transmit dummy data
- example_rx.py - receive and plot IQ samples
- example_rx_stream.py - rx streaming with some OOK processing: the script will receive forever until a packet with valid sync pulse is received
