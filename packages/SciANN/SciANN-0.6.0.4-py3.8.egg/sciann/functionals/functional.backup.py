""" Functional class for SciANN.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.keras import backend as K
graph_unique_name = K.get_graph().unique_name

from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import Activation
from tensorflow.python.keras.layers import Concatenate
from tensorflow.python.keras.layers import Lambda
from tensorflow.python.keras.models import Model
from tensorflow import tensordot, expand_dims

from ..utils import to_list, unpack_singleton, is_same_tensor, unique_tensors
from ..utils import default_weight_initializer
from ..utils import default_regularizer
from ..utils import validations, getitem
from ..utils import floatx, set_floatx
from ..utils import math
# from ..utils.transformers import FourierFeature
from ..utils.activations import SciActivation, get_activation
from ..utils import prepare_default_activations_and_initializers

from .field import Field


""" Configures the Functional object (Neural Network).

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
    activation: defaulted to "tanh".
        Activation function for the hidden layers.
        Last layer will have a linear output.
    output_activation: defaulted to "linear".
        Activation function to be applied to the network output.
    res_net: (True, False). Constructs a resnet architecture.
        Defaulted to False.
    fourier_features: (True)
    kernel_initializer: Initializer of the `Kernel`, from `k.initializers`.
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
def SciFunctional(fields=None,
               variables=None,
               hidden_layers=None,
               activation="tanh",
               output_activation="linear",
               res_net=False,
               fourier=None,
               kernel_initializer=None,
               bias_initializer=None,
               kernel_regularizer=None,
               bias_regularizer=None,
               trainable=True,
               dtype='float64',
               **kwargs):
    # prepare hidden layers.
    if hidden_layers is None:
        hidden_layers = []
    else:
        hidden_layers = to_list(hidden_layers)
    # prepare kernel initializers.
    activations, def_biasinit, def_kerinit = \
        prepare_default_activations_and_initializers(
        len(hidden_layers) * [activation] + [output_activation]
    )
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
    bias_regularizer = default_regularizer(bias_regularizer)
    # prepares fields.
    fields = to_list(fields)
    if all([isinstance(fld, str) for fld in fields]):
        output_fields = [
            Field(
                name=fld,
                dtype=dtype,
                kernel_initializer=kernel_initializer[-1],
                bias_initializer=bias_initializer[-1],
                kernel_regularizer=kernel_regularizer,
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
    if all([isinstance(var, Functional) for var in variables]):
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

    # Input layers.
    if len(inputs) == 1:
        net_input = inputs[0]
    else:
        layer = Concatenate(name=graph_unique_name('conct'))
        net_input = layer(inputs)

    # Define the output network.
    net = [net_input]

    # set up the Fourier layer.
    if fourier is not None:
        fourier = to_list(fourier)
        assert len(fourier) == len(inputs)
        fourier_output = []
        for x, w in zip(inputs, fourier):
            layers.append(
                FourierFeature(w, name=graph_unique_name("Fourier"))
            )
            fourier_output.append(layers[-1](x))
        if len(fourier_output)>1:
            layers.append(Concatenate(name=graph_unique_name('conct')))
            net[-1] = layers[-1](fourier_output)
        else:
            net[-1] = fourier_output[-1]

    # define the ResNet networks.
    if res_net is True:
        res_layers = []
        res_outputs = []
        for rl in ["U", "V", "H"]:
            layers.append(
                Dense(
                    hidden_layers[0],
                    kernel_initializer=kernel_initializer[0],
                    bias_initializer=bias_initializer[0],
                    kernel_regularizer=kernel_regularizer,
                    bias_regularizer=bias_regularizer,
                    trainable=trainable,
                    dtype=dtype,
                    name=graph_unique_name("DRes"+rl+"{:d}b".format(hidden_layers[0]))
                )
            )
            res_output = layers[-1](net_input)
            # Apply the activation.
            if activations[0].activation.__name__ != 'linear':
                layers.append(activations[0])
                res_outputs.append(layers[-1](res_output))
        net[-1] = res_outputs[-1]

    for nLay, nNeuron in enumerate(hidden_layers):
        # Add the layer.
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
        if activations[nLay].activation.__name__ != 'linear': #nLay<len(hidden_layers)-1 and
            layer = activations[nLay]
            layers.append(layer)
            net[-1] = layer(net[-1])
        # Add the resnet layer
        if res_net is True:
            layer = Lambda(lambda xs: (1-xs[0])*xs[1] + xs[0]*xs[2], name=graph_unique_name("ResLayer"))
            net[-1] = layer([net[-1]] + res_outputs[:2])

    # set up the Fourier layer.
    # if fourier is not None and len(fourier)>1:
    #     fourier_dims = [w if isinstance(w,int) else w.size for w in fourier]
    #     f_outputs = []
    #     for nNeuron in fourier_dims:
    #         layer = Dense(
    #             nNeuron,
    #             kernel_initializer=kernel_initializer[-1],
    #             bias_initializer=bias_initializer[-1],
    #             kernel_regularizer=kernel_regularizer,
    #             bias_regularizer=bias_regularizer,
    #             trainable=trainable,
    #             dtype=dtype,
    #             name=graph_unique_name("FourierD{:d}b".format(nNeuron))
    #         )
    #         layers.append(layer)
    #         net[-1] = layer(net[-1])
    #         # Apply the activation.
    #         if activations[-1].activation.__name__ != 'linear':  # nLay<len(hidden_layers)-1 and
    #             layer = activations[-1]
    #             layers.append(layer)
    #             net[-1] = layer(net[-1])
    #         f_outputs.append(net[-1])
    #     # Create the last output.
    #     layers.append(
    #         Lambda(lambda ys: tensordot(expand_dims(ys[0], -1), expand_dims(ys[1], -2), axes=[-1,-2]))
    #     )
    #     net[-1] = layer(f_outputs)

    # Assign to the output variable
    if len(net) == 1:
        net_output = net[0]
    else:
        raise ValueError("Legacy for Enrichment: Must be updated. ")
        layer = Concatenate(name=graph_unique_name('conct'))
        net_output = layer(net)

    # Define the final outputs of each network
    for out in output_fields:
        layers.append(out)
    outputs = []
    for out in output_fields:
        # add the activation on the output.
        if activations[-1].activation.__name__ != 'linear':
            layer = activations[-1]
            layers.append(layer)
            outputs.append(layer(out(net_output)))
        else:
            outputs.append(out(net_output))

    return Functional(
        inputs, outputs, layers
    )


#
#
# def Functional(object):
#     """ Configures the Functional object (Neural Network).
#
#     # Arguments
#         fields: String or Field.
#             [Sub-]Network outputs.
#             It can be of type `String` - Associated fields will be created internally.
#             It can be of type `Field` or `Functional`
#         variables: Variable.
#             [Sub-]Network inputs.
#             It can be of type `Variable` or other Functional objects.
#         hidden_layers: A list indicating neurons in the hidden layers.
#             e.g. [10, 100, 20] is a for hidden layers with 10, 100, 20, respectively.
#         activation: defaulted to "tanh".
#             Activation function for the hidden layers.
#             Last layer will have a linear output.
#         output_activation: defaulted to "linear".
#             Activation function to be applied to the network output.
#         res_net: (True, False). Constructs a resnet architecture.
#             Defaulted to False.
#         fourier_features: (True)
#         kernel_initializer: Initializer of the `Kernel`, from `k.initializers`.
#         bias_initializer: Initializer of the `Bias`, from `k.initializers`.
#         kernel_regularizer: Regularizer for the kernel.
#             To set l1 and l2 to custom values, pass [l1, l2] or {'l1':l1, 'l2':l2}.
#         bias_regularizer: Regularizer for the bias.
#             To set l1 and l2 to custom values, pass [l1, l2] or {'l1':l1, 'l2':l2}.
#         dtype: data-type of the network parameters, can be
#             ('float16', 'float32', 'float64').
#             Note: Only network inputs should be set.
#         trainable: Boolean.
#             False if network is not trainable, True otherwise.
#             Default value is True.
#
#     # Raises
#         ValueError:
#         TypeError:
#     """
#     def __init__(self,
#                  fields=None,
#                  variables=None,
#                  hidden_layers=None,
#                  activation="tanh",
#                  output_activation="linear",
#                  res_net=False,
#                  fourier=None,
#                  kernel_initializer=None,
#                  bias_initializer=None,
#                  kernel_regularizer=None,
#                  bias_regularizer=None,
#                  dtype=None,
#                  trainable=True,
#                  **kwargs):
#         # check data-type.
#         if dtype is None:
#             dtype = K.floatx()
#         elif not K.floatx() == dtype:
#             K.set_floatx(dtype)
#         # prepare hidden layers.
#         if hidden_layers is None:
#             hidden_layers = []
#         else:
#             hidden_layers = to_list(hidden_layers)
#         # check for copy constructor.
#         if all([x in kwargs for x in ('inputs', 'outputs', 'layers')]):
#             self._inputs = kwargs['inputs'].copy()
#             self._outputs = kwargs['outputs'].copy()
#             self._layers = kwargs['layers'].copy()
#             self._set_model()
#             return
#         # prepare kernel initializers.
#         activations, def_biasinit, def_kerinit = \
#             prepare_default_activations_and_initializers(
#             len(hidden_layers) * [activation] + [output_activation]
#         )
#         if kernel_initializer is None:
#             kernel_initializer = def_kerinit
#         elif isinstance(kernel_initializer, (float, int)):
#             kernel_initializer = default_weight_initializer(
#                 len(hidden_layers) * [activation] + [output_activation],
#                 'constant',
#                 scale=kernel_initializer
#             )
#         else:
#             kernel_initializer = [kernel_initializer for l in len(hidden_layers) * [activation] + [output_activation]]
#         # prepare bias initializers.
#         if bias_initializer is None:
#             bias_initializer = def_biasinit
#         elif isinstance(bias_initializer, (float, int)):
#             bias_initializer = default_weight_initializer(
#                 len(hidden_layers) * [activation] + [output_activation],
#                 'constant',
#                 scale=bias_initializer
#             )
#         else:
#             bias_initializer = [bias_initializer for l in len(hidden_layers) * [activation] + [output_activation]]
#         # prepare regularizers.
#         kernel_regularizer = default_regularizer(kernel_regularizer)
#         bias_regularizer = default_regularizer(bias_regularizer)
#         # prepares fields.
#         fields = to_list(fields)
#         if all([isinstance(fld, str) for fld in fields]):
#             output_fields = [
#                 Field(
#                     name=fld,
#                     dtype=dtype,
#                     kernel_initializer=kernel_initializer[-1],
#                     bias_initializer=bias_initializer[-1],
#                     kernel_regularizer=kernel_regularizer,
#                     bias_regularizer=bias_regularizer,
#                     trainable=trainable,
#                 )
#                 for fld in fields
#             ]
#         elif all([validations.is_field(fld) for fld in fields]):
#             output_fields = fields
#         else:
#             raise TypeError(
#                 'Please provide a "list" of field names of'
#                 + ' type "String" or "Field" objects.'
#             )
#         # prepare inputs/outputs/layers.
#         inputs = []
#         layers = []
#         variables = to_list(variables)
#         if all([isinstance(var, Functional) for var in variables]):
#             for var in variables:
#                 inputs += var.outputs
#             # for var in variables:
#             #     for lay in var.layers:
#             #         layers.append(lay)
#         else:
#             raise TypeError(
#                 "Input error: Please provide a `list` of `Functional`s. \n"
#                 "Provided - {}".format(variables)
#             )
#
#         # Input layers.
#         if len(inputs) == 1:
#             net_input = inputs[0]
#         else:
#             layer = Concatenate(name=graph_unique_name('conct'))
#             net_input = layer(inputs)
#
#         # Define the output network.
#         net = [net_input]
#
#         # set up the Fourier layer.
#         if fourier is not None:
#             fourier = to_list(fourier)
#             assert len(fourier) == len(inputs)
#             fourier_output = []
#             for x, w in zip(inputs, fourier):
#                 layers.append(
#                     FourierFeature(w, name=graph_unique_name("Fourier"))
#                 )
#                 fourier_output.append(layers[-1](x))
#             if len(fourier_output)>1:
#                 layers.append(Concatenate(name=graph_unique_name('conct')))
#                 net[-1] = layers[-1](fourier_output)
#             else:
#                 net[-1] = fourier_output[-1]
#
#         # define the ResNet networks.
#         if res_net is True:
#             res_layers = []
#             res_outputs = []
#             for rl in ["U", "V", "H"]:
#                 layers.append(
#                     Dense(
#                         hidden_layers[0],
#                         kernel_initializer=kernel_initializer[0],
#                         bias_initializer=bias_initializer[0],
#                         kernel_regularizer=kernel_regularizer,
#                         bias_regularizer=bias_regularizer,
#                         trainable=trainable,
#                         dtype=dtype,
#                         name=graph_unique_name("DRes"+rl+"{:d}b".format(hidden_layers[0]))
#                     )
#                 )
#                 res_output = layers[-1](net_input)
#                 # Apply the activation.
#                 if activations[0].activation.__name__ != 'linear':
#                     layers.append(activations[0])
#                     res_outputs.append(layers[-1](res_output))
#             net[-1] = res_outputs[-1]
#
#         for nLay, nNeuron in enumerate(hidden_layers):
#             # Add the layer.
#             layer = Dense(
#                 nNeuron,
#                 kernel_initializer=kernel_initializer[nLay],
#                 bias_initializer=bias_initializer[nLay],
#                 kernel_regularizer=kernel_regularizer,
#                 bias_regularizer=bias_regularizer,
#                 trainable=trainable,
#                 dtype=dtype,
#                 name=graph_unique_name("D{:d}b".format(nNeuron))
#             )
#             layers.append(layer)
#             net[-1] = layer(net[-1])
#             # Apply the activation.
#             if activations[nLay].activation.__name__ != 'linear': #nLay<len(hidden_layers)-1 and
#                 layer = activations[nLay]
#                 layers.append(layer)
#                 net[-1] = layer(net[-1])
#             # Add the resnet layer
#             if res_net is True:
#                 layer = Lambda(lambda xs: (1-xs[0])*xs[1] + xs[0]*xs[2], name=graph_unique_name("ResLayer"))
#                 net[-1] = layer([net[-1]] + res_outputs[:2])
#
#         # set up the Fourier layer.
#         # if fourier is not None and len(fourier)>1:
#         #     fourier_dims = [w if isinstance(w,int) else w.size for w in fourier]
#         #     f_outputs = []
#         #     for nNeuron in fourier_dims:
#         #         layer = Dense(
#         #             nNeuron,
#         #             kernel_initializer=kernel_initializer[-1],
#         #             bias_initializer=bias_initializer[-1],
#         #             kernel_regularizer=kernel_regularizer,
#         #             bias_regularizer=bias_regularizer,
#         #             trainable=trainable,
#         #             dtype=dtype,
#         #             name=graph_unique_name("FourierD{:d}b".format(nNeuron))
#         #         )
#         #         layers.append(layer)
#         #         net[-1] = layer(net[-1])
#         #         # Apply the activation.
#         #         if activations[-1].activation.__name__ != 'linear':  # nLay<len(hidden_layers)-1 and
#         #             layer = activations[-1]
#         #             layers.append(layer)
#         #             net[-1] = layer(net[-1])
#         #         f_outputs.append(net[-1])
#         #     # Create the last output.
#         #     layers.append(
#         #         Lambda(lambda ys: tensordot(expand_dims(ys[0], -1), expand_dims(ys[1], -2), axes=[-1,-2]))
#         #     )
#         #     net[-1] = layer(f_outputs)
#
#         # store output layers.
#         for out in output_fields:
#             layers.append(out)
#
#         # Assign to the output variable
#         if len(net) == 1:
#             net_output = net[0]
#         else:
#             raise ValueError("Legacy for Enrichment: Must be updated. ")
#             layer = Concatenate(name=graph_unique_name('conct'))
#             net_output = layer(net)
#
#         # Define the final outputs of each network
#         outputs = []
#         for out in output_fields:
#             # add the activation on the output.
#             if activations[-1].activation.__name__ != 'linear':
#                 layer = activations[-1]
#                 layers.append(layer)
#                 outputs.append(layer(out(net_output)))
#             else:
#                 outputs.append(out(net_output))
#
#         self._inputs = inputs
#         self._outputs = outputs
#         self._layers = layers
#         self._set_model()


# from tensorflow.python.util.tf_export import keras_export
# @keras_export('keras.model.SciFunctional')
class Functional(object):
    """ Configures the Functional object (Neural Network).

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
        activation: defaulted to "tanh".
            Activation function for the hidden layers.
            Last layer will have a linear output.
        output_activation: defaulted to "linear".
            Activation function to be applied to the network output.
        res_net: (True, False). Constructs a resnet architecture.
            Defaulted to False.
        fourier_features: (True)
        kernel_initializer: Initializer of the `Kernel`, from `k.initializers`.
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
    def __init__(self, inputs, outputs, layers):
        # check data-type.
        self.inputs = inputs.copy()
        self.outputs = outputs.copy()
        self.layers = layers.copy()
        self._set_model()

    def _set_model(self, inputs, outputs, layers):
        self.inputs = inputs
        self.outputs = outputs
        self.layers = layers

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
        shape_default = x_pred[0].shape if all([x.shape==x_pred[0].shape for x in x_pred]) else None
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

    @property
    def name(self):
        return self._layers[-1].name
    
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
        """ Get the weights and biases of different layers.

        # Arguments
            at_layer: 
                Get the weights of a specific layer. 
            
        # Returns
            List of numpy array. 
        """
        return [l.get_weights() for l in self.layers]

    def set_weights(self, weights):
        """ Set the weights and biases of different layers.

        # Arguments
            weights: Should take the dimensions as the output of ".get_weights"
            
        # Returns 
        """
        try:
            for l, w in zip(self.layers, weights):
                l.set_weights(w)
        except:
            raise ValueError(
                'Provide data exactly the same as .get_weights() outputs. '
            )

    def count_params(self):
        """ Total number of parameters of a functional.

        # Arguments
            
        # Returns 
            Total number of parameters.
        """
        return sum([l.count_params() for l in self.layers])

    def copy(self):
        return Functional(
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

    def set_trainable(self, val, layers=None):
        """ Set the weights and biases of a functional object trainable or not-trainable.
        Note: The SciModel should be called after this.

        # Arguments
            val: (Ture, False)
            layers: list of layers to be set trainable or non-trainable.
                defaulted to None.
            
        # Returns 
        """
        print("Warning: Call 'SciModel' after using set_trainable")
        if isinstance(val, bool):
            if layers is None:
                for l in self._layers:
                    l.trainable = val
            else:
                for li in to_list(layers):
                    i = -1
                    for l in self._layers:
                        if l.count_params() > 0:
                            i += 1
                        if li == i:
                            l.trainable = val
                            break
        else:
            raise ValueError('Expected a boolean value: True or False')

    def reinitialize_weights(self):
        """ Re-initialize the weights and biases of a functional object.

        # Arguments

        # Returns 
        
        """
        for lay in self.layers:
            if hasattr(lay, 'kernel_initializer') and lay.kernel is not None:
                K.set_value(lay.kernel, lay.kernel_initializer(lay.kernel.shape))
            if hasattr(lay, 'bias_initializer') and lay.bias is not None:
                K.set_value(lay.bias, lay.bias_initializer(lay.bias.shape))

    def split(self):
        """ In the case of `Functional` with multiple outputs,
            you can split the outputs and get an associated functional.

        # Returns
            (f1, f2, ...): Tuple of splitted `Functional` objects
                associated to each output.
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
            f = Functional(
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

    def __eq__(self, other):
        return math.equal(self, other)

    def __ne__(self, other):
        return math.not_equal(self, other)

    def __gt__(self, other):
        return math.greater(self, other)

    def __ge__(self, other):
        return math.greater_equal(self, other)

    def __lt__(self, other):
        return math.less(self, other)

    def __le__(self, other):
        return math.less_equal(self, other)

    @classmethod
    def get_class(cls):
        return Functional
