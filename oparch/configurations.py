import tensorflow as tf
IMAGE_SIZE = (180,180)
BATCH_SIZE = 32
LEARNING_METRIC = "LAST_LOSS" #LAST_LOSS or RELATIVE_IMPROVEMENT_EPOCH seems to work best
TEST_EPOCHS = 5
TEST_SAMPLES = 5000

#TODO: This probably has many places where a parameter changed at runtime doesn't reflect
def configure(**kwargs):
    allowed_kwargs = {"IMAGE_SIZE", "BATCH_SIZE", "LEARNING_METRIC", "TEST_EPOCHS", "TEST_SAMPLES"}
    global IMAGE_SIZE,BATCH_SIZE,LEARNING_METRIC,TEST_EPOCHS,TEST_SAMPLES
    IMAGE_SIZE = kwargs.get("IMAGE_SIZE",IMAGE_SIZE)
    BATCH_SIZE = kwargs.get("BATCH_SIZE",BATCH_SIZE)
    LEARNING_METRIC = kwargs.get("LEARNING_METRIC",LEARNING_METRIC)
    TEST_EPOCHS = kwargs.get("TEST_EPOCHS",TEST_EPOCHS)
    TEST_SAMPLES = kwargs.get("TEST_SAMPLES", TEST_SAMPLES)
    

ACTIVATION_FUNCTIONS = {
    "sigmoid":tf.keras.activations.sigmoid,
    "linear":None,
    "tanh":tf.keras.activations.tanh,
    "exponential":tf.keras.activations.exponential,
    "relu":tf.keras.activations.relu,
    "elu":tf.keras.activations.elu,
}

REGRESSION_LOSS_FUNCTIONS = {
    "mse":tf.keras.losses.MeanSquaredError(),
    "mean_squared_logarithmic_error":tf.keras.losses.MeanSquaredLogarithmicError(),
    "mean_absolute_error":tf.keras.losses.MeanAbsoluteError(),
}

LOSS_FUNCTIONS = {
    "categorical_hinge":tf.keras.losses.CategoricalHinge(),
    "hinge":tf.keras.losses.Hinge(),
    "huber":tf.keras.losses.Huber(),
    "KLDivergence":tf.keras.losses.KLDivergence(),
    "mse":tf.keras.losses.MeanSquaredError(),
    "mean_squared_logarithmic_error":tf.keras.losses.MeanSquaredLogarithmicError(),
    "poisson":tf.keras.losses.Poisson(),
}

OPTIMIZERS = {
    "sgd":tf.keras.optimizers.SGD(),
    "adadelta":tf.keras.optimizers.Adadelta(),
    "adagrad":tf.keras.optimizers.Adagrad(),
    "adam":tf.keras.optimizers.Adam(),
    "Adamax":tf.keras.optimizers.Adamax(),
    "rmsprop":tf.keras.optimizers.RMSprop(),
}

BINARY_LOSSES = {
    "binary_crossentropy":tf.keras.losses.BinaryCrossentropy,
}