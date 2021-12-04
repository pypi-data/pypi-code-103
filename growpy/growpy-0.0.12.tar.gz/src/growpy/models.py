import tensorflow as tf
from tensorflow import keras

__all__ = ['GeneralizedLogistic',
           'Gaussian',
           'Gompertz',
           'HyperbolasticTypeI',
           'HyperbolasticTypeII',
           'HyperbolasticTypeIII',
           'Linear',
           'SuperGaussian',
           'VanGenuchtenGupta',
           'Verhulst',
           'VonBertalanffy']

class GeneralizedLogistic(tf.keras.Model):
    '''
    Trainable generalized logistic growth model.

    Also called "Richard's curve".

    Attributes
    -------
    K : float
        Upper asymptote.
    A : float
        Lower asymptote.
    B : float
        Growth rate.
    nu : float
        Parameter that affects asymptotic growth.
    Q : float
        Parameter related initial value of dependent variable.
    C : float
        Parameter related to upper asymptote.

    Method
    -------
    call(inputs)
        Predicts dependent variable from input.
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.K = self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=1000.
                ),
            trainable=True
            )
        self.A=self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=self.K
                ),
            trainable=True
            )
        self.B=self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=2
                ),
            trainable=True
            )
        self.nu=self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=2
                ),
            trainable=True
            )
        self.Q=self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=1
                ),
            trainable=True
            )
        self.C=self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=1
                ),
            trainable=True
            )
        self.M=self.add_weight(
            shape=(units, input_dim),
            initializer='random_normal',
            trainable=True
            )

    def self_start(self, x, y, optimizer=tf.keras.optimizers.Nadam(learning_rate=0.1), loss=tf.keras.losses.MeanSquaredError(), epochs=2):
        model = Linear()
        model.compile(optimizer=optimizer, loss=loss)
        self.starter_history = model.fit(x, y, epochs=epochs)
        self.B =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)), trainable=True, name='unimpeded_growth_rate')
        if model.w > 0:
            self.K = tf.Variable(tf.reduce_max(y), trainable=True, name='carrying_capacity')
            self.A = tf.Variable(tf.reduce_min(y), trainable=True)
        elif model.w < 0:
            self.K = tf.Variable(tf.reduce_min(y), trainable=True, name='carrying_capacity')
            self.A = tf.Variable(tf.reduce_max(y), trainable=True)
        else:
            self.K = tf.Variable(tf.reduce_mean(y), trainable=True, name='carrying_capacity')
            self.A = tf.Variable(tf.reduce_mean(y), trainable=True)

    def call(self, inputs):
        '''
        Parameters
        ----------
        inputs : array-like[float]
            Input array of data.
        '''
        result = inputs - self.M
        result = self.B * result
        result = -result
        result = tf.exp(result)
        result = self.Q * result
        result = self.C + result
        result = tf.math.pow(result, 1 / self.nu)
        result = (self.K - self.A) / result
        result = self.A + result
        return result

class Gaussian(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Gaussian_function
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.a=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.b=self.add_weight(
            shape=(units, input_dim),
            initializer='random_normal',
            trainable=True
            )
        self.c=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )

    def self_start(self, x, y):
        self.a = tf.Variable(tf.math.reduce_max(y), trainable=True, name='height')
        self.b = tf.Variable(tf.reduce_mean([x[i] for i in tf.argmax(y)]), trainable=True, name='location')
        self.c = tf.Variable(tf.math.reduce_std(x), trainable=True, name='width')


    def call(self, inputs):
        result = inputs - self.b
        result = result / self.c
        result = tf.math.pow(result, 2)
        result = -result
        result = result / 2
        result = tf.exp(result)
        result = self.a * result
        return result

class Gompertz(tf.keras.Model):

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.a=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.b=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.c=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )


    def call(self, inputs):
        result = self.c * inputs
        result = self.b - result
        result = tf.exp(result)
        result = -result
        result = tf.exp(result)
        result = self.a * result
        return result

# TODO: Implement!
class HollingDisc(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Functional_response#Type_II
    '''

class HyperbolasticTypeI(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Hyperbolastic_functions#Function_H1
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.M = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='carrying_capacity'
            )
        self.P0 = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.delta = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='delta'
            )
        self.theta = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='theta'
            )
        self.t0 = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='initial_time'
            )
        
    def self_start(self, x, y, optimizer=tf.keras.optimizers.Nadam(learning_rate=0.1), loss=tf.keras.losses.MeanSquaredError(), epochs=2):
        model = Linear()
        model.compile(optimizer=optimizer, loss=loss)
        self.starter_history = model.fit(x, y, epochs=epochs, verbose=0)
        self.delta =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)) / 2, trainable=True, name='delta')
        self.theta =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)) / 2, trainable=True, name='theta')
        self.P0 = tf.Variable(model.b, trainable=True, name='initial_population')
        if model.w > 0:
            self.M = tf.Variable(tf.reduce_max(y), trainable=True, name='carrying_capacity')
        elif model.w < 0:
            self.M = tf.Variable(tf.reduce_min(y), trainable=True, name='carrying_capacity')
        else:
            self.M = tf.Variable(tf.reduce_mean(y), trainable=True, name='carrying_capacity')

    def call(self, inputs):
        alpha = tf.math.asinh(self.t0)
        alpha = self.theta * alpha
        alpha = self.delta * self.t0 + alpha
        alpha = tf.math.exp(alpha)
        alpha = (self.M - self.P0) * alpha
        alpha = alpha / self.P0
        result = tf.math.asinh(inputs)
        result = self.theta * result
        result = - self.delta * inputs - result
        result = tf.math.exp(result)
        result = alpha * result
        result = 1 + result
        result = self.M / result
        return result

class HyperbolasticTypeII(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Hyperbolastic_functions#Function_H2
    '''
    
    def __init__(self, units=1, input_dim=1, gamma=1.0, **kwargs):
        super().__init__()
        self.M = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='carrying_capacity'
            )
        self.P0 = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.delta = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='delta_rate'
            )
        self.gamma = tf.constant(gamma)
        self.t0 = self.add_weight(
            shape=(units, input_dim),
            initializer='zeros',
            trainable=True,
            name='initial_time'
            )
        
    def self_start(self, x, y, optimizer=tf.keras.optimizers.Nadam(learning_rate=0.1), loss=tf.keras.losses.MeanSquaredError(), epochs=2):
        model = Linear()
        model.compile(optimizer=optimizer, loss=loss)
        self.starter_history = model.fit(x, y, epochs=epochs, verbose=0)
        self.delta =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)), trainable=True, name='delta_rate')
        self.P0 = tf.Variable(model.b, trainable=True, name='initial_population')
        if model.w > 0:
            self.M = tf.Variable(tf.reduce_max(y), trainable=True, name='carrying_capacity')
        elif model.w < 0:
            self.M = tf.Variable(tf.reduce_min(y), trainable=True, name='carrying_capacity')
        else:
            self.M = tf.Variable(tf.reduce_mean(y), trainable=True, name='carrying_capacity')

    def call(self, inputs):
        alpha = tf.math.pow(self.t0, self.gamma)
        alpha = -self.delta * alpha
        alpha = tf.math.exp(alpha)
        alpha = tf.math.asinh(alpha)
        alpha = self.P0 * alpha
        alpha = (self.M - self.P0) / alpha
        result = tf.math.pow(inputs, self.gamma)
        result = -self.delta * result
        result = tf.math.exp(result)
        result = tf.math.asinh(result)
        result = alpha * result
        result = result + 1
        result = self.M / result
        return result

class HyperbolasticTypeIII(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Hyperbolastic_functions#Function_H3
    '''
    def __init__(self, units=1, input_dim=1, gamma=1.0, **kwargs):
        super().__init__()
        self.M = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='carrying_capacity'
            )
        self.P0 = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.delta = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='delta_rate'
            )
        self.theta = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='theta_rate'
            )
        self.gamma = tf.constant(gamma)
        self.t0 = self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='initial_time'
            )
        
    def self_start(self, x, y, optimizer=tf.keras.optimizers.Nadam(learning_rate=0.1), loss=tf.keras.losses.MeanSquaredError(), epochs=2):
        model = Linear()
        model.compile(optimizer=optimizer, loss=loss)
        self.starter_history = model.fit(x, y, epochs=epochs, verbose=0)
        self.delta =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)) / 2, trainable=True, name='delta_rate')
        self.P0 = tf.Variable(model.b, trainable=True, name='initial_population')
        if model.w > 0:
            self.M = tf.Variable(tf.reduce_max(y), trainable=True, name='carrying_capacity')
        elif model.w < 0:
            self.M = tf.Variable(tf.reduce_min(y), trainable=True, name='carrying_capacity')
        else:
            self.M = tf.Variable(tf.reduce_mean(y), trainable=True, name='carrying_capacity')

    def call(self, inputs):
        alpha = self.theta * self.t0
        alpha = tf.math.asinh(alpha)
        alpha = self.delta * tf.math.pow(self.t0, self.gamma) + alpha
        alpha = tf.math.exp(alpha)
        alpha = (self.M - self.P0) * alpha
        result = self.theta * inputs
        result = tf.math.asinh(result)
        result = -self.delta * tf.math.pow(inputs, self.gamma) - result
        result = tf.math.exp(result)
        result = alpha * result
        result = self.M - result
        return result

class Linear(tf.keras.Model):
    '''
    Example
    ----
    >>> model = Linear()
    >>> x = tf.random.normal((4,1))
    >>> y = model(x)
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.w = self.add_weight(
            shape=(units, input_dim),
            initializer="random_normal",
            trainable=True,
            )
        self.b = self.add_weight(
            shape=(units,),
            initializer="zeros",
            trainable=True
            )

    def call(self, inputs):
        return tf.matmul(inputs, self.w) + self.b

class QuickModel(tf.keras.Model):

    def __init__(self, function, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.a=self.add_weight(
                shape=(units, input_dim),
                initializer='random_normal',
                trainable=True
                )
        self.b=self.add_weight(
                shape=(units, input_dim),
                initializer='random_normal',
                trainable=True
                )
        self.c=self.add_weight(
                shape=(units, input_dim),
                initializer='random_normal',
                trainable=True
                )
        self.d=self.add_weight(
                shape=(units, input_dim),
                initializer='random_normal',
                trainable=True
                )
        self.function = function

    def call(self, inputs):
            return self.a * self.function(self.b * inputs + self.c) + self.d

class SuperGaussian(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Gaussian_function#Higher-order_Gaussian_or_super-Gaussian_function
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.a=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='height'
            )
        self.b=self.add_weight(
            shape=(units, input_dim),
            initializer='random_normal',
            trainable=True,
            name='location'
            )
        self.c=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='width'
            )
        self.p=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True,
            name='shape'
            )

    def self_start(self, x, y):
        self.a = tf.Variable(tf.math.reduce_max(y), trainable=True, name='height')
        self.b = tf.Variable(tf.reduce_mean([x[i] for i in tf.argmax(y)]), trainable=True, name='location')
        self.c = tf.Variable(tf.math.reduce_std(x), trainable=True, name='width')


    def call(self, inputs):
        result = inputs - self.b
        result = result / self.c
        result = tf.math.pow(result, 2)
        result = result / 2
        result = tf.math.pow(result, self.p)
        result = -result
        result = tf.exp(result)
        result = self.a * result
        return result

class VanGenuchtenGupta(tf.keras.Model):
    '''
    https://en.wikipedia.org/wiki/Van_Genuchten%E2%80%93Gupta_model
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.Emax=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.EC50=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.n=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )

    def call(self, inputs):
        result = self.EC50 / inputs
        result = tf.math.pow(result, self.n)
        result = 1.0 + result
        result = 1 / result
        result = self.Emax * result
        return result

class Verhulst(tf.keras.Model):

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.k = self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=1000.
                ),
            trainable=True
            )
        self.p0 = self.add_weight(
            shape=(units, input_dim),
            initializer=tf.keras.initializers.RandomUniform(
                minval=0.,
                maxval=1000.
                ),
            trainable=True
            )
        self.r = self.add_weight(
            shape=(units, input_dim),
            initializer="random_uniform",
            trainable=True
            )
        
    def self_start(self, x, y, optimizer=tf.keras.optimizers.Nadam(learning_rate=0.1), loss=tf.keras.losses.MeanSquaredError(), epochs=2):
        model = Linear()
        model.compile(optimizer=optimizer, loss=loss)
        self.starter_history = model.fit(x, y, epochs=epochs)
        self.r =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)), trainable=True, name='unimpeded_growth_rate')
        self.p0 = tf.Variable(model.b, trainable=True, name='initial_population')
        if model.w > 0:
            self.k = tf.Variable(tf.reduce_max(y), trainable=True, name='carrying_capacity')
        elif model.w < 0:
            self.k = tf.Variable(tf.reduce_min(y), trainable=True, name='carrying_capacity')
        else:
            self.k = tf.Variable(tf.reduce_mean(y), trainable=True, name='carrying_capacity')

    def call(self, inputs):
        result = - self.r * inputs
        result = tf.exp(result)
        result = (self.k - self.p0) * result
        result = result / self.p0
        result = result + 1.0
        result = self.k / result
        return result

class VonBertalanffy(tf.keras.Model):

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.L=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.k=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
        self.t0=self.add_weight(
            shape=(units, input_dim),
            initializer='random_uniform',
            trainable=True
            )
    def self_start(self, x, y, optimizer=tf.keras.optimizers.Nadam(learning_rate=0.1), loss=tf.keras.losses.MeanSquaredError(), epochs=2):
        model = Linear()
        model.compile(optimizer=optimizer, loss=loss)
        self.starter_history = model.fit(x, y, epochs=epochs)
        self.k =  tf.Variable(tf.sign(model.w) * tf.math.log1p(tf.abs(model.w)), trainable=True, name='unimpeded_growth_rate')
        self.L = tf.Variable(tf.reduce_max(y), trainable=True, name='carrying_capacity')
        del model


    def call(self, inputs):
        result = inputs - self.t0
        result = -result
        result = tf.exp(result)
        result = 1 - result
        result = self.L * result
        return result

class SEM(tf.keras.Model):
    '''
    A toy structural equation model.
    '''

    def __init__(self, units=1, input_dim=1, **kwargs):
        super().__init__()
        self.model1 = Gaussian()
        self.model2 = Gaussian()

    def call(self, inputs):
        return tf.concat((self.model1(x), self.model2(x)), 1)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns
    
    # Constuct/Import data
    x = tf.random.uniform((100000,1), 0, 10)
    y = 500 / (1 + (500-50)/50 * tf.exp(-0.5 * x))

    # Defined model
    model = VonBertalanffy()
    optimizer = tf.keras.optimizers.Nadam(learning_rate=0.0001)
    loss = tf.keras.losses.MeanSquaredError()

        
    model.compile(optimizer=optimizer,
                  loss=loss)

    # Self start parameters
    model.self_start(x, y)
    print(model.weights)

    # Train
    history = model.fit(x,
                        y,
                        epochs=20,
                        callbacks=[tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)])
    print(model.weights)

##    # Inspect results
    fig, axes = plt.subplots(2, 1)
    axes[0].scatter(x, y, alpha=0.5, s=1, label='Data')
    axes[0].scatter(x, model(x), alpha=0.5, s=1, label='Model')
    axes[0].set_ylabel('y')
    axes[0].set_xlabel('x')
    axes[0].legend()
    
    axes[1].plot(history.history['loss'], label='Loss')
    axes[1].set_ylabel(loss.name)
    axes[1].set_xlabel('Epoch')
    axes[1].legend()
    plt.show()
