import crikit.network as backend_network
import numpy as np
from pyadjoint.overloaded_type import (
    OverloadedType,
    create_overloaded_object,
    register_overloaded_type,
)


@register_overloaded_type
class Network(OverloadedType, backend_network.Network):
    def __init__(self, *args, **kwargs):
        super(Network, self).__init__(*args, **kwargs)
        backend_network.Network.__init__(self, *args, **kwargs)

    def create_copy(self, weights=None):
        return create_overloaded_object(
            backend_network.Network.create_copy(self, weights)
        )

    @classmethod
    def _ad_init_object(cls, obj):
        r = cls(obj.layers)
        return r

    def _create_from_values(self, values):
        return self.create_copy(weights=values)

    # This takes the result of an adjoint computation and converts it to my type.
    def _ad_convert_type(self, value, options={}):
        if value is None:
            # TODO: Should the default be 0 constant here or return just None?
            return None
        if isinstance(value, backend_network.Network):
            return value
        return self._create_from_values(value)

    def _ad_create_checkpoint(self):
        return self.create_copy()

    def _ad_restore_at_checkpoint(self, checkpoint):
        return checkpoint

    def _ad_mul(self, other):
        weights = self.get_weights()
        for w in weights:
            w *= other
        return self._create_from_values(weights)

    def __add__(self, other):
        return self._ad_add(other)

    def _ad_add(self, other):
        weights = self.get_weights()
        other_weights = other.get_weights(copy=False)
        for w, ow in zip(weights, other_weights):
            w += ow
        return self._create_from_values(weights)

    def _ad_dot(self, other, options=None):
        dot = 0
        weights = self.get_weights(copy=False)
        other_weights = other.get_weights(copy=False)
        for w, ow in zip(weights, other_weights):
            dot += np.sum(w * ow)
        return dot

    @staticmethod
    def _ad_assign_numpy(dst, src, offset):
        weights = dst.get_weights(copy=False)
        new_weights = []
        for w in weights:
            new_weights.append(np.reshape(src[offset : offset + w.size], w.shape))
            offset += w.size
        dst.set_weights(new_weights)
        return dst, offset

    @staticmethod
    def _ad_to_list(m):
        weights = m.get_weights(copy=False)
        flattened_weights = []
        for w in weights:
            for row in w:
                for val in row:
                    flattened_weights.append(val)
        return flattened_weights

    def _ad_copy(self):
        return self.create_copy()

    def _ad_dim(self):
        weights = self.get_weights(copy=False)
        dim = 0
        for w in weights:
            dim += w.size
        return dim


@register_overloaded_type
class PlapNetwork(OverloadedType, backend_network.PlapNetwork):
    def __init__(self, *args, **kwargs):
        super(PlapNetwork, self).__init__(*args, **kwargs)
        backend_network.PlapNetwork.__init__(self, *args, **kwargs)

    def create_copy(self, weights=None):
        # TODO: this is inefficient because it creates a backend copy and then
        # create_overloaded_object calls _ad_init_object, which creates another copy.
        return create_overloaded_object(
            backend_network.PlapNetwork.create_copy(self, weights)
        )

    @classmethod
    def _ad_init_object(cls, obj, weights=None):
        p = obj.p if weights is None else weights
        r = cls(
            p,
            dims=obj.dims,
            input_just_vector=obj.input_just_vector,
            output_vector=obj.output_vector,
        )
        return r

    # This takes the result of an adjoint computation and converts it to my type.
    def _ad_convert_type(self, value, options={}):
        if value is None:
            # TODO: Should the default be 0 constant here or return just None?
            return None
        if isinstance(value, backend_network.PlapNetwork):
            return value
        return self.create_copy(value)

    def _ad_create_checkpoint(self):
        return self.create_copy(self.p)

    def _ad_restore_at_checkpoint(self, checkpoint):
        return checkpoint

    def _ad_mul(self, other):
        return self.create_copy(self.p * other)

    def __add__(self, other):
        return self._ad_add(other)

    def _ad_add(self, other):
        return self.create_copy(self.p + other.p)

    def _ad_dot(self, other, options=None):
        return self.p * other.p

    @staticmethod
    def _ad_assign_numpy(dst, src, offset):
        dst.p = src[offset]
        offset += 1
        return dst, offset

    @staticmethod
    def _ad_to_list(m):
        return [m.p]

    def _ad_copy(self):
        return self.create_copy(self.p)

    def _ad_dim(self):
        return 1
