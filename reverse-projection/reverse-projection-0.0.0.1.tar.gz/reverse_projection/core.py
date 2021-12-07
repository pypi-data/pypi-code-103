import numpy as np, logging
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from collections import defaultdict as dict

logger = logging.getLogger(__name__)

def hp_space(*args):
    space = []
    # arg --> dict, e.g., {fname: [min, max], fname: {range: {min, max}/[a,b,c,d], type: "uniform/choice"}}
    # data in item should be int or float
    for arg in args:
        for fname, item in arg.items():
            if isinstance(item, (list, np.ndarray, )):
                if len(item) > 2 or len(item) == 1:
                    hpobj = hp.choice(fname, item)
                elif len(item) == 2:
                    hpobj = hp.uniform(fname, item[0], item[1])
                else:
                    raise Exception(f"{fname}'s item length is {len(item)}, should be > 0.")
            elif isinstance(item, dict):
                if item["type"] == "uniform":
                    hpobj = hp.uniform(fname, item["range"])
                elif item["type"] == "choice":
                    hpobj = hp.choice(fname, item["range"])
                else:
                    raise Exception(f"item['type'] should be uniform or choice, not {item['type']}")
            elif isinstance(item, (int, float, )):
                hpobj = hp.choice(fname, [item])
            else:
                raise Exception(f"item should be list/ndarray, dict or int/float, not {type(item)}")
        space.append(hpobj)
    return space

class ReverseProjection(object):

    def __init__(self, transformer=None):
        self.trials = {}
        self.transformer = transformer

        self.early_stop_loss = None
        self.criterion = None
        self.verbose = None
        self.best_trial = None

    def searching_fn(self, params, point):
        point = np.array(point)
        outputted_point = self.transformer.transform(np.array(params).reshape(1, -1)).reshape(-1, )[:point.shape[0]]
        error = outputted_point - point
        error = (error**2).sum()
        if self.verbose:
            logger.info(f"{params}, error: {error}")
        point_name = f"{round(point[0], 2)}_{round(point[1], 2)}"
        if point_name not in self.trials.keys():
            self.trials[point_name] = []
        self.trials[point_name].append([
            error, outputted_point, params
        ])
        return error, outputted_point

    def reverse_search(self, *hpobjargs, point, iteration=100, criterion=0.1, early_stop_loss=None, verbose=True,
                       early_stop_fn=None, hp_space_fn=None, searching_fn=None):
        """
        hpobjargs --> dict, e.g., {fname: [min, max], fname: {range: {min, max}/[a,b,c,d], type: "uniform/choice"}}
        hp_space_fn --> callable function, if None, use the default function hp_space

        """
        if hp_space_fn:
            space = hp_space_fn(*hpobjargs)
        else:
            space = hp_space(*hpobjargs)

        if early_stop_fn is None:
            early_stop_fn = self.early_stop_fn

        if searching_fn is None:
            searching_fn = self.searching_fn

        if early_stop_loss is None:
            if self.early_stop_loss is None:
                self.early_stop_loss = 0.1 * criterion

        if self.criterion is None:
            self.criterion = criterion
        if self.verbose is None:
            self.verbose = verbose

        def f(params):
            error = searching_fn(params, point)
            return {'loss': error[0], 'status': STATUS_OK}

        trials = Trials()
        fmin(fn=f, space=space, algo=tpe.suggest, max_evals=iteration, verbose=verbose, trials=trials, early_stop_fn=early_stop_fn)

        self.best_trial = { i:sorted(j, key=lambda x: x[0], reverse=False)[0] for i, j in self.trials.items()}

        return self

    def early_stop_fn(self, trials, *args, **wargs):
        best_loss = trials.best_trial["result"]["loss"]
        if best_loss < self.early_stop_loss:
            return True, dict(loss=trials.losses()[-1])
        else:
            return False, dict(loss=trials.losses()[-1])
