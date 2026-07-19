import random
from .value import Value


class Module:
    """Base class for all neural network modules (from Karpathy's pattern)."""

    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0.0

    def parameters(self):
        return []


class Neuron(Module):
    """Single neuron with weights, bias, and optional nonlinearity."""

    def __init__(self, nin, nonlin=True, activation='tanh'):
        self.w = [Value(random.uniform(-1, 1), label=f'w{i}') for i in range(nin)]
        self.b = Value(0, label='b')
        self.nonlin = nonlin
        self.activation = activation

    def __call__(self, x):
        act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        if self.nonlin:
            if self.activation == 'tanh':
                return act.tanh()
            elif self.activation == 'relu':
                return act.relu()
            elif self.activation == 'sigmoid':
                return act.sigmoid()
        return act

    def parameters(self):
        return self.w + [self.b]

    def __repr__(self):
        act = self.activation if self.nonlin else 'Linear'
        return f"Neuron({len(self.w)}, {act})"


class Layer(Module):
    """Layer of neurons."""

    def __init__(self, nin, nout, **kwargs):
        self.neurons = [Neuron(nin, **kwargs) for _ in range(nout)]

    def __call__(self, x):
        out = [n(x) for n in self.neurons]
        return out[0] if len(out) == 1 else out

    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]

    def __repr__(self):
        return f"Layer([{', '.join(str(n) for n in self.neurons)}])"


class MLP(Module):
    """Multi-Layer Perceptron."""

    def __init__(self, nin, nouts, activation='tanh'):
        sz = [nin] + nouts
        self.layers = []
        for i in range(len(nouts)):
            is_last = (i == len(nouts) - 1)
            self.layers.append(
                Layer(sz[i], sz[i + 1], nonlin=not is_last, activation=activation)
            )

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]

    def __repr__(self):
        return f"MLP([{', '.join(str(layer) for layer in self.layers)}])"