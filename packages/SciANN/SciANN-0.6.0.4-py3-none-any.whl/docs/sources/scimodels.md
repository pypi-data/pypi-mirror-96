# Intro

`SciModel` is similar to Keras' `Model`, prepared to make scientific model creation effortless. 
The inputs are of `Variable` objects, and the outputs are `Target` objects.
As an example:  

```python
from sciann import Variable, Functional, SciModel, Data

x = Variable('x')
y = Variable('y')

Fxy = Functional('Fxy', [x, y], 
                 hidden_layers=[10, 20, 10],
                 activation='tanh')

model = SciModel([x,y], Data(Fxy))
```

`SciModel` can be trained by calling `model.train`. 

```python
training_history = model.train([X_data, Y_data], Fxy_data)
```

`training_history` object records the loss for each epoch as well as other parameters. 
Check Keras' documentation for more details.   

`SciModel` object also provides functionality such as `predict` and `save`.  

---

<span style="float:right;">[[source]](https://github.com/sciann/sciann/tree/master/sciann/models/model.py#L29)</span>
### SciModel

```python
sciann.models.model.SciModel(inputs=None, targets=None, loss_func='mse', optimizer='adam', load_weights_from=None, plot_to_file=None)
```

Configures the model for training.
Example:
__Arguments__

- __inputs__: Main variables (also called inputs, or independent variables) of the network, `xs`.
    They all should be of type `Variable`.
- __targets__: list all targets (also called outputs, or dependent variables)
    to be satisfied during the training. Expected list members are:
    - Entries of type `Constraint`, such as Data, Tie, etc.
    - Entries of type `Functional` can be:
        . A single `Functional`: will be treated as a Data constraint.
            The object can be just a `Functional` or any derivatives of `Functional`s.
            An example is a PDE that is supposed to be zero.
        . A tuple of (`Functional`, `Functional`): will be treated as a `Constraint` of type `Tie`.
    - If you need to impose more complex types of constraints or
        to impose a constraint partially in a specific part of region,
        use `Data` or `Tie` classes from `Constraint`.
- __loss_func__: defaulted to "mse" or "mean_squared_error".
    It can be an string from supported loss functions, i.e. ("mse" or "mae").
    Alternatively, you can create your own loss function and
    pass the function handle (check Keras for more information).
- __optimizer__: defaulted to "adam" optimizer.
    It can be one of Keras accepted optimizers, e.g. "adam".
    You can also pass more details on the optimizer:
    - `optimizer = k.optimizers.RMSprop(lr=0.01, rho=0.9, epsilon=None, decay=0.0)`
    - `optimizer = k.optimizers.SGD(lr=0.001, momentum=0.0, decay=0.0, nesterov=False)`
    - `optimizer = k.optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)`

    Check our Keras documentation for further details. We have found

- __load_weights_from__: (file_path) Instantiate state of the model from a previously saved state.
- __plot_to_file__: A string file name to output the network architecture.

__Raises__

- __ValueError__: `inputs` must be of type Variable.
            `targets` must be of types `Functional`, or (`Functional`, data), or (`Functional`, `Functional`).
    
----

### train


```python
train(x_true, y_true, weights=None, target_weights=None, batch_size=64, epochs=100, learning_rate=0.001, adaptive_weights=False, log_adaptive_weights=None, log_loss_gradients=None, shuffle=True, callbacks=None, stop_lr_value=1e-08, reduce_lr_after=None, reduce_lr_min_delta=0.0, stop_after=None, stop_loss_value=1e-08, log_parameters=None, log_parameters_freq=None, save_weights_to=None, save_weights_freq=0, default_zero_weight=0.0, validation_data=None)
```


Performs the training on the model.

__Arguments__

- __x_true__: list of `Xs` associated to targets of `Y`.
    Expecting a list of np.ndarray of size (N,1) each,
    with N as the sample size.
- __y_true__: list of true `Ys` associated to the targets defined during model setup.
    Expecting the same size as list of targets defined in `SciModel`.
    - To impose the targets at specific `Xs` only, pass a tuple of `(ids, y_true)` for that target.
- __weights__: (np.ndarray) A global sample weight to be applied to samples.
    Expecting an array of shape (N,1), with N as the sample size.
    Default value is `one` to consider all samples equally important.
- __target_weights__: (list) A weight for each target defined in `y_true`.
- __batch_size__: (Integer) or 'None'.
    Number of samples per gradient update.
    If unspecified, 'batch_size' will default to 2^6=64.
- __epochs__: (Integer) Number of epochs to train the model.
    Defaulted to 100.
    An epoch is an iteration over the entire `x` and `y`
    data provided.
- __learning_rate__: (Tuple/List) (epochs, lrs).
    Expects a list/tuple with a list of epochs and a list or learning rates.
    It linearly interpolates between entries.
    Defaulted to 0.001 with no decay.
    Example:
        learning_rate = ([0, 100, 1000], [0.001, 0.0005, 0.00001])
- __shuffle__: Boolean (whether to shuffle the training data).
    Default value is True.
- __adaptive_weights__: Defaulted to False (no updates - evaluated once in the beginning).
    Used if the model is compiled with adaptive_weights.
- __log_adaptive_weights__: Logging the weights and gradients of adaptive_weight.
    Defaulted to adaptive_weights.
- __log_loss_gradients__: Frequency for logging the norm2 of gradients of each target.
    Defaulted to None.
- __callbacks__: List of `keras.callbacks.Callback` instances.
- __reduce_lr_after__: patience to reduce learning rate or stop after certain missed epochs.
    Defaulted to epochs max(10, epochs/10).
- __stop_lr_value__: stop the training if learning rate goes lower than this value.
    Defaulted to 1e-8.
- __reduce_lr_min_delta__: min absolute change in total loss value that is considered a successful change.
    Defaulted to 0.001. 
    This values affects number of failed attempts to trigger reduce learning rate based on reduce_lr_after. 
- __stop_after__: To stop after certain missed epochs. Defaulted to total number of epochs.
- __stop_loss_value__: The minimum value of the total loss that stops the training automatically. 
    Defaulted to 1e-8. 
- __save_weights_to__: (file_path) If you want to save the state of the model (at the end of the training).
- __save_weights_freq__: (Integer) Save weights every N epcohs.
    Defaulted to 0.
- __default_zero_weight__: a small number for zero sample-weight.

__Returns__

A Keras 'History' object after performing fitting.
    
----

### predict


```python
predict(xs, batch_size=None, verbose=0, steps=None)
```


Predict output from network.

__Arguments__

- __xs__: list of `Xs` associated model.
    Expecting a list of np.ndarray of size (N,1) each,
    with N as the sample size.
- __batch_size__: defaulted to None.
    Check Keras documentation for more information.
- __verbose__: defaulted to 0 (None).
    Check Keras documentation for more information.
- __steps__: defaulted to 0 (None).
    Check Keras documentation for more information.

__Returns__

List of numpy array of the size of network outputs.

__Raises__

ValueError if number of `xs`s is different from number of `inputs`.
    
----

### loss_functions


```python
loss_function)
```


loss_function returns the callable object to evaluate the loss.

__Arguments__

- __method__: String.
- "mse" for `Mean Squared Error` or
- "mae" for `Mean Absolute Error` or
- "se" for `Squared Error` or
- "ae" for `Absolute Error`.

__Returns__

Callable function that gets (y_true, y_pred) as the input and
    returns the loss value as the output.

__Raises__

ValueError if anything other than "mse" or "mae" is passed.
    
