""" Functional class for SciANN.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.keras import backend as K
graph_unique_name = K.get_graph().unique_name

from tensorflow.python.keras.layers import Dense, LSTM, SimpleRNN
from tensorflow.python.keras.layers import Activation
from tensorflow.python.keras.layers import Concatenate

from ..utils import to_list, unpack_singleton, is_same_tensor, unique_tensors
from ..utils import default_weight_initializer
from ..utils import default_regularizer
from ..utils import to_list, unpack_singleton
from ..utils import validations, getitem
from ..utils import math
from ..utils.activations import SciActivation, get_activation
from ..utils import prepare_default_activations_and_initializers

from .rnn_field import RNNField


class RNNFunctional(object):
    """ Configures the LSTMFunctional object (Recurrent Neural Network).

    # Arguments
        fields: String or Field.
            [Sub-]Network outputs.
            It can be of type `String` - Associated fields will be created internally.
            It can be of type `Field` or `Functional`
        variables: Variable.
            [Sub-]Network inputs.
            It can be of type `Variable` or other Functional objects.
        hidden_layers: A list indicating neurons in the hidden layers.
            e.g. [10, 100, 20] is a for hidden layers with 10, 100, 20, respectively.
        activation: Activation function for the hidden layers.
            Last layer will have a linear output.
        output_activation: defaulted to "linear".
            Activation function to be applied to the network output.
        rnn_type: currently, `SimpleRNN` and `LSTM` are accepted.
            Defaulted to `SimpleRNN`.
            Check `Keras` documentation for additional information.
        kernel_initializer: Initializer of the `Kernel`, from `k.initializers`.
        recurrent_initializer: Initializer of the `Recurrent Kernel`, from `k.initializers`.
        bias_initializer: Initializer of the `Bias`, from `k.initializers`.
        kernel_regularizer: Regularizer for the kernel.
            To set l1 and l2 to custom values, pass [l1, l2] or {'l1':l1, 'l2':l2}.
        bias_regularizer: Regularizer for the bias.
            To set l1 and l2 to custom values, pass [l1, l2] or {'l1':l1, 'l2':l2}.
        dtype: data-type of the network parameters, can be
            ('float16', 'float32', 'float64').
            Note: Only network inputs should be set.
        trainable: Boolean.
            False if network is not trainable, True otherwise.
            Default value is True.

    # Raises
        ValueError:
        TypeError:
    """
    def __init__(self,
                 fields=None,
                 variables=None,
                 hidden_layers=None,
                 activation="tanh",
                 output_activation="linear",
                 rnn_type="SimpleRNN",
                 recurrent_activation="tanh",
                 kernel_initializer=None,
                 recurrent_initializer=None,
                 bias_initializer=None,
                 kernel_regularizer=None,
                 recurrent_regularizer=None,
                 bias_regularizer=None,
                 dtype=None,
                 trainable=True,
                 **kwargs):
        # check data-type.
        if dtype is None:
            dtype = K.floatx()
        elif not K.floatx() == dtype:
            K.set_floatx(dtype)
        # prepare hidden layers.
        if hidden_layers is None:
            hidden_layers = []
        else:
            hidden_layers = to_list(hidden_layers)
        # check for copy constructor.
        if all([x in kwargs for x in ('inputs', 'outputs', 'layers')]):
            self._inputs = kwargs['inputs'].copy()
            self._outputs = kwargs['outputs'].copy()
            self._layers = kwargs['layers'].copy()
            self._set_model()
            return
        # prepare kernel initializers.
        activations, def_biasinit, def_kerinit = \
            prepare_default_activations_and_initializers(
            len(hidden_layers) * [activation] + [output_activation]
        )
        # prepare kernel initializer.
        if kernel_initializer is None:
            kernel_initializer = def_kerinit
        elif isinstance(kernel_initializer, (float, int)):
            kernel_initializer = default_weight_initializer(
                len(hidden_layers) * [activation] + [output_activation],
                'constant',
                scale=kernel_initializer
            )
        else:
            kernel_initializer = [kernel_initializer for l in len(hidden_layers) * [activation] + [output_activation]]
        # prepare recurrent initializer.
        if recurrent_initializer is None:
            recurrent_initializer = def_kerinit
        elif isinstance(recurrent_initializer, (float, int)):
            recurrent_initializer = default_weight_initializer(
                len(hidden_layers) * [activation] + [output_activation],
                'constant',
                scale=recurrent_initializer
            )
        else:
            recurrent_initializer = [recurrent_initializer for l in len(hidden_layers) * [activation] + [output_activation]]
        # prepare bias initializers.
        if bias_initializer is None:
            bias_initializer = def_biasinit
        elif isinstance(bias_initializer, (float, int)):
            bias_initializer = default_weight_initializer(
                len(hidden_layers) * [activation] + [output_activation],
                'constant',
                scale=bias_initializer
            )
        else:
            bias_initializer = [bias_initializer for l in len(hidden_layers) * [activation] + [output_activation]]
        # prepare regularizers.
        kernel_regularizer = default_regularizer(kernel_regularizer)
        recurrent_regularizer = default_regularizer(recurrent_regularizer)
        bias_regularizer = default_regularizer(bias_regularizer)
        # prepares fields.
        fields = to_list(fields)
        if all([isinstance(fld, str) for fld in fields]):
            output_fields = [
                RNNField(
                    name=fld,
                    rnn_type='Dense',
                    dtype=dtype,
                    kernel_initializer=kernel_initializer[-1],
                    recurrent_initializer=recurrent_initializer[-1],
                    bias_initializer=bias_initializer[-1],
                    kernel_regularizer=kernel_regularizer,
                    recurrent_regularizer=recurrent_regularizer,
                    bias_regularizer=bias_regularizer,
                    trainable=trainable,
                )
                for fld in fields
            ]
        elif all([validations.is_field(fld) for fld in fields]):
            output_fields = fields
        else:
            raise TypeError(
                'Please provide a "list" of field names of'
                + ' type "String" or "Field" objects.'
            )
        # prepare inputs/outputs/layers.
        inputs = []
        layers = []
        variables = to_list(variables)
        if all([isinstance(var, RNNFunctional) for var in variables]):
            for var in variables:
                inputs += var.outputs
            # for var in variables:
            #     for lay in var.layers:
            #         layers.append(lay)
        else:
            raise TypeError(
                "Input error: Please provide a `list` of `Functional`s. \n"
                "Provided - {}".format(variables)
            )
        # Check and convert activation functions to proper format.
        assert not isinstance(activation, list), \
            'Expected an activation function name not a "list". '
        afunc = get_activation(activation)

        # Input layers.
        if len(inputs) == 1:
            net_input = inputs[0]
        else:
            layer = Concatenate(name=graph_unique_name('conct'))
            net_input = layer(inputs)

        # Define the networks.
        net = [net_input]

        # Adding hidden layers
        for nLay, nNeuron in enumerate(hidden_layers):
            if nLay < 1000:
                # First layer starts with RNN.
                if rnn_type=='LSTM':
                    layer = LSTM(
                        nNeuron,
                        return_sequences=False if nLay == len(hidden_layers)-1 else True,
                        activation=None,
                        recurrent_activation=recurrent_activation,
                        kernel_initializer=kernel_initializer[nLay],
                        recurrent_initializer=recurrent_initializer[nLay],
                        bias_initializer=bias_initializer[nLay],
                        kernel_regularizer=kernel_regularizer,
                        recurrent_regularizer=recurrent_regularizer,
                        bias_regularizer=bias_regularizer,
                        trainable=trainable,
                        dtype=dtype,
                        unroll=True,
                        name=graph_unique_name("LSTM{:d}b_".format(nNeuron))
                    )
                elif rnn_type=='SimpleRNN':
                    layer = SimpleRNN(
                        nNeuron,
                        activation=None,
                        return_sequences=False if nLay == len(hidden_layers)-1 else True,
                        kernel_initializer=kernel_initializer[nLay],
                        recurrent_initializer=recurrent_initializer[nLay],
                        bias_initializer=bias_initializer[nLay],
                        kernel_regularizer=kernel_regularizer,
                        recurrent_regularizer=recurrent_regularizer,
                        bias_regularizer=bias_regularizer,
                        trainable=trainable,
                        dtype=dtype,
                        unroll=True,
                        name=graph_unique_name("SRNN{:d}b_".format(nNeuron))
                    )
                else:
                    raise ValueError(
                        'Invalid entry for `rnn_type` -- '
                        'accepts from (`SimpleRNN`, `LSTM`).'
                    )
            else:
                # Add the dense layer.
                layer = Dense(
                    nNeuron,
                    kernel_initializer=kernel_initializer[nLay],
                    bias_initializer=bias_initializer[nLay],
                    kernel_regularizer=kernel_regularizer,
                    bias_regularizer=bias_regularizer,
                    trainable=trainable,
                    dtype=dtype,
                    name=graph_unique_name("D{:d}b".format(nNeuron))
                )
            layers.append(layer)
            net[-1] = layer(net[-1])
            # Apply the activation.
            if afunc.__name__ != 'linear':
                layer = activations[nLay]
                layers.append(layer)
                net[-1] = layer(net[-1])

        # store output layers.
        for out in output_fields:
            layers.append(out)

        # Assign to the output variable
        if len(net) == 1:
            net_output = net[0]
        else:
            raise ValueError("Legacy for Enrichment: Must be updated. ")
            layer = Concatenate(name=graph_unique_name("{}_".format("conct")))
            net_output = layer(net)

        # check output activation functions.
        output_func = get_activation(output_activation)
        # Define the final outputs of each network
        outputs = []
        for out in output_fields:
            # add the activation on the output.
            if output_func.__name__ != 'linear':
                layer = activations[-1]
                layers.append(layer)
                outputs.append(layer(out(net_output)))
            else:
                outputs.append(out(net_output))

        self._inputs = inputs
        self._outputs = outputs
        self._layers = layers
        self._set_model()

    def eval(self, *kwargs):
        """ Evaluates the functional object for a given input.

        # Arguments
            (SciModel, Xs):
                Evalutes the functional object from the beginning
                    of the graph defined with SciModel.
                    The Xs should match those of SciModel.

            (Xs):
                Evaluates the functional object from inputs of the functional.
                    Xs should match those of inputs to the functional.

        # Returns
            Numpy array of dimensions of network outputs.

        # Raises
            ValueError:
            TypeError:
        """
        if len(kwargs) == 1:
            model = self.model
            # read data.
            mesh = kwargs[0]
        elif len(kwargs) == 2:
            if validations.is_scimodel(kwargs[0]):
                model = K.function(kwargs[0].model.inputs, self.outputs)
            else:
                raise ValueError(
                    'Expected a SciModel object for the first arg. '
                )
            mesh = kwargs[1]
        else:
            raise NotImplemented()
        x_pred = to_list(mesh.copy())
        # To have unified output for postprocessing - limitted support.
        shape_default = x_pred[0].shape if all([x.shape == x_pred[0].shape for x in x_pred]) else None
        # prepare X,Y data.
        for i, (x, xt) in enumerate(zip(x_pred, model.inputs)):
            x_shape = tuple(xt.get_shape().as_list())
            if x.shape != x_shape:
                try:
                    x_pred[i] = x.reshape((-1,) + x_shape[1:])
                except:
                    print(
                        'Could not automatically convert the inputs to be '
                        'of the same size as the expected input tensors. '
                        'Please provide inputs of the same dimension as the `Variables`. '
                    )
                    assert False

        y_pred = to_list(model(x_pred))

        if shape_default is not None:
            try:
                y_pred = [y.reshape(shape_default) for y in y_pred]
            except:
                print("Input and output dimensions need re-adjustment for post-processing.")

        return unpack_singleton(y_pred)

    @property
    def layers(self):
        return self._layers

    @layers.setter
    def layers(self, value):
        self._layers = value

    @property
    def inputs(self):
        return self._inputs

    @inputs.setter
    def inputs(self, value):
        self._inputs = value

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        self._outputs = value

    @property
    def model(self):
        self._set_model()
        return self._model

    def _set_model(self):
        if hasattr(self, '_model'):
            if is_same_tensor(self._inputs, self._model.inputs) and \
               is_same_tensor(self._outputs, self._model.outputs):
               return
        self._model = K.function(
            unique_tensors(self._inputs),
            self._outputs
        )

    def get_weights(self, at_layer=None):
        return [l.get_weights() for l in self.layers]

    def set_weights(self, weights):
        try:
            for l, w in zip(self.layers, weights):
                l.set_weights(w)
        except:
            raise ValueError(
                'Provide data exactly the same as .get_weights() outputs. '
            )

    def count_params(self):
        return sum([l.count_params() for l in self.layers])

    def copy(self):
        return RNNFunctional(
            inputs=self.inputs,
            outputs=self.outputs,
            layers=self.layers
        )

    def append_to_layers(self, layers):
        if self.layers is not layers:
            cl = [x.name for x in self.layers]
            for x in layers:
                if not x.name in cl:
                    self.layers += [x]

    def append_to_inputs(self, inputs):
        if self.inputs is not inputs:
            cl = [x.name for x in self.inputs]
            for x in inputs:
                if not x.name in cl:
                    self.inputs.append(x)

    def append_to_outputs(self, outputs):
        self._outputs += to_list(outputs)

    def set_trainable(self, val):
        if isinstance(val, bool):
            for l in self._layers:
                l.trainable = val
        else:
            raise ValueError('Expected a boolean value: True or False')
        return self

    def reinitialize_weights(self):
        for lay in self.layers:
            if hasattr(lay, 'kernel_initializer') and lay.kernel is not None:
                K.set_value(lay.kernel, lay.kernel_initializer(lay.kernel.shape))
            if hasattr(lay, 'bias_initializer') and lay.bias is not None:
                K.set_value(lay.bias, lay.bias_initializer(lay.bias.shape))
        return self

    def split(self):
        """ In the case of `Functional` with multiple outputs,
            you can split the outputs and get an associated functional.

        # Returns
            (f1, f2, ...): Tuple of splitted `Functional` objects
                associated to cheach outputs.
        """
        if len(self._outputs)==1:
            return self
        fs = ()
        # total number of outputs to get splitted.
        nr = len(self._outputs)
        # associated to each output, there is a layer to be splitted.
        lays = self.layers[:-nr]
        for out, lay in zip(self._outputs, self._layers[-nr:]):
            # copy constructor for functional.
            f = RNNFunctional(
                inputs = to_list(self.inputs),
                outputs = to_list(out),
                layers = lays + to_list(lay)
            )
            fs += (f,)
        return fs

    def __call__(self):
        return self.outputs

    def __pos__(self):
        return self

    def __neg__(self):
        return self*-1.0

    def __add__(self, other):
        return math.add(self, other)

    def __radd__(self, other):
        return math.radd(self, other)

    def __sub__(self, other):
        return math.sub(self, other)

    def __rsub__(self, other):
        return math.rsub(self, other)

    def __mul__(self, other):
        return math.mul(self, other)

    def __rmul__(self, other):
        return math.rmul(self, other)

    def __truediv__(self, other):
        return math.div(self, other)

    def __rtruediv__(self, other):
        return math.rdiv(self, other)

    def __pow__(self, power):
        return math.pow(self, power)

    def __getitem__(self, item):
        return getitem(self, item)

    def diff(self, *args, **kwargs):
        return math.diff(self, *args, **kwargs)

    @classmethod
    def get_class(cls):
        return RNNFunctional