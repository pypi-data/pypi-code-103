import numpy as np
import tensorflow as tf

class IterativeGaussianGuess():

    def __init__(self, model, x, y, loss):
        self.model = model
        self.x = x
        self.y = y
        self.loss = loss

    def __call__(self, mean, std, iters=1000):
        loss = np.inf
        best_model = None
        for i in range(iters):
            new_weights = []
            for j, param in enumerate(self.model.get_weights()):
                new_weights.append(
                    tf.random.normal(
                        shape=param.shape,
                        mean=mean,
                        stddev=std
                        )
                    )
            self.model.set_weights(new_weights)
            new_loss = self.loss(self.y, self.model(self.x))
            if new_loss < loss:
                loss = new_loss
                best_model = self.model
        return best_model
