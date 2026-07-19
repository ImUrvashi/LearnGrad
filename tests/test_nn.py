"""Tests for the neural network module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gradient_quest.engine.value import Value
from gradient_quest.engine.nn import Neuron, Layer, MLP


def test_neuron_forward():
    n = Neuron(2)
    out = n([Value(1.0), Value(2.0)])
    assert isinstance(out, Value)
    assert -1.0 <= out.data <= 1.0  # tanh output range


def test_neuron_parameters():
    n = Neuron(3)
    params = n.parameters()
    assert len(params) == 4  # 3 weights + 1 bias


def test_layer_forward():
    layer = Layer(2, 3)
    out = layer([Value(1.0), Value(2.0)])
    assert isinstance(out, list)
    assert len(out) == 3


def test_layer_single_output():
    layer = Layer(2, 1)
    out = layer([Value(1.0), Value(2.0)])
    assert isinstance(out, Value)  # single neuron returns Value, not list


def test_mlp_forward():
    model = MLP(2, [3, 1])
    out = model([Value(1.0), Value(2.0)])
    assert isinstance(out, Value)


def test_mlp_parameters():
    model = MLP(2, [3, 1])
    params = model.parameters()
    # Layer 1: 3 neurons * (2 weights + 1 bias) = 9
    # Layer 2: 1 neuron * (3 weights + 1 bias) = 4
    assert len(params) == 13


def test_mlp_backward():
    model = MLP(2, [3, 1])
    out = model([Value(1.0), Value(2.0)])
    out.backward()
    # All parameters should have non-None gradients
    for p in model.parameters():
        assert p.grad is not None


def test_mlp_zero_grad():
    model = MLP(2, [3, 1])
    out = model([Value(1.0), Value(2.0)])
    out.backward()
    model.zero_grad()
    for p in model.parameters():
        assert p.grad == 0.0


def test_mlp_relu_activation():
    model = MLP(2, [3, 1], activation='relu')
    out = model([Value(1.0), Value(2.0)])
    assert isinstance(out, Value)


def test_mlp_sigmoid_activation():
    model = MLP(2, [3, 1], activation='sigmoid')
    out = model([Value(1.0), Value(2.0)])
    assert isinstance(out, Value)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])