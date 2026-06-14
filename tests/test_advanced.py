import pytest
import numpy as np
from openquanta.modules.advanced import BitFlipCode, QNNLayer, QAOA_MaxCut

def test_bit_flip_code_no_error():
    c = BitFlipCode()
    res = c.simulate(shots=100)
    # The initial state is H + RZ(0.5). So logical q0 is not a pure basis state.
    # But since we measure it into bit 2, and syndrome into 0,1.
    # Syndrome should always be 00 if no error.
    for k in res.keys():
        assert k[-2:] == "00"  # syndrome bits (c0, c1 are last in little-endian representation, wait... c0 is the rightmost)

def test_qnn_layer():
    c = QNNLayer(3, [0.1, 0.2, 0.3])
    assert c.n_qubits == 3

def test_qaoa_maxcut():
    c = QAOA_MaxCut([(0,1), (1,2)], 3, 0.5, 0.2)
    assert c.n_qubits == 3
