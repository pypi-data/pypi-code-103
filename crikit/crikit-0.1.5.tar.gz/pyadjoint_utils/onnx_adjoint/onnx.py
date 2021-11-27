from pyadjoint_utils.numpy_adjoint import ndarray
from pyadjoint_utils.block import Block
from pyadjoint_utils.identity import JacobianIdentity
from pyadjoint.enlisting import Enlist
from pyadjoint.tape import get_working_tape, stop_annotating, annotate_tape
from pyadjoint.overloaded_type import create_overloaded_object
from functools import wraps

def _array(x):
    return ndarray._ad_init_object(x)

class ONNXBlock(Block):

    def __init__(self,
                 model,
                 jacobian,
                 args,
                 outputs
    ):

        super().__init__()
        # protect the import in case we don't have onnxruntime installed
        # and don't want to use this class
        import onnxruntime as ort
        for arg in args:
            self.add_dependency(arg)
        for out in outputs:
            self.add_output(out.create_block_variable())

        self.model = self._load_model(model) if isinstance(model, str) else model
        self.jacobian = self._load_model(jacobian) if isinstance(jacobian, str) else jacobian

        self._args = list(args)
        self._argnums = list(range(len(args)))

    def _replace_params_partial(self, new_params, idxs):
        for i, idx in enumerate(idxs):
            self._args[idx] = new_params[i]

    def _make_partial_func(self, idxs, f):
        def _pdiff_func(*args):
            param_idxs = [self._argnums[idx] for idx in idxs]
            self._replace_params_partial(args, param_idxs)
            return f(*self._args)

        return _pdiff_func

    def _load_model(self, filename):
        session = ort.InferenceSession(filename)
        inames = [node.name for node in session.get_inputs()]

        def model(*args):
            if len(args) != len(inames):
                raise ValueError("Must provide the same number of args as input names ({len(inames)}) to the model!")
            return tuple(map(_array, session.run(None, {name : arg for name, arg in zip(inames, args)})))

        return model


    def prepare_recompute_component(self, inputs, relevant_outputs):
        return Enlist(self.model(*inputs))
    

    def recompute_component(self, inputs, block_variable, idx, prepared):
        return prepared[idx]


    def prepare_evaluate_tlm_matrix(self, inputs, tlm_inputs, relevant_outputs):
        args = []
        argnums = []
        for i, x in enumerate(tlm_inputs):
            if inputs[i] is not None:
                args.append(inputs[i])
                argnums.append(i)
            if x is not None:
                for j, di_dj in enumerate(x):
                    if (i != j and di_dj is not None) or (
                        i == j and not isinstance(di_dj, JacobianIdentity)
                    ):
                        raise NotImplementedError(
                            "Non-identity tlm_inputs cannot be handled yet!"
                        )

        jacfun = self._make_partial_func(argnums, self.jacobian)
        return jacfun(*args)


    def evaluate_tlm_matrix_component(
        self, inputs, tlm_inputs, block_variable, idx, prepared=None
    ):
        return prepared[idx]




def overload_onnx(model, jacobian=None):

    @wraps(model)
    def _overloaded_model(*args):
        with stop_annotating():
            out = Enlist(model(*args))

        overloads = [create_overloaded_object(x) for x in out]
        if annotate_tape():
            get_working_tape().add_block(
                ONNXBlock(model, jacobian, args, overloads)
            )

        return out.delist(overloads)

    return _overloaded_model
        
