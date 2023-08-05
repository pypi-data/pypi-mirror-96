from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ..utils import default_bias_initializer, default_kernel_initializer, default_constant_initializer
from tensorflow.python.keras.layers import Dense, SimpleRNN, LSTM, TimeDistributed
from tensorflow.python.keras.activations import linear

from ..utils import default_bias_initializer, default_kernel_initializer
from ..utils import default_regularizer
from ..utils import floatx, set_floatx


class RNNField(Dense):
    """ Configures the `LSTMField` class for the model outputs.

    # Arguments
        units: Positive integer.
            Dimension of the output of the network.
        name: String.
            Assigns a layer name for the output.
        activation: Callable.
            A callable object for the activation.
        kernel_initializer: Initializer for the kernel.
            Defaulted to a normal distribution.
        bias_initializer: Initializer for the bias.
            Defaulted to a normal distribution.
        kernel_regularizer: Regularizer for the kernel.
            To set l1 and l2 to custom values, pass [l1, l2] or {'l1':l1, 'l2':l2}.
        bias_regularizer: Regularizer for the bias.
            To set l1 and l2 to custom values, pass [l1, l2] or {'l1':l1, 'l2':l2}.
        trainable: Boolean to activate parameters of the network.
        dtype: data-type of the network parameters, can be
            ('float16', 'float32', 'float64').

    # Raises

    """
    def __init__(self, units=1,
                 name=None,
                 rnn_type='SimpleRNN',
                 activation=linear,
                 kernel_initializer=default_kernel_initializer(),
                 recurrent_initializer=default_kernel_initializer(),
                 bias_initializer=default_bias_initializer(),
                 kernel_regularizer=None,
                 recurrent_regularizer=None,
                 bias_regularizer=None,
                 trainable=True,
                 dtype=None,):
        if not dtype:
            dtype = floatx()
        elif not dtype == floatx():
            set_floatx(dtype)

        assert isinstance(name, str), \
            "Please provide a string for field name. "
        assert callable(activation), \
            "Please provide a function handle for the activation. "

        # prepare initializers.
        if isinstance(kernel_initializer, (float, int)):
            kernel_initializer = default_constant_initializer(kernel_initializer)
        if isinstance(bias_initializer, (float, int)):
            bias_initializer = default_constant_initializer(bias_initializer)
        # prepare regularizers.
        kernel_regularizer = default_regularizer(kernel_regularizer)
        bias_regularizer = default_regularizer(bias_regularizer)

        # if rnn_type == 'SimpleRNN':
        #     super(RNNField, self).__init__(
        #         SimpleRNN(
        #             units=units,
        #             activation=activation,
        #             return_sequences=True,
        #             kernel_initializer=kernel_initializer,
        #             recurrent_initializer=recurrent_initializer,
        #             bias_initializer=bias_initializer,
        #             kernel_regularizer=kernel_regularizer,
        #             recurrent_regularizer=recurrent_regularizer,
        #             bias_regularizer=bias_regularizer,
        #             trainable=trainable,
        #             dtype=dtype,
        #             unroll=True,
        #             name=name
        #         )
        #     )
        # elif rnn_type == 'LSTM':
        #     super(RNNField, self).__init__(
        #         LSTM(
        #             units=units,
        #             activation=activation,
        #             return_sequences=True,
        #             kernel_initializer=kernel_initializer,
        #             recurrent_initializer=recurrent_initializer,
        #             bias_initializer=bias_initializer,
        #             kernel_regularizer=kernel_regularizer,
        #             recurrent_regularizer=recurrent_regularizer,
        #             bias_regularizer=bias_regularizer,
        #             trainable=trainable,
        #             dtype=dtype,
        #             unroll=True,
        #             name=name
        #         )
        #     )
        # elif rnn_type == 'Dense':
        super(RNNField, self).__init__(
            units=units,
            activation=activation,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            trainable=trainable,
            dtype=dtype,
            name=name
        )
        # else:
        #     raise NotImplementedError('Supported RNNType: (SimpleRNN, LSTM, Dense)')
