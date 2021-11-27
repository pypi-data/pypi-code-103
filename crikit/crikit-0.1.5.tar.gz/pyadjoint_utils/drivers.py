from pyadjoint.enlisting import Enlist
from pyadjoint.tape import get_working_tape, stop_annotating
import numpy
from pyadjoint.overloaded_type import OverloadedType
from typing import Union, List, Optional, Any
from .adjfloat import AdjFloat
from .identity import JacobianIdentity, make_jacobian_identities
from .jax_adjoint import ndarray
from .control import Control
from .tape import Tape

Array = Any


def compute_gradient(
    J: Union[List[OverloadedType], OverloadedType],
    m: Union[List[Control], Control],
    options: Optional[dict] = None,
    tape: Optional[Tape] = None,
    adj_value: float = 1.0,
) -> Union[List[OverloadedType], OverloadedType]:
    """
    Compute the gradient of J with respect to the initialisation value of m,
    that is the value of m at its creation.

    Args:
        J (OverloadedType, list[OverloadedType]):  The objective functional.
        m (Union[list[Control], Control]): The (list of) controls.
        options (dict): A dictionary of options. To find a list of available options
            have a look at the specific control type.
        tape (Tape): The tape to use. Default is the current tape.

    Returns:
        OverloadedType: The derivative with respect to the control. Should be an instance of the same type as
            the control.
    """
    options = {} if options is None else options
    tape = get_working_tape() if tape is None else tape
    tape.reset_variables()
    adj_value = Enlist(adj_value)
    J = Enlist(J)
    m = Enlist(m)

    for i in range(len(adj_value)):
        J[i].block_variable.adj_value = adj_value[i]

    with stop_annotating():
        with tape.marked_nodes(m):
            tape.evaluate_adj(markings=True, inputs=m, outputs=J)

    grads = [i.get_derivative(options=options) for i in m]
    return m.delist(grads)


def compute_jacobian_matrix(
    J: Union[List[OverloadedType], OverloadedType],
    m: Union[List[Control], Control],
    m_jac: Any = None,
    tape: Tape = None,
) -> Any:
    """
    Compute dJdm matrix.

    Args:
        J (OverloadedType): The outputs of the function.
        m (list[pyadjoint_utils.Control] or pyadjoint_utils.Control): The (list of) controls.
        m_jac: An input Jacobian to multiply with. By default, this will be an identity Jacobian.
            If m is a list, this should be a list of lists with len(m_jac) == len(m) and
            len(m_jac[i]) == len(m) for each i-th entry in m_jac.
        tape: The tape to use. Default is the current tape.

    Returns:
        OverloadedType: The jacobian with respect to the control. Should be an instance of the same type as the control.
    """
    tape = get_working_tape() if tape is None else tape

    m = Enlist(m)
    if m_jac is None:
        m_jac = make_jacobian_identities(len(m))
    else:
        m_jac = Enlist(m_jac)

    tape.reset_tlm_matrix_values()

    J = Enlist(J)

    for i, input_jac in enumerate(m_jac):
        m[i].tlm_matrix = Enlist(input_jac)

    with stop_annotating():
        tape.evaluate_tlm_matrix(m, J)

    r = [v.block_variable.tlm_matrix for v in J]
    return J.delist(r)


def compute_jacobian_action(
    J: Union[List[OverloadedType], OverloadedType],
    m: Union[List[Control], Control],
    m_dot: Union[List[OverloadedType], OverloadedType],
    options: Optional[dict] = None,
    tape: Optional[Tape] = None,
) -> Union[List[OverloadedType], OverloadedType]:
    """
    Compute the action of the Jacobian of J on m_dot with respect to the
    initialisation value of m, that is the value of m at its creation.

    Args:
        J (OverloadedType):  The outputs of the function.
        m (list[pyadjoint.Control] or pyadjoint.Control): The (list of) controls.
        options (dict): A dictionary of options. To find a list of available options
            have a look at the specific control type.
        tape: The tape to use. Default is the current tape.
        m_dot(OverloadedType): variation of same overloaded type as m.

    Returns:
        OverloadedType: The action on m_dot of the Jacobian of J with respect to the control. Should be an instance of the same type as the output of J.
    """
    options = {} if options is None else options
    tape = get_working_tape() if tape is None else tape
    tape.reset_tlm_values()
    m_dot = Enlist(m_dot)
    J = Enlist(J)
    m = Enlist(m)

    for i in range(len(m_dot)):
        m[i].tlm_value = m_dot[i]

    with stop_annotating():
        tape.evaluate_tlm(inputs=m, outputs=J)

        Jmdots = []
        for Ji in J:
            if isinstance(Ji.block_variable.tlm_value, numpy.ndarray):
                output = Ji.block_variable.output._ad_copy()
                output, offset = output._ad_assign_numpy(
                    output, Ji.block_variable.tlm_value.flatten(), offset=0
                )
            else:
                output = Ji.block_variable.tlm_value
            Jmdots.append(output)
    return J.delist(Jmdots)


def compute_hessian_action(
    J: Union[List[OverloadedType], OverloadedType],
    m: Union[List[Control], Control],
    m_dot: Union[List[OverloadedType], OverloadedType],
    options: Optional[dict] = None,
    tape: Optional[Tape] = None,
    hessian_value=1.0,
) -> Union[List[OverloadedType], OverloadedType]:
    """
    Compute the Hessian of J in a direction m_dot at the current value of m

    Args:
        J (AdjFloat):  The objective functional.
        m (list or instance of Control): The (list of) controls.
        m_dot (list or instance of the control type): The direction in which to compute the Hessian.
        options (dict): A dictionary of options. To find a list of available options
            have a look at the specific control type.
        tape: The tape to use. Default is the current tape.

    Returns:
        OverloadedType: The second derivative with respect to the control in direction m_dot. Should be an instance of
            the same type as the control.
    """
    tape = get_working_tape() if tape is None else tape
    options = {} if options is None else options

    tape.reset_tlm_values()
    tape.reset_hessian_values()

    m = Enlist(m)
    m_dot = Enlist(m_dot)
    for i, value in enumerate(m_dot):
        m[i].tlm_value = m_dot[i]

    with stop_annotating():
        tape.evaluate_tlm()

    hessian_value = Enlist(hessian_value)
    J = Enlist(J)
    for i in range(len(hessian_value)):
        J[i].block_variable.hessian_value = hessian_value[i]

    with stop_annotating():
        with tape.marked_nodes(m):
            tape.evaluate_hessian(markings=True)

    r = [v.get_hessian(options=options) for v in m]
    return m.delist(r)
