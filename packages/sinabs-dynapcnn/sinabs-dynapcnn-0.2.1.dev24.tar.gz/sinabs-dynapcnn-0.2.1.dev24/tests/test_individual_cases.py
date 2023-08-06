import samna

from sinabs.backend.dynapcnn import DynapcnnCompatibleNetwork
import torch
from torch import nn
from sinabs.from_torch import from_model
from sinabs.layers.iaf_bptt import SpikingLayer
from sinabs.layers import SumPool2d
import pytest


input_shape = (2, 16, 16)
input_data = torch.rand(1, *input_shape, requires_grad=False) * 100.


# --- UTILITIES --- #
def reset_states(seq):
    for s in seq:
        if isinstance(s, SpikingLayer):
            s.reset_states()
    return seq


def networks_equal_output(input_data, snn):
    snn.eval()
    snn_out = snn(input_data).squeeze()  # forward pass
    reset_states(snn)

    spn = DynapcnnCompatibleNetwork(
        snn, input_shape=input_data.shape[1:], discretize=False,
        dvs_input = True,
    )
    spn_out = spn(input_data).squeeze()

    print(snn_out.sum(), spn_out.sum())
    assert torch.equal(snn_out, spn_out)

    # this will give an error if the config is not compatible
    return spn.make_config()


# --- TESTS --- #
def test_with_class():
    torch.manual_seed(0)

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.seq = nn.Sequential(
                nn.Conv2d(2, 4, kernel_size=2, stride=2),
                nn.ReLU(),
            )

        def forward(self, x):
            return self.seq(x)

    snn = from_model(Net())
    snn.eval()
    snn_out = snn(input_data).squeeze()  # forward pass

    snn.reset_states()
    spn = DynapcnnCompatibleNetwork(
        snn, input_shape=input_data.shape[1:], discretize=False
    )
    spn_out = spn(input_data).squeeze()

    assert torch.equal(snn_out, spn_out)


def test_with_sinabs_batch():
    seq = nn.Sequential(
        nn.AvgPool2d(kernel_size=(2, 1), stride=(2, 1)),
        nn.Conv2d(2, 4, kernel_size=2, stride=2),
        SpikingLayer(batch_size=1),
    )

    networks_equal_output(input_data, seq)


def test_initial_pooling():
    torch.manual_seed(0)

    seq = nn.Sequential(
        nn.AvgPool2d(kernel_size=(2, 1), stride=(2, 1)),
        nn.Conv2d(2, 4, kernel_size=2, stride=2),
        SpikingLayer(),
    )

    networks_equal_output(input_data, seq)


def test_initial_sumpooling():
    seq = nn.Sequential(
        SumPool2d(kernel_size=(2, 1), stride=(2, 1)),
        nn.Conv2d(2, 4, kernel_size=2, stride=2),
        SpikingLayer(),
    )

    networks_equal_output(input_data, seq)


def test_pooling_consolidation():
    torch.manual_seed(0)

    seq = nn.Sequential(
        nn.Conv2d(2, 4, kernel_size=2, stride=2),
        SpikingLayer(),
        nn.AvgPool2d(kernel_size=2, stride=2),
        nn.AvgPool2d(kernel_size=2, stride=2),
        nn.Conv2d(4, 2, kernel_size=1, stride=1),
        SpikingLayer()
    )

    networks_equal_output(input_data, seq)


def test_sumpooling_consolidation():
    seq = nn.Sequential(
        nn.Conv2d(2, 4, kernel_size=2, stride=2),
        SpikingLayer(),
        SumPool2d(kernel_size=2, stride=2),
        SumPool2d(kernel_size=2, stride=2),
        nn.Conv2d(4, 2, kernel_size=1, stride=1),
        SpikingLayer()
    )

    networks_equal_output(input_data, seq)


def test_different_xy_input():
    torch.manual_seed(0)

    input_shape = (2, 16, 32)
    input_data = torch.rand(1, *input_shape, requires_grad=False) * 100.

    seq = nn.Sequential(
        nn.Conv2d(2, 4, kernel_size=2, stride=2),
        SpikingLayer(),
        nn.AvgPool2d(kernel_size=2, stride=2),
        nn.Conv2d(4, 2, kernel_size=1, stride=1),
        SpikingLayer()
    )

    networks_equal_output(input_data, seq)


def test_bias_nobias():
    torch.manual_seed(0)

    input_shape = (2, 16, 32)
    input_data = torch.rand(1, *input_shape, requires_grad=False) * 100.

    seq = nn.Sequential(
        nn.Conv2d(2, 4, kernel_size=2, stride=2, bias=True),
        SpikingLayer(),
        nn.AvgPool2d(kernel_size=2, stride=2),
        nn.Conv2d(4, 2, kernel_size=1, stride=1, bias=False),
        SpikingLayer()
    )

    config = networks_equal_output(input_data, seq)
    assert config.cnn_layers[0].leak_enable is True
    assert config.cnn_layers[1].leak_enable is False


def test_batchnorm_after_conv():
    torch.manual_seed(0)
    seq = nn.Sequential(
        nn.Conv2d(2, 2, kernel_size=1, stride=1),
        nn.BatchNorm2d(2),
        SpikingLayer()
    )

    # setting batchnorm parameters, otherwise it's just identity
    seq[-2].running_mean.data = torch.tensor([.2, -.5])
    seq[-2].running_var.data = torch.tensor([1.1, 0.7])
    seq[-2].weight.data = torch.tensor([-.02, -.5])
    seq[-2].bias.data = torch.tensor([-0.2, 0.15])

    networks_equal_output(input_data, seq)


def test_flatten_linear():
    torch.manual_seed(0)

    seq = nn.Sequential(
        nn.Flatten(),
        nn.Linear(512, 2),
        SpikingLayer()
    )

    networks_equal_output(input_data, seq)
