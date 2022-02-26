import numpy as np
import tensorflow as tf
import warnings
from . import optimize_utils as utils
from . import LossCallback as lcb
from . import configurations
import oparch
import bisect

def opt_all_layer_params(model,X,y,param,**kwargs):
    """Loops over all layers and optimizes the given parameter if the layer has that parameter attribute.

    Args:
        model (Sequential): The model which layers are looped through
        X (feature data): a numpy array
        y (observed output): a numpy arra
        param (string): a string identifier

    Returns:
        _type_: _description_
    """
    kwargs["all"] = True
    layers = model.layers.copy()
    layers.pop(-1)
    orig_layers = len(model.layers)
    removed = 0
    for i,layer in enumerate(layers):
        model = opt_layer_parameter(model, X, y, i+removed, param,**kwargs)
        removed = len(model.layers) - orig_layers
    return model

def opt_optimizer_parameter(model: tf.keras.models.Sequential, X: np.ndarray, y: np.ndarray,param: str,**kwargs) -> tf.keras.models.Sequential or list:
    """
    Optimizes an optimizer parameter such as learning_rate, decay or whatever. Uses enhancing to find the best parameter.
    Only finds the first minima. If learning_metric has a local minima, narrows the search and starts again.
    Stops when the locally optimal parameter is found at either the parameter bounds or at the first local minima.
    
    Returns the model compiled with the optimized parameter.
    If there is a small fault in the call, returns the unchanged model.
    
    Args:
        model (tf.keras.models.Sequential): Sequential model, compiled or with loss function and optimizer as kwargs
        X (np.ndarray): numpy array
        y (np.ndarray): numpy array
        param (str): string identifier of the parameter, for ex "learning_rate"

    Returns:
        tf.keras.models.Sequential or list: _description_
    """    
    oparch.__reset_random__()
    utils.check_types((model,tf.keras.models.Sequential),
                   (X,np.ndarray),
                   (y,np.ndarray),
                   (param,str)
                   )
    # Checks that the model can be compiled and hasn't been trained before
    model = utils.check_compilation(model, X, **kwargs)
    print(f"Optimizing '{param}' for {model.optimizer}...")
    if not hasattr(model.optimizer,param):
        warnings.warn(f"{model.optimizer} doesn't have '{param}' attribute.")
        #print(f"{model.optimizer} doesn't have '{param}' attribute.")
        return model
    return_metric = kwargs.get("return_metric",configurations.get_default_misc("learning_metric"))
    if "RELATIVE" in return_metric:
        epochs = kwargs.get("epochs", configurations.get_default_misc("epochs"))
        if epochs < 2:
            kwargs["epochs"] = 2
    vals = kwargs.get(param,configurations.get_default_interval(param))
    if vals is None:
        warnings.warn(f"Parameter '{param}' doesn't have default values and none were specified.",
              "Specify the testable values with adding an argument with the values to be tested.",
              f"For example: opt_layer(....., {param}=[0.1,0.01,0.005])")
        #print(f"Parameter '{param}' doesn't have default values and none were specified.",
        #      "Specify the testable values with adding an argument with the values to be tested.",
        #      f"For example: opt_layer(....., {param}=[0.1,0.01,0.005])")
        return model
    optimizer_config = model.optimizer.get_config()
    optimizer_type = model.optimizer.__class__
    get_optimizer = lambda : optimizer_type.from_config(optimizer_config)
    curr_param = optimizer_config.get(param)
    decimals = kwargs.get("decimals",configurations.get_default_misc("decimals"))
    #if curr_param not in vals:#curr_param not in vals:
    #    vals.append(curr_param)
    vals = set(vals)
    vals = sorted(vals)
    results = []
    i = 0
    while vals:
        val = vals.pop(0)
        optimizer_config[param] = val
        model.compile(optimizer=get_optimizer(),loss=model.loss)
        metric = utils.test_learning_speed(model,X,y,**kwargs)
        print(f"{param:<16}{val:<16}{return_metric:<16}{metric:<16}")
        bisect.insort(results,(round(val,decimals),round(metric,decimals)),key=lambda x: x[0] if x[0] is not None else -float("inf"))
        #results.append((round(val,decimals),round(metric,decimals)))
        i = i + 1
        new_vals = utils.grid_search(results,**kwargs)
        if new_vals:
            vals = new_vals
        #if not vals or (i > 4 and results[-1][1] - results[-4][1] == 0):
            #break
    utils.plot_results(results)
    return_model = kwargs.get("return_model",True)
    if return_model:
        best = min(results,key=lambda x : x[1])
        optimizer_config[param] = best[0]
        model.compile(optimizer=get_optimizer(),loss=model.loss)
        print("results:",results)
        return model
    else:
        return results
    
def opt_layer_parameter(model,X,y,index,param,**kwargs):
    """
    Optimizes a layer parameter such as pool_size, units.
    
    Returns the compiled model with the optimized parameter implemented in the layer.
    If there is a small fault in the call, returns the unchanged model.
    
    Args:
        model (tf.keras.models.Sequential): Sequential model, compiled or with loss function and optimizer as kwargs
        X (np.ndarray): numpy array
        y (np.ndarray): numpy array
        index (int): the index of the layer to optimize
        param (str): string identifier of the parameter, for ex "learning_rate"

    Returns:
        tf.keras.models.Sequential or list: _description_
    """
    oparch.__reset_random__()
    utils.check_types((model,tf.keras.models.Sequential),
                   (X,np.ndarray),
                   (y,np.ndarray),
                   (param,str)
                   )
    model = utils.check_compilation(model, X, **kwargs)
    if index > len(model.layers)-1:
        warnings.warn(f"Index {index} is out of range. Model has {len(model.layers)} layers")
        return model
    if not hasattr(model.layers[index], param):
        if not kwargs.get("all",False):
            warnings.warn(f"{model.layers[index]} at index {index} doesn't have '{param}' attribute.")
        return model
    print(f"Optimizing '{param}' for {model.layers[index]} at index {index}...")
    vals = kwargs.get(param,configurations.get_default_interval(param))
    if vals is None:
        warnings.warn(f"Parameter '{param}' doesn't have default values and none were specified.",
              "Specify the testable values with adding an argument with the values to be tested.",
              f"For example: opt_layer(....., {param}=[(2,2),(3,3),(2,3)])")
        return model
    if param == "activation" and index == len(model.layers)-1:
        if not model.loss.get_config().get("from_logits",True):
            vals = ["softmax","sigmoid"]          
    return_metric = kwargs.get("return_metric",configurations.get_default_misc("learning_metric"))
    if "RELATIVE" in return_metric:
        epochs = kwargs.get("epochs", configurations.get_default_misc("epochs"))
        if epochs < 2:
            kwargs["epochs"] = 2
    optimizer_config = model.optimizer.get_config()
    optimizer_type = model.optimizer.__class__
    get_optimizer = lambda : optimizer_type.from_config(optimizer_config)
    copy_of_layers = utils.get_copy_of_layers(model.layers)
    layer_configs = utils.get_layers_config(copy_of_layers)
    curr_param = layer_configs[index].get(param)
    loss = model.loss
    if curr_param not in vals:
        bisect.insort(vals,curr_param)
        #vals.append(curr_param)
    loss = model.loss
    results = []
    i = 0
    while vals:
        oparch.__reset_random__()
        val = vals.pop(0)
        if val is None:
            curr_layer = copy_of_layers.pop(index)
            curr_config = layer_configs.pop(index)
        else:
            layer_configs[index][param] = val
        copy_of_layers = utils.layers_from_configs(copy_of_layers, layer_configs)
        model = tf.keras.models.Sequential(copy_of_layers)
        try:
            model.build(np.shape(X))
            model.compile(
            optimizer=get_optimizer(),
            loss=loss
            )
            metric = utils.test_learning_speed(model, X, y,**kwargs)
        except ValueError:
            metric = float("inf")
        print(f"{param:<16}{str(val):<16}{return_metric:<16}{str(metric):<16}")
        try:
            bisect.insort(results,(val,metric),key=lambda x: x[0] if x[0] is not None else -float("inf"))
        except TypeError:
            results.append((val,metric))
        #results.append((val,metric))
        if val is None:
            copy_of_layers.insert(index,curr_layer)
            layer_configs.insert(index,curr_config)
        i = i + 1
        if not vals:
            vals = utils.grid_search(results)
        
    return_model = kwargs.get("return_model",True)
    if not return_model:
        return results
    else:
        best = min(results,key=lambda x : x[1])
        if best[0] is None:
            print(f"Removing {copy_of_layers[index]}...")
            copy_of_layers.pop(index)
            layer_configs.pop(index)
        else:
            layer_configs[index][param] = best[0]
        copy_of_layers = utils.layers_from_configs(copy_of_layers, layer_configs)
        model = tf.keras.models.Sequential(copy_of_layers)
        model.build(np.shape(X))
        model.compile(
            optimizer=get_optimizer(),
            loss=loss
        )
        return model

def opt_loss_fun(model: tf.keras.models.Sequential,X,y,**kwargs):
    """
    Optimizes the loss function by minizing the slope.
    WARNING: Might not work correctly, because incentivizes the loss to start as very large.
    """
    model = utils.check_compilation(model, X, **kwargs)
    return_metric = kwargs.get("return_metric")
    epochs = kwargs.get("epochs",configurations.get_default_misc("epochs"))
    if return_metric == "RELATIVE_IMPROVEMENT_EPOCH" or return_metric is None:
        kwargs["return_metric"] = "RELATIVE_IMPROVEMENT_EPOCH"
        return_metric = "RELATIVE_IMPROVEMENT_EPOCH"
        if epochs<2:
            kwargs["epochs"] = 2
    categorical = kwargs.pop("categorical",False)
    if categorical: #TODO Lisää ehto ilman kwargeja
        loss_functions = list(configurations.LOSS_FUNCTIONS.values())
    else:
        loss_functions = list(configurations.REGRESSION_LOSS_FUNCTIONS.values())
    loss_functions.append(model.loss)
    results = list(range(len(loss_functions)))
    best_metric = float("inf")
    best_loss_fun = model.loss.__class__
    for i, loss_fun in enumerate(loss_functions):
        model.compile(optimizer=model.optimizer, loss=loss_fun)
        try:
            metric = utils.test_learning_speed(model, X, y, **kwargs)
        except ValueError:
            metric = None
        print(type(loss_fun).__name__, return_metric,metric)
        results[i] = [type(loss_fun).__name__,metric]
        if(metric is not None and metric<best_metric):
            best_loss_fun = loss_fun
            best_metric = metric
    return_model = kwargs.get("return_model",True)
    if not return_model:
        return results
    model.compile(optimizer=model.optimizer,loss=best_loss_fun)
    return model