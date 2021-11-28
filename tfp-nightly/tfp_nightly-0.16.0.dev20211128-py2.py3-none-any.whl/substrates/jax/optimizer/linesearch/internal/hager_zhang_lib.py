# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Implements the Hager-Zhang inexact line search algorithm.

Line searches are a central component for many optimization algorithms (e.g.
BFGS, conjugate gradient etc). Most of the sophisticated line search methods
aim to find a step length in a given search direction so that the step length
satisfies the
[Wolfe conditions](https://en.wikipedia.org/wiki/Wolfe_conditions).
[Hager-Zhang 2006](https://epubs.siam.org/doi/abs/10.1137/030601880)
algorithm is a refinement of the commonly used
[More-Thuente](https://dl.acm.org/citation.cfm?id=192132) algorithm.

This module implements the Hager-Zhang algorithm.
"""

import collections

from tensorflow_probability.python.internal.backend.jax.compat import v1 as tf1
from tensorflow_probability.python.internal.backend.jax.compat import v2 as tf
from tensorflow_probability.substrates.jax.internal import prefer_static


def val_where(cond, tval, fval):
  """Like tf.where but works on namedtuples."""
  if isinstance(tval, tf.Tensor):
    return tf1.where(cond, tval, fval)
  elif isinstance(tval, tuple):
    cls = type(tval)
    return cls(*(val_where(cond, t, f) for t, f in zip(tval, fval)))
  else:
    raise Exception(TypeError)


_Secant2Result = collections.namedtuple('_Secant2Result', [
    'active',     # Boolean indicating batch members with work left to do.
    'converged',  # Boolean indicating whether wolfe conditions are satisfied.
    'failed',     # Boolean indicating whether the secant procedure failed.
    'num_evals',  # The total number of objective evaluations performed.
    'left',       # Result of value_and_gradients_function at left end point.
    'right'       # Result of value_and_gradients_function at right end point.
])


def secant2(value_and_gradients_function,
            val_0,
            search_interval,
            f_lim,
            sufficient_decrease_param=0.1,
            curvature_param=0.9,
            name=None):
  """Performs the secant square procedure of Hager Zhang.

  Given an interval that brackets a root, this procedure performs an update of
  both end points using two intermediate points generated using the secant
  interpolation. For details see the steps S1-S4 in [Hager and Zhang (2006)][2].

  The interval [a, b] must satisfy the opposite slope conditions described in
  the documentation for `update`.

  Args:
    value_and_gradients_function: A Python callable that accepts a real scalar
      tensor and returns an object that can be converted to a namedtuple.
      The namedtuple should have fields 'f' and 'df' that correspond to scalar
      tensors of real dtype containing the value of the function and its
      derivative at that point. The other namedtuple fields, if present,
      should be tensors or sequences (possibly nested) of tensors.
      In usual optimization application, this function would be generated by
      projecting the multivariate objective function along some specific
      direction. The direction is determined by some other procedure but should
      be a descent direction (i.e. the derivative of the projected univariate
      function must be negative at 0.).
      Alternatively, the function may represent the batching of `n` such line
      functions (e.g. projecting a single multivariate objective function along
      `n` distinct directions at once) accepting n points as input, i.e. a
      tensor of shape [n], and the fields 'f' and 'df' in the returned
      namedtuple should each be a tensor of shape [n], with the corresponding
      function values and derivatives at the input points.
    val_0: A namedtuple, as returned by value_and_gradients_function evaluated
      at `0.`.
    search_interval: A namedtuple describing the current search interval,
      must include the fields:
      - converged: Boolean `Tensor` of shape [n], indicating batch members
          where search has already converged. Interval for these batch members
          won't be modified.
      - failed: Boolean `Tensor` of shape [n], indicating batch members
          where search has already failed. Interval for these batch members
          wont be modified.
      - iterations: Scalar int32 `Tensor`. Number of line search iterations
          so far.
      - func_evals: Scalar int32 `Tensor`. Number of function evaluations
          so far.
      - left: A namedtuple, as returned by value_and_gradients_function,
          of the left end point of the current search interval.
      - right: A namedtuple, as returned by value_and_gradients_function,
          of the right end point of the current search interval.
    f_lim: Scalar `Tensor` of real dtype. The function value threshold for
      the approximate Wolfe conditions to be checked.
    sufficient_decrease_param: Positive scalar `Tensor` of real dtype.
      Bounded above by the curvature param. Corresponds to 'delta' in the
      terminology of [Hager and Zhang (2006)][2].
    curvature_param: Positive scalar `Tensor` of real dtype. Bounded above
      by `1.`. Corresponds to 'sigma' in the terminology of
      [Hager and Zhang (2006)][2].
    name: (Optional) Python str. The name prefixed to the ops created by this
      function. If not supplied, the default name 'secant2' is used.

  Returns:
    A namedtuple containing the following fields.
      active: A boolean `Tensor` of shape [n]. Used internally by the procedure
        to indicate batch members on which there is work left to do.
      converged: A boolean `Tensor` of shape [n]. Indicates whether a point
        satisfying the Wolfe conditions has been found. If this is True, the
        interval will be degenerate (i.e. `left` and `right` below will be
        identical).
      failed: A boolean `Tensor` of shape [n]. Indicates if invalid function or
        gradient values were encountered (i.e. infinity or NaNs).
      num_evals: A scalar int32 `Tensor`. The total number of function
        evaluations made.
      left: Return value of value_and_gradients_function at the updated left
        end point of the interval.
      right: Return value of value_and_gradients_function at the updated right
        end point of the interval.
  """
  with tf.name_scope(name or 'secant2'):
    # This will always be s.t. left <= c <= right
    val_c = value_and_gradients_function(
        _secant(search_interval.left, search_interval.right))
    finished = _is_negative_inf(val_c.f)
    failed = ~search_interval.converged & (
        search_interval.failed | (~finished & ~is_finite(val_c)))
    converged = search_interval.converged | finished | (
        ~failed & _satisfies_wolfe(
            val_0, val_c, f_lim, sufficient_decrease_param, curvature_param))
    new_converged = converged & ~search_interval.converged
    val_left = val_where(new_converged, val_c, search_interval.left)
    val_right = val_where(new_converged, val_c, search_interval.right)

    initial_args = _Secant2Result(
        active=~failed & ~converged,
        converged=converged,
        failed=failed,
        num_evals=search_interval.func_evals + 1,
        left=val_left,
        right=val_right)

    def _apply_secant2_inner():
      return _secant2_inner(
          value_and_gradients_function,
          initial_args,
          val_0,
          val_c,
          f_lim,
          sufficient_decrease_param,
          curvature_param)

    return prefer_static.cond(
        tf.reduce_any(initial_args.active),
        _apply_secant2_inner,
        lambda: initial_args)


def _secant2_inner(value_and_gradients_function,
                   initial_args,
                   val_0,
                   val_c,
                   f_lim,
                   sufficient_decrease_param,
                   curvature_param):
  """Helper function for secant square."""
  # Apply the `update` function on active branch members to squeeze their
  # bracketing interval.
  update_result = update(value_and_gradients_function,
                         initial_args.left,
                         initial_args.right,
                         val_c,
                         f_lim,
                         active=initial_args.active)

  # Update active and failed flags, update left/right on non-failed entries.
  active = initial_args.active & ~update_result.failed
  failed = initial_args.failed | update_result.failed
  val_left = val_where(active, update_result.left, initial_args.left)
  val_right = val_where(active, update_result.right, initial_args.right)

  # Check if new `c` points should be generated.
  updated_left = active & tf.equal(val_left.x, val_c.x)
  updated_right = active & tf.equal(val_right.x, val_c.x)
  is_new = updated_left | updated_right

  next_c = tf.where(
      updated_left, _secant(initial_args.left, val_left), val_c.x)
  next_c = tf.where(
      updated_right, _secant(initial_args.right, val_right), next_c)
  in_range = (val_left.x <= next_c) & (next_c <= val_right.x)

  # Figure out if an extra function evaluation is needed for new `c` points.
  needs_extra_eval = tf.reduce_any(in_range & is_new)
  num_evals = initial_args.num_evals + update_result.num_evals
  num_evals = num_evals + tf.cast(needs_extra_eval, num_evals.dtype)

  next_args = _Secant2Result(
      active=active & in_range,  # No longer active if `c` is out of range.
      converged=initial_args.converged,
      failed=failed,
      num_evals=num_evals,
      left=val_left,
      right=val_right)

  def _apply_inner_update():
    next_val_c = prefer_static.cond(
        needs_extra_eval,
        (lambda: value_and_gradients_function(next_c)),
        (lambda: val_c))
    return _secant2_inner_update(
        value_and_gradients_function, next_args, val_0, next_val_c, f_lim,
        sufficient_decrease_param, curvature_param)

  return prefer_static.cond(
      tf.reduce_any(next_args.active),
      _apply_inner_update,
      lambda: next_args)


def _secant2_inner_update(value_and_gradients_function,
                          initial_args,
                          val_0,
                          val_c,
                          f_lim,
                          sufficient_decrease_param,
                          curvature_param):
  """Helper function for secant-square step."""
  # Fail if `val_c` is no longer finite.
  new_failed = initial_args.active & ~is_finite(val_c)
  active = initial_args.active & ~new_failed
  failed = initial_args.failed | new_failed

  # We converge when we find a point satisfying the Wolfe conditions, in those
  # cases we set `val_left = val_right = val_c`.
  found_wolfe = active & _satisfies_wolfe(
      val_0, val_c, f_lim, sufficient_decrease_param, curvature_param)
  val_left = val_where(found_wolfe, val_c, initial_args.left)
  val_right = val_where(found_wolfe, val_c, initial_args.right)
  converged = initial_args.converged | found_wolfe
  active = active & ~found_wolfe

  # If any active batch members remain, we apply the `update` function to
  # squeeze further their corresponding left/right bracketing interval.
  def _apply_update():
    update_result = update(
        value_and_gradients_function, val_left, val_right, val_c, f_lim,
        active=active)
    return _Secant2Result(
        active=tf.zeros_like(active),  # End of secant2, no actives anymore.
        converged=converged,
        failed=failed | update_result.failed,
        num_evals=initial_args.num_evals + update_result.num_evals,
        left=update_result.left,
        right=update_result.right)

  # Otherwise just return the current results.
  def _default():
    return _Secant2Result(
        active=active,
        converged=converged,
        failed=failed,
        num_evals=initial_args.num_evals,
        left=val_left,
        right=val_right)

  return prefer_static.cond(
      tf.reduce_any(active), _apply_update, _default)


_IntermediateResult = collections.namedtuple('_IntermediateResult', [
    'iteration',  # Number of iterations taken to bracket.
    'stopped',    # Boolean indicating whether bracketing/bisection terminated.
    'failed',     # Boolean indicating whether objective evaluation failed.
    'num_evals',  # The total number of objective evaluations performed.
    'left',       # Result of value_and_gradients_function at left end point.
    'right'       # Result of value_and_gradients_function at right end point.
])


def update(value_and_gradients_function, val_left, val_right, val_trial, f_lim,
           active=None):
  """Squeezes a bracketing interval containing the minimum.

  Given an interval which brackets a minimum and a point in that interval,
  finds a smaller nested interval which also brackets the minimum. If the
  supplied point does not lie in the bracketing interval, the current interval
  is returned.

  The following description is given in terms of individual points evaluated on
  a line function to be minimized. Note, however, the implementation also
  accepts batches of points allowing to minimize multiple line functions at
  once. See details on the docstring of `value_and_gradients_function` below.

  The requirement of the interval bracketing a minimum is expressed through the
  opposite slope conditions. Assume the left end point is 'a', the right
  end point is 'b', the function to be minimized is 'f' and the derivative is
  'df'. The update procedure relies on the following conditions being satisfied:

  '''
    f(a) <= f(0) + epsilon   (1)
    df(a) < 0                (2)
    df(b) > 0                (3)
  '''

  In the first condition, epsilon is a small positive constant. The condition
  demands that the function at the left end point be not much bigger than the
  starting point (i.e. 0). This is an easy to satisfy condition because by
  assumption, we are in a direction where the function value is decreasing.
  The second and third conditions together demand that there is at least one
  zero of the derivative in between a and b.

  In addition to the interval, the update algorithm requires a third point to
  be supplied. Usually, this point would lie within the interval [a, b]. If the
  point is outside this interval, the current interval is returned. If the
  point lies within the interval, the behaviour of the function and derivative
  value at this point is used to squeeze the original interval in a manner that
  preserves the opposite slope conditions.

  For further details of this component, see the procedure U0-U3 on page 123 of
  the [Hager and Zhang (2006)][2] article.

  Note that this function does not explicitly verify whether the opposite slope
  conditions are satisfied for the supplied interval. It is assumed that this
  is so.

  Args:
    value_and_gradients_function: A Python callable that accepts a real scalar
      tensor and returns an object that can be converted to a namedtuple.
      The namedtuple should have fields 'f' and 'df' that correspond to scalar
      tensors of real dtype containing the value of the function and its
      derivative at that point. The other namedtuple fields, if present,
      should be tensors or sequences (possibly nested) of tensors.
      In usual optimization application, this function would be generated by
      projecting the multivariate objective function along some specific
      direction. The direction is determined by some other procedure but should
      be a descent direction (i.e. the derivative of the projected univariate
      function must be negative at 0.).
      Alternatively, the function may represent the batching of `n` such line
      functions (e.g. projecting a single multivariate objective function along
      `n` distinct directions at once) accepting n points as input, i.e. a
      tensor of shape [n], and the fields 'f' and 'df' in the returned
      namedtuple should each be a tensor of shape [n], with the corresponding
      function values and derivatives at the input points.
    val_left: Return value of value_and_gradients_function at the left
      end point of the bracketing interval (labelles 'a' above).
    val_right: Return value of value_and_gradients_function at the right
      end point of the bracketing interval (labelles 'b' above).
    val_trial: Return value of value_and_gradients_function at the trial point
      to be used to shrink the interval (labelled 'c' above).
    f_lim: real `Tensor` of shape [n]. The function value threshold for
      the approximate Wolfe conditions to be checked for each batch member.
    active: optional boolean `Tensor` of shape [n]. Relevant in batching mode
      only, indicates batch members on which the update procedure should be
      applied. On non-active members the current left/right interval is returned
      unmodified.

  Returns:
    A namedtuple containing the following fields:
      iteration: An int32 scalar `Tensor`. The number of iterations performed
        by the bisect algorithm.
      stopped: A boolean `Tensor` of shape [n]. True for those batch members
        where the bisection algorithm terminated.
      failed: A boolean `Tensor` of shape [n]. True for those batch members
        where an error was encountered.
      num_evals: An int32 scalar `Tensor`. The number of times the objective
        function was evaluated.
      left: Return value of value_and_gradients_function at the updated left
        end point of the interval found.
      right: Return value of value_and_gradients_function at the updated right
        end point of the interval found.
  """
  # We should only update if the trial point is within the interval.
  within_range = (val_left.x < val_trial.x) & (val_trial.x < val_right.x)
  if active is not None:
    within_range = within_range & active

  # The new point is a valid left end point if it has negative slope
  # and the value at the point is not too large.
  valid_left = (val_trial.df < 0) & (val_trial.f <= f_lim)

  # If the trial point has a negative slope but the value at that point
  # is too high, bisect can narrow down an interval between the current left
  # and the trial point.
  needs_bisect = within_range & (val_trial.df < 0) & (val_trial.f > f_lim)

  # Note that if `~valid_left` it is because either:
  # - the slope at the trial point is positive, so it is a valid right
  #   point, or
  # - the needs_bisect condition is true.
  # In both cases we want to keep the current left and replace right
  # with the trial point.
  left = val_where(within_range & valid_left, val_trial, val_left)
  right = val_where(within_range & ~valid_left, val_trial, val_right)

  bisect_args = _IntermediateResult(
      iteration=tf.convert_to_tensor(0),
      stopped=~needs_bisect,
      failed=tf.zeros_like(within_range),  # i.e. all false.
      num_evals=tf.convert_to_tensor(0),
      left=left,
      right=right)
  return _bisect(value_and_gradients_function, bisect_args, f_lim)


def bracket(value_and_gradients_function,
            search_interval,
            f_lim,
            max_iterations,
            expansion_param=5.0):
  """Brackets the minimum given an initial starting point.

  Applies the Hager Zhang bracketing algorithm to find an interval containing
  a region with points satisfying Wolfe conditions. Uses the supplied initial
  step size 'c', the right end point of the provided search interval, to find
  such an interval. The only condition on 'c' is that it should be positive.
  For more details see steps B0-B3 in [Hager and Zhang (2006)][2].

  Args:
    value_and_gradients_function: A Python callable that accepts a real scalar
      tensor and returns a namedtuple containing the value filed `f` of the
      function and its derivative value field `df` at that point.
      Alternatively, the function may representthe batching of `n` such line
      functions (e.g. projecting a single multivariate objective function along
      `n` distinct directions at once) accepting n points as input, i.e. a
      tensor of shape [n], and return a tuple of two tensors of shape [n], the
      function values and the corresponding derivatives at the input points.
    search_interval: A namedtuple describing the current search interval,
      must include the fields:
      - converged: Boolean `Tensor` of shape [n], indicating batch members
          where search has already converged. Interval for these batch members
          wont be modified.
      - failed: Boolean `Tensor` of shape [n], indicating batch members
          where search has already failed. Interval for these batch members
          wont be modified.
      - iterations: Scalar int32 `Tensor`. Number of line search iterations
          so far.
      - func_evals: Scalar int32 `Tensor`. Number of function evaluations
          so far.
      - left: A namedtuple, as returned by value_and_gradients_function
          evaluated at 0, the left end point of the current interval.
      - right: A namedtuple, as returned by value_and_gradients_function,
          of the right end point of the current interval (labelled 'c' above).
    f_lim: real `Tensor` of shape [n]. The function value threshold for
      the approximate Wolfe conditions to be checked for each batch member.
    max_iterations: Int32 scalar `Tensor`. The maximum number of iterations
      permitted. The limit applies equally to all batch members.
    expansion_param: Scalar positive `Tensor` of real dtype. Must be greater
      than `1.`. Used to expand the initial interval in case it does not bracket
      a minimum.

  Returns:
    A namedtuple with the following fields.
      iteration: An int32 scalar `Tensor`. The number of iterations performed.
        Bounded above by `max_iterations` parameter.
      stopped: A boolean `Tensor` of shape [n]. True for those batch members
        where the algorithm terminated before reaching `max_iterations`.
      failed: A boolean `Tensor` of shape [n]. True for those batch members
        where an error was encountered during bracketing.
      num_evals: An int32 scalar `Tensor`. The number of times the objective
        function was evaluated.
      left: Return value of value_and_gradients_function at the updated left
        end point of the interval found.
      right: Return value of value_and_gradients_function at the updated right
        end point of the interval found.
  """
  already_stopped = search_interval.failed | search_interval.converged

  # We fail if there is a nan at the right end-point that prevents us from
  # making a decision, i.e., either a nan value or a finite value and a nan
  # derivative.
  failed = _bad_nan(search_interval.right)

  # If the right end is -inf, we have already found a minimum.  Passing along to
  # `_bisect` in this state will do the right thing, so just mark those as
  # stopped.
  finished = _is_negative_inf(search_interval.right.f)

  # If the value at the right end is finite and the slope at right end point is
  # positive, step B1 in [2], then the given initial points already bracket a
  # minimum.
  bracketed = _is_rising(search_interval.right)

  # Bisection is needed, step B2, if right end point almost works as a new left
  # end point but the objective value is too high.
  needs_bisect = _needs_bisect(search_interval.right, f_lim)

  # In these three cases bracketing is already `stopped` and there is no need
  # to perform further evaluations. Otherwise, assuming there are no `nan`s,
  # - The right-end point has a finite value,
  # - Whose derivative is non-positive, and
  # - Which is below `f_lim`.
  # This is then a valid left end-point, and the bracketing loop is needed to
  # expand the interval to the right, step B3, until the conditions are met.
  initial_args = _IntermediateResult(
      iteration=search_interval.iterations,
      stopped=already_stopped | failed | finished | bracketed | needs_bisect,
      failed=search_interval.failed | failed,
      num_evals=search_interval.func_evals,
      left=search_interval.left,
      right=search_interval.right)

  def _loop_cond(curr):
    return (curr.iteration <
            max_iterations) & ~tf.reduce_all(curr.stopped)

  def _loop_body(curr):
    """Main body of bracketing loop."""
    # The loop maintains the invariant that curr.stopped is true if we have
    # either: failed, successfully bracketed, or not yet bracketed but need to
    # bisect. On the only remaining case, step B3 in [2], `curr.right` is
    # actually a valid left end-point, and we need to expand to guess another
    # right end-point.
    new_right = value_and_gradients_function(expansion_param * curr.right.x)
    left = val_where(curr.stopped, curr.left, curr.right)
    right = val_where(curr.stopped, curr.right, new_right)

    # Updated the failed, bracketed, and needs_bisect conditions.
    failed = curr.failed | _bad_nan(right)
    finished = _is_negative_inf(right.f)
    bracketed = _is_rising(right)
    needs_bisect = _needs_bisect(right, f_lim)
    return [_IntermediateResult(
        iteration=curr.iteration + 1,
        stopped=curr.stopped | failed | finished | bracketed | needs_bisect,
        failed=failed,
        num_evals=curr.num_evals + 1,
        left=left,
        right=right)]

  bracket_result = tf.while_loop(
      cond=_loop_cond, body=_loop_body, loop_vars=[initial_args])[0]

  # Reset the input for the _bisect loop.
  # - `stopped` is now whether `_bisect` should feel already stopped
  # - `left` is adjusted
  #   - to equal `right` if we already found a minimum (i.e., -inf)
  #   - to the starting point if we're actually bisecting, per step B2
  finished = _is_negative_inf(bracket_result.right.f)
  bracketed = _is_rising(bracket_result.right)
  needs_bisect = _needs_bisect(bracket_result.right, f_lim)
  stopped = already_stopped | bracket_result.failed | finished | bracketed
  left = val_where(
      finished, bracket_result.right,
      val_where(needs_bisect, search_interval.left, bracket_result.left))
  bisect_args = bracket_result._replace(stopped=stopped, left=left)
  return _bisect(value_and_gradients_function, bisect_args, f_lim)


def bisect(value_and_gradients_function,
           initial_left,
           initial_right,
           f_lim):
  """Bisects an interval and updates to satisfy opposite slope conditions.

  Corresponds to the step U3 in [Hager and Zhang (2006)][2].

  Tolerates non-finite candidate right end-points.  Specifically:
  - If f(x) = -inf, that's a minimum, so we should just jump both end-points
    there and report success.
  - If f(x) = nan, fail (that is, stop trying to bisect and report failure).
  - If f(x) = +inf, that's fine, but just not an acceptable right
    end-point, so keep bisecting.

  In all of these cases, takes care to ignore the derivative, because (a) it
  doesn't inflence the outcome, and (b) if the value is infinite, the derivative
  should be `nan` (whether the client code arranged for that to be so or not).

  Args:
    value_and_gradients_function: A Python callable that accepts a real scalar
      tensor and returns a namedtuple containing the value filed `f` of the
      function and its derivative value field `df` at that point.
      Alternatively, the function may representthe batching of `n` such line
      functions (e.g. projecting a single multivariate objective function along
      `n` distinct directions at once) accepting n points as input, i.e. a
      tensor of shape [n], and return a tuple of two tensors of shape [n], the
      function values and the corresponding derivatives at the input points.
    initial_left: Return value of value_and_gradients_function at the left end
      point of the current bracketing interval.
    initial_right: Return value of value_and_gradients_function at the right end
      point of the current bracketing interval.
    f_lim: real `Tensor` of shape [n]. The function value threshold for
      the approximate Wolfe conditions to be checked for each batch member.

  Returns:
    A namedtuple containing the following fields:
      iteration: An int32 scalar `Tensor`. The number of iterations performed.
        Bounded above by `max_iterations` parameter.
      stopped: A boolean scalar `Tensor`. True if the bisect algorithm
        terminated.
      failed: A scalar boolean tensor. Indicates whether the objective function
        failed to produce a finite value.
      num_evals: A scalar int32 tensor. The number of value and gradients
        function evaluations.
      left: Return value of value_and_gradients_function at the left end
        point of the bracketing interval found.
      right: Return value of value_and_gradients_function at the right end
        point of the bracketing interval found.
  """
  failed = ~is_finite(initial_left) | tf.math.is_nan(initial_right.f)
  finished = _is_negative_inf(initial_right.f)
  bisect_args = _IntermediateResult(
      iteration=tf.convert_to_tensor(0),
      stopped=failed | finished | ~_needs_bisect(initial_right, f_lim),
      failed=failed,
      num_evals=tf.convert_to_tensor(0),
      left=val_where(finished, initial_right, initial_left),
      right=initial_right)
  return _bisect(value_and_gradients_function, bisect_args, f_lim)


def _bisect(value_and_gradients_function, initial_args, f_lim):
  """Actual implementation of bisect given initial_args in a _BracketResult."""
  def _loop_cond(curr):
    # TODO(b/112524024): Also take into account max_iterations.
    return ~tf.reduce_all(curr.stopped)

  def _loop_body(curr):
    """Narrow down interval to satisfy opposite slope conditions."""
    mid = value_and_gradients_function((curr.left.x + curr.right.x) / 2)

    # If the mid point has a value of -inf, we have found a minimum; jump
    # both ends of the interval there and exit.
    finished = _is_negative_inf(mid.f)

    # Otherwise, fail if the midpoint has a `nan` value or derivative, or if the
    # left/right points are so close to it that we can't distinguish them any
    # more.
    failed = (curr.failed |
              (~finished &
               (_bad_nan(mid) |
                tf.equal(mid.x, curr.left.x) |
                tf.equal(mid.x, curr.right.x))))

    # We will update only non-stopped and non-failed batch members.
    to_update = ~(curr.stopped | failed)

    # If the mid point has a negative slope and the function value at that point
    # is small enough, we can use it as a new left end point to narrow down the
    # interval.  Otherwise it becomes the new right end-point.
    update_left = (mid.df < 0) & (mid.f <= f_lim)
    left = val_where(to_update & (update_left | finished), mid, curr.left)
    right = val_where(to_update & (~update_left | finished), mid, curr.right)
    # If mid point has a finite value and a positive slope, then we have found a
    # suitable right end point to bracket a minimum within opposite slopes.
    # Otherwise, the mid point has a negative slope but the function value at
    # that point is too high to work as left end point (including +inf as a
    # possibility), so we are in the same situation in which we started the
    # loop.  We just update the right end point and continue.
    stopped = curr.stopped | failed | finished | _is_rising(right)

    return [_IntermediateResult(
        iteration=curr.iteration,
        stopped=stopped,
        failed=failed,
        num_evals=curr.num_evals + 1,
        left=left,
        right=right)]

  # The interval needs updating if the right end point has a negative slope and
  # the value of the function at that point is too high. It is not a valid left
  # end point but along with the current left end point, it encloses another
  # minimum. The loop above tries to narrow the interval so that it satisfies
  # the opposite slope conditions.
  return tf.while_loop(
      cond=_loop_cond, body=_loop_body, loop_vars=[initial_args])[0]


def _needs_bisect(val, f_lim):
  """Checks whether a candidate end-point calls for bisection.

  This is the case if the derivative at that point is negative, suggesting that
  this should be a left end-point, but the function value is too high, implying
  that it must instead be a right end-point but that it is unsuitable for secant
  steps and requires bisection steps.

  This check is careful about a +inf value, in which case the derivative is
  ignored and we move to bisection.

  Args:
    val: A namedtuple with fields `f` and `df` holding the function value and
      derivative at the point of interest.  May be batched.
    f_lim: Upper bound on acceptable function values.

  Returns:
    needs_bisect: Boolean Tensor mask giving whether each end-point in the batch
      calls for bisection.
  """
  return (val.f >= float('inf')) | ((val.df < 0) & (val.f > f_lim))


def _is_negative_inf(x):
  return x <= tf.constant(float('-inf'), dtype=x.dtype)


def _is_rising(val):
  """Checks that the value is finite and the derivative is positive.

  This is the stopping condition for the loop U3, and the condition for U1.  The
  check that the value is finite is necessary to ensure that the derivative is
  meaningful.

  Args:
    val: A namedtuple with fields `f` and `df` giving the value and gradient
      of the univariate objective, respectively.  May be batched.

  Returns:
    rising: A Boolean Tensor giving whether this point is a suitable right
      end-point for an interval subject to secant subdivision.
  """
  return tf.math.is_finite(val.f) & (val.df > 0)


def is_finite(val_1, val_2=None):
  """Checks if the supplied values are finite.

  Args:
    val_1: A namedtuple instance with the function value and derivative,
      as returned e.g. by value_and_gradients_function evaluations.
    val_2: (Optional) A namedtuple instance with the function value and
      derivative, as returned e.g. by value_and_gradients_function evaluations.

  Returns:
    is_finite: Scalar boolean `Tensor` indicating whether the function value
      and the derivative in `val_1` (and optionally in `val_2`) are all finite.
  """
  val_1_finite = tf.math.is_finite(val_1.f) & tf.math.is_finite(val_1.df)
  if val_2 is not None:
    return val_1_finite & tf.math.is_finite(val_2.f) & tf.math.is_finite(
        val_2.df)
  return val_1_finite


def _bad_nan(val):
  # If the value is +-inf, nan in the derivative doesn't matter because we
  # always know what to do.
  bad_nan_df = tf.math.is_finite(val.f) & tf.math.is_nan(val.df)
  return tf.math.is_nan(val.f) | bad_nan_df


def _satisfies_wolfe(val_0,
                     val_c,
                     f_lim,
                     sufficient_decrease_param,
                     curvature_param):
  """Checks whether the Wolfe or approx Wolfe conditions are satisfied.

  The Wolfe conditions are a set of stopping criteria for an inexact line search
  algorithm. Let f(a) be the function value along the search direction and
  df(a) the derivative along the search direction evaluated a distance 'a'.
  Here 'a' is the distance along the search direction. The Wolfe conditions are:

    ```None
      f(a) <= f(0) + delta * a * df(0)   (Armijo/Sufficient decrease condition)
      df(a) >= sigma * df(0)             (Weak curvature condition)
    ```
  `delta` and `sigma` are two user supplied parameters satisfying:
   `0 < delta < sigma <= 1.`. In the following, delta is called
   `sufficient_decrease_param` and sigma is called `curvature_param`.

  On a finite precision machine, the Wolfe conditions are difficult to satisfy
  when one is close to the minimum. Hence, Hager-Zhang propose replacing
  the sufficient decrease condition with the following condition on the
  derivative in the vicinity of a minimum.

    ```None
      df(a) <= (2 * delta - 1) * df(0)  (Approx Wolfe sufficient decrease)
    ```
  This condition is only used if one is near the minimum. This is tested using

    ```None
      f(a) <= f(0) + epsilon * |f(0)|
    ```
  The following function checks both the Wolfe and approx Wolfe conditions.
  Here, `epsilon` is a small positive constant. In the following, the argument
  `f_lim` corresponds to the product: epsilon * |f(0)|.

  Args:
    val_0: A namedtuple, as returned by value_and_gradients_function
      evaluated at 0.
    val_c: A namedtuple, as returned by value_and_gradients_function
      evaluated at the point to be tested.
    f_lim: Scalar `Tensor` of real dtype. The function value threshold for
      the approximate Wolfe conditions to be checked.
    sufficient_decrease_param: Positive scalar `Tensor` of real dtype.
      Bounded above by the curvature param. Corresponds to 'delta' in the
      terminology of [Hager and Zhang (2006)][2].
    curvature_param: Positive scalar `Tensor` of real dtype. Bounded above
      by `1.`. Corresponds to 'sigma' in the terminology of
      [Hager Zhang (2005)][1].

  Returns:
    is_satisfied: A scalar boolean `Tensor` which is True if either the
      Wolfe or approximate Wolfe conditions are satisfied.
  """
  exact_wolfe_suff_dec = (sufficient_decrease_param * val_0.df >=
                          tf.math.divide_no_nan(val_c.f - val_0.f, val_c.x))
  wolfe_curvature = val_c.df >= curvature_param * val_0.df
  exact_wolfe = exact_wolfe_suff_dec & wolfe_curvature
  approx_wolfe_applies = val_c.f <= f_lim
  approx_wolfe_suff_dec = ((2 * sufficient_decrease_param - 1) * val_0.df
                           >= val_c.df)
  approx_wolfe = approx_wolfe_applies & approx_wolfe_suff_dec & wolfe_curvature
  is_satisfied = exact_wolfe | approx_wolfe
  return is_satisfied


def _secant(val_a, val_b):
  """Returns the secant interpolation for the minimum.

  The secant method is a technique for finding roots of nonlinear functions.
  When finding the minimum, one applies the secant method to the derivative
  of the function.
  For an arbitrary function and a bounding interval, the secant approximation
  can produce the next point which is outside the bounding interval. However,
  with the assumption of opposite slope condtion on the interval [a,b] the new
  point c is always bracketed by [a,b]. Note that by assumption,
  f'(a) < 0 and f'(b) > 0.
  Hence c is a weighted average of a and b and thus always in [a, b].

  Args:
    val_a: A namedtuple with the left end point, function value and derivative,
      of the current interval (i.e. a).
    val_b: A namedtuple with the right end point, function value and derivative,
      of the current interval (i.e. b).

  Returns:
    approx_minimum: A scalar real `Tensor`. An approximation to the point
      at which the derivative vanishes.
  """
  return tf.math.divide_no_nan(val_a.x * val_b.df - val_b.x * val_a.df,
                               val_b.df - val_a.df)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# This file is auto-generated by substrates/meta/rewrite.py
# It will be surfaced by the build system as a symlink at:
#   `tensorflow_probability/substrates/jax/optimizer/linesearch/internal/hager_zhang_lib.py`
# For more info, see substrate_runfiles_symlinks in build_defs.bzl
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
