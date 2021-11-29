
from extremals import *

RWD.__doc__ = \
"""
Relative Weighted Distance

:param value: Either a number or a pandas series
:param mean,unstds: numbers

:return: the value (value-mean)/unstd except special cases

In :py:func:`Normalize` you can read more about this function.
"""

TWD.__doc__ =\
"""
Total Weighted Distance

:param list values, means, unstds: lists of numbers of the same length

:return: a number. 

It returns the sum of

.. code-block:: python
    
    abs(xt.RWD(values[i],means[i],unstds[i]))

where the sum runs over the indexes ``i`` for which ``values[i]`` is not ``NaN``.

This function is used when ``keys = [k_1, ..., k_l]`` are columns of a dataframe ``data`` and ``x`` is an index of data, by setting

.. code-block:: python
    
    values[i]  = data[k_i].loc[x]
    means[i]   = data[k_i].mean()
    un_stds[i] = the un-normalized standard deviation of data[k_i]

In this case:

.. code-block:: python

    TWD(values, means, un_stds) = abs(xt.Normalize(data[keys])).sum().loc[x]

The contribution ``abs(xt.RWD(values[i],means[i],un_stds[i]))`` measures
the distance of ``data[k_i].loc[x]`` from the mean of ``data[k_i]``. Thus the higher the value of the sum, the farther are the values ``values[i]``
from the mean of the corresponding column.
Moreover those contribution are uniform among the various columns as we are using the normalization process described in :py:func:`Normalize`.
"""

Normalize.__doc__ = \
"""
Returns a normalized copy of ``obj``.

:param obj: numeric series or dataframe
:type obj: pd.Series or pd.DataFrame
:param bool dropna: if True and ``obj`` is a series, then ``NaN`` values are discarded; has no effect if ``obj`` is a dataframe, default True

:rtype: same type of ``obj``

If ``obj`` is a dataframe, the function is applied to all columns with ``dropna = False``. So assume ``obj`` is a series and let

.. code-block:: python

    nor = xt.Normalize(obj)

its normalization. Except special cases, ``nor`` is 

.. code-block:: python

    nor = (obj - mean)/unstd

where ``mean = obj.mean()`` is the mean of ``obj``, while ``unstd`` is the un-normalized standard deviation

.. math::

    unstd = \sqrt{\sum_i (obj[i]-mean)^2}

where ``i`` runs on the set of indexes of ``obj`` such that ``obj[i]`` is not ``NaN``. If ``dropna`` is True, ``NaN`` values in ``nor`` are discarded.

The new series ``nor`` has the following properties: it has mean 0, un-normalized standard deviation 1, all its values lie between -1 and 1 and their squares sum up to 1.
In particular normalizing ``nor`` again has no effect. Moreover the normalization of a positive multiple of ``obj`` is still ``nor``.

If x is an index of obj, the closer is ``nor.loc[x]`` to 1 or -1, the farther is the ``obj.loc[x]`` from the mean of ``obj``.

We have prefered the un-normalized standard deviation over the classical one, because otherwise the sum of the squares of the normalization would give us the length
of the series, rather than 1, making more difficult to understand how "extremal" is a value. Clearly any normalization obtained as ``(obj+a)/b`` for constants ``a,b`` with ``b`` positive
makes no difference when sorting the indexes of ``obj`` by their value.

``Warning`` There are some special cases when the normalization must be defined in a different way.

- If the series contains ``numpy.inf`` the normalization process is not possible, therefore the original series is returned.

- If ``unstd = 0`` the normalization cannot be obtained modding out by ``unstd``. On the other hand ``unstd = 0`` \
means that all non ``NaN`` values are the same and coincide with the mean of ``obj``. Therefore ``nor`` is ``obj`` with all non ``NaN`` values \
replaced by zeros.


Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    nor_data = xt.Normalize(data)
    
    # nor_data is the dataframe
           col1      col2      col3
    a -0.149131  0.215801 -0.237982
    b  0.918013  0.376647  0.729637
    c -0.171134 -0.142884 -0.413199
    d -0.215140       NaN  0.337359
    e       NaN  0.066215  0.036613
    f -0.083122 -0.000536 -0.198754
    g  0.059897  0.207759 -0.290286
    h -0.094124  0.059781       NaN
    i -0.083122  0.074257       NaN
    l -0.182136 -0.857039  0.036613


    nor_col3 = xt.Normalize(data['col3'], dropna = True)
    
    # nor_col3 is the series
    a   -0.237982
    b    0.729637
    c   -0.413199
    d    0.337359
    e    0.036613
    f   -0.198754
    g   -0.290286
    l    0.036613
    Name: col3, dtype: float64

"""

Test.__doc__ = \
"""
This class implements the idea of a test to run on a dataframe.
The output, returned via :py:func:`Test.Apply`, is a sorted series.

:param keys: list of columns to use, default ``None``: all columns used
:type keys: list
:param function: function, default ``None``
:type function: function
:param args: list of optional arguments for ``function``, default empty
:type args: list
:param bool normalized: If True, the resulting series will be normalized (see :py:func:`Normalize`), default False
:param name: name of the output series, default ``None``
:type name: str

The attribute ``function`` takes a list as input: if ``l`` is the length of ``keys``, such list is divided into two parts: the first ``l`` elements will be the values of a row
of some dataframe, the others are the elements of ``args``.

Alternatively, one can change the methods :py:func:`Test.GetArgs` and :py:func:`Test.GetValue` and ignore the attributes 
``function`` and ``args``.

Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    test = xt.Test(function = lambda x : (x[1]-x[2])**2/x[0], name = 'custom' )
    
``function`` is some random function. ``keys`` not specified means that all columns will be used

.. code-block:: python

    result = test.Apply(data)
    
    # result is the series
    f    1.562500e+02
    b    1.587600e+02
    g    4.455000e+02
    a    3.333333e+03
    c    1.201216e+04
    l             inf # A division by zero warning is raised
    Name: custom, dtype: float64

Columns ``d,e,h,i`` are discarded and the series is sorted


.. code-block:: python

    test = xt.Test(function = lambda x : sum(x), name='Sum', normalized = True)
    result = test.Apply(data)
    
    # result is the (normalized) series
    l   -0.762235
    c   -0.168376
    f   -0.005086
    a    0.176427
    g    0.190890
    b    0.568380
    Name: Sum, dtype: float64
"""

Test.Apply.__doc__ = \
"""
Creates and returns a new pandas series obtained applying ``self.function`` on the
values of dataframe ``data`` corresponding to the columns listed in ``self.keys``.

:param data: dataframe
:type data: pandas.DataFrame
:param sort: if True the resulting series is sorted, default True
:type sort: bool

:rtype: ``pandas.Series`` with name ``self.name``

"""

FilterDatakeys.__doc__ = \
"""
Filter ``keys`` from non numeric columns and ``data`` for duplicated columns.

:param pandas.DataFrame data: dataframe
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty

:return: ``[keys, data]`` after the filtering
:rtype: list 

Columns whose type is not in :py:attr:`Test.numtype_list` are discarded.
"""

Test.GetArgs.__doc__ = \
"""
Loads the optional arguments ``self.args`` or any other data needed.

:param pandas.DataFrame data: dataframe
"""
Test.GetValue.__doc__ = \
"""
Return ``self.function`` applied on the list ``arr+self.args``

:param list arr: this will be a list of values of a row in a dataframe

:rtype: numeric result
"""

TWDTest.__doc__ = \
"""
Returns a Total Weighted Distance test

:param list keys: list of columns to use, default ``None``: all columns used
:param str name: optional name, default ``'TWD'``

If ``data`` is a dataframe and ``keys`` is a list of columns, we can run

.. code-block:: python

    twd = xt.TWDTest(keys)
    series = twd.Apply(data)

The resulting pandas.Series ``series`` has the same index as data. For a row ``x`` the corresponding value is

.. code-block:: python

    means = data[keys].mean()
    series.loc[x] = extremals.TWD(data[keys].loc[x], means, un_stds])

while ``un_stds`` is the sequence of un-normalized standard deviations of each column (taking into account ``NaN`` values).
See :py:func:`.TWD`. As the value of ``Series`` in ``x`` is a uniform contribution of ``errors`` coming from each column, rows with higher values are somehow
special. One can use

.. code-block:: python

    bounded_series = xt.OutOfBound(series, [0,0.01])

to extrapolate the 1% higher values. See :py:func:`.OutOfBound`.

Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    twd = xt.TWDTest() # all columns will be used
    result = twd.Apply(data)
    
    # result is the sorted series
    e    0.102827
    h    0.153905
    i    0.157379
    f    0.282413
    d    0.552499
    g    0.557941
    a    0.602914
    c    0.727218
    l    1.075787
    b    2.024297
    Name: TWD, dtype: float64

``l`` and ``b`` have higher values. This is consistent with the special values of ``data.loc['l']`` and ``data.loc['b']``

.. code-block:: python

    twd3 = xt.TWDTest(keys = ['col3'])
    result3 = twd3.Apply(data)
    
    # result3 is the series
    e    0.036613
    l    0.036613
    f    0.198754
    a    0.237982
    g    0.290286
    d    0.337359
    c    0.413199
    b    0.729637
    Name: TWD, dtype: float64
    
``result3`` can also be obtained as

.. code-block:: python

    abs(xt.ColTest('col3', normalized = True).Apply(data)).sort_values()
        """

TWDTest.GetArgs.__doc__ = TWDTest.GetValue.__doc__ = ""

TWDTest.Apply.__doc__ = \
"""
Creates and returns a new pandas series as explained in :py:class:`.TWDTest`.

:param data: dataframe
:type data: pandas.DataFrame
:param sort: if True the resulting series is sorted, default True
:type sort: bool

:rtype: ``pandas.Series`` with name ``self.name``

"""

ColTest.__doc__ = \
"""
This is a simple test on one column ``key``. The function ``self.function`` is the ``identity``: for each row return the value at that row.
This test is interesting if used with ``normalized = True``.

:param str key: column key of some dataframe
:param bool normalized: if True, the test is normalized, default False
:param name: optional name, default ``None``: ``self.name`` is set to ``key``
:type name: str or ``None``

Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    ctest = xt.ColTest('col1')
    result = ctest.Apply(data)
    
    # result is just data['col1'] sorted and without NaN values.
    d     -3.0
    l      0.0
    c      1.0
    a      3.0
    h      8.0
    f      9.0
    i      9.0
    g     22.0
    b    100.0
    Name: col1, dtype: float64

    ctest.normalized = True
    # or ctest = extremal.ColTest('col1', normalized = True)
    result_nor = ctest.Apply(data)
    
    # result_nor is the normalization of result
    d   -0.215140
    l   -0.182136
    c   -0.171134
    a   -0.149131
    h   -0.094124
    f   -0.083122
    i   -0.083122
    g    0.059897
    b    0.918013
    Name: col1, dtype: float64
"""

ColDiffTest.__doc__ = \
"""
It tests the difference between columns key1 and key2: the function ``self.function`` maps a row to the difference of the values corresponding to the two columns.

:param str key1: column key of some dataframe
:param str key2: column key of some dataframe
:param bool normalized: if True, the test is normalized, default False
:param name: optional name, default ``None``: ``self.name`` is set to ``key2 - key1``
:type name: str or ``None``

Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    cdtest = xt.ColDiffTest('col1','col2')
    result = cdtest.Apply(data)
    
    # result is just data['col2'] - data['col1'] sorted and without NaN values.
    l   -567.0
    c   -124.0
    f    -43.5
    h     -5.0
    i      3.0
    g     73.0
    a     97.0
    b    100.0
    Name: (col2 - col1), dtype: float64


    cdtest.normalized = True
    # or cdtest = extremal.ColDiffTest('col1','col2', normalized = True)
    result_nor = cdtest.Apply(data)
    
    # result_nor is the normalization of result
    l   -0.877143
    c   -0.113267
    f    0.025542
    h    0.091928
    i    0.105723
    g    0.226426
    a    0.267809
    b    0.272982
    Name: (col2 - col1), dtype: float64
"""


OutOfBound.__doc__ = \
"""
Returns a dataframe or a series which is a concatenation of the lowest values of ``obj`` followed by the highest ones, depending on ``low``, ``high`` and ``bound``.

:param obj: numeric series or dataframe
:type obj: pandas.Series or pandas.DataFrame 
:param low,high: default 0
:type low,high: numbers
:param str key: sorting column, default ``None``
:param list bound: list of two numbers, default empty

:rtype: same type as ``obj``

If ``bound`` is a list of two numbers, those are used instead of ``low`` and ``high``. The argument ``key`` is used only when ``obj`` is a dataframe and
specifies the column according to which order the rows in the returned dataframe.

The two numbers ``low`` and ``high`` in ``bound`` have the following meaning:

- If ``low`` and ``high`` are non negative integers, the resulting object is a concatenation of the ``low`` lowest values in ``obj``, \
followed by its ``high`` highest values.
- If ``low`` (resp. ``high``) is strictly between 0 and 1, it will be interpreted as a percentage: \
the resulting obj will have the ``(low*100)%`` of lowest values (resp. ``(high*100)%`` of higher values).
- if either ``low`` or ``high`` is negative, no bound is applied.
   

Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    s = data['col1']
    
    # s is the series
    a      3.0
    b    100.0
    c      1.0
    d     -3.0
    e      NaN
    f      9.0
    g     22.0
    h      8.0
    i      9.0
    l      0.0
    Name: col1, dtype: float64

    t1 = xt.OutOfBound(s,2,3)
    
    # t1 is the series:
    d     -3.0
    l      0.0 # the 2 lowest
    i      9.0
    g     22.0
    b    100.0 # the 3 higher
    Name: col1, dtype: float64

    t2 = xt.OutOfBound(s, bound = [0,0.3])
   
    # t2 is the series:
    g     22.0
    b    100.0  # only the highest 30%
    Name: col1, dtype: float64

As the ``NaN`` value has been discarded, there are only 9 elements left.
Their 30% is 0.3*9 = 2.7, which is rounded to 2.

As ``-1`` means no bound, the following series coincide

.. code-block:: python

    xt.OutOfBound(s, -1)
    s.sort_values().dropna()

When we apply :py:func:`OutOfBound` to a dataframe the value of ``key`` must be specified. This new input
can change both the size and the order of the returned dataframe, as the following example shows.

.. code-block:: python
    
    new_data = pd.DataFrame(
                {'col1' : [1, 2, 3, 4],
                 'col2' : [None, 4 , None, 2]},
                 index = ['a', 'b', 'c', 'd']
                )
    
    # new_data is the dataframe
       col1  col2
    a     1   NaN
    b     2   4.0
    c     3   NaN
    d     4   2.0

    d1 = xt.OutOfBound(new_data,0,0.5, key = 'col1')
    
    # d1 is the dataframe
       col1  col2
    c     3   NaN
    d     4   2.0
    
    d2 = xt.OutOfBound(new_data,0,0.5, key = 'col2')

    # d2 is the dataframe
       col1  col2
    b     2   4.0

For ``d1`` the order is given by the first column and the number of rows is ``0.5*4=2``. For ``d2`` instead, the order is given by
the second column and the number or rows is ``0.5*(4-2) = 1`` because we have to drop the ``NaN`` values.
"""

GetColTests.__doc__= \
"""
Returns a list of :py:class:`.ColTest`, one for each  specified column.

:param pandas.DataFrame data: dataframe
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param bool normalized: parameter passed to the returned tests

:rtype: list 
"""

GetDiffTests.__doc__ = \
"""
Returns a list of :py:class:`.ColDiffTest`, one for each pair of specified columns.

:param pandas.DataFrame data: dataframe
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param bool normalized: parameter passed to the returned tests

:rtype: list 
"""

Extremals.__doc__ = \
"""
This class allows to create a new dataframe as results of multiple tests and to look for the extremals rows.

:param pandas.DataFrame data: dataframe, which is then copied in ``self.data``
:param list tests: list of :py:class:`.Test` instances to run on ``data``, default empty

Examples:

.. code-block:: python

    tests = ... # define some tests
    data = ... # your dataframe
    extr = xt.Extremals(data, tests)
    results = extr.Run()

``results`` is a dataframe with the results of the tests, see :py:func:`Extremals.Run`.
It can be accessed also with ``extr.results``. We can look at the bounded results using :py:func:`Extremals.OutOfBound`.


Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    tests = [
        xt.ColTest('col3', normalized = True),
        xt.Test(function = lambda x: x[2] - x[1] -x[0], name = 'custom'),
        xt.TWDTest(name = 'TWD on data')
    ]

    extr = xt.Extremals(data, tests)
    result = extr.Run()
    
    # result is the dataframe
           col3  custom  TWD on data       TWD
    i       NaN     NaN     0.157379  0.268680
    h       NaN     NaN     0.153905  0.270682
    e  0.036613     NaN     0.102827  0.336722
    d  0.337359     NaN     0.552499  0.378391
    f -0.198754    28.5     0.282413  0.422102
    a -0.237982  -103.0     0.602914  0.479087
    c -0.413199   108.6     0.727218  0.569419
    g -0.290286  -121.0     0.557941  0.585008
    l  0.036613   588.0     1.075787  1.131579
    b  0.729637  -226.0     2.024297  1.955023
    
The last column is the result of a :py:class:`TWDTest` on the first three columns and it is automatically run, unless ``twd = False`` is passed to ``extr.Run``.
We can bound the results using

.. code-block:: python

    b_result = extr.OutOfBound(0, 0.2)
    
    # b_result is the dataframe
           col3  custom  TWD on data       TWD
    l  0.036613   588.0     1.075787  1.131579
    b  0.729637  -226.0     2.024297  1.955023
    
It contains the 20% highest rows of ``result``, computed with respect to the column ``'TWD'``.

.. code-block:: python

    bb_result = extr.OutOfBound(0, 0.2, key = 'custom')
    
    # bb_result is the dataframe
       col3  custom  TWD on data       TWD
    l  0.036613   588.0     1.075787  1.131579
    
Now the 20% and the sorting are computed with respect to the column 'custom', after all ``NaN`` values have been discarded.
``bb_result`` can also be obtained as

.. code-block:: python

    xt.OutOfBound(extr.results, bound = [0, 0.2], key = 'custom')
"""

Extremals.Run.__doc__ = \
"""
Runs the tests

:param bool twd: if True, applies a :py:class:`.TWDTest` to the results of the tests in ``self.tests``, default True

:rtype: pandas.DataFrame ``self.results``
    
It first applies each test in ``self.test`` on ``self.data``. The resulting series are then packed into a new dataframe ``self.results``.
If ``twd`` is set to True (which is default), it runs a :py:class:`.TWDTest` on the whole ``self.results``, appending it as last column
and sorting the dataframe with respect to it. Notice that the ``TWD`` column (which is not normalized) does not depend on the ``normalized`` attributes
of the tests in ``self.tests``.

``self.results`` is also returned as output.
"""


Extremals.OutOfBound.__doc__ = \
"""
Returns a dataframe with the lowest values followed by the highest ones, depending on ``low``, ``high`` and ``bound``.

:param low,high: default 0
:type low,high: numbers
:param str key: sorting column, default ``'TWD'``
:param list bound: list of two numbers, default empty

:rtype: pandas.DataFrame

If ``bound`` is a list of two numbers, those are used instead of ``low`` and ``high``. It calls :py:func:`OutOfBound` on ``self.results`` with the same arguments.

Examples

.. code-block:: python

    extr = ... # An instance of xt.Extremals
    results = extr.Run()
    bounded_res = extr.OutOfBound(10,0.02)

``bounded_res`` contains the lowest 10 elements of ``results``, followed by %2 of the highest one, with respect to the ``'TWD'`` column created automatically
with ``xt.Run()``. See also :py:class:`.Extremals`
"""

Extremals.SetColTests.__doc__ = \
"""
Set ``self.tests`` via :py:func:`.GetColTests`
"""


Extremals.SetDiffTests.__doc__ = \
"""
Set ``self.tests`` via :py:func:`.GetDiffTests`
"""

Extremals.NormalizeTests.__doc__ = \
"""
:param bool value: default True

Set the attribute ``normalized`` to ``value`` for all :py:class:`.Test` instances in ``self.tests``. 
"""

ExtremalsCol.__doc__ = \
"""
This class applies  a series of :py:class:`.ColTest` to the dataframe ``data``, one for each specified column.

:param pandas.DataFrame data: dataframe, which is then copied in ``self.data``
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param bool normalized: if True, the tests are normalized, default False


Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    xt.ExtremalsCol(data, keys = ['col1', 'col3'])
    result = ecol.Run()
    
    # result is the dataframe
        col1  col3       TWD
    e    NaN  21.0  0.036613
    i    9.0   NaN  0.083122
    h    8.0   NaN  0.094124
    l    0.0  21.0  0.218748
    f    9.0   3.0  0.281877
    g   22.0  -4.0  0.350183
    a    3.0   0.0  0.387113
    d   -3.0  44.0  0.552499
    c    1.0 -13.4  0.584334
    b  100.0  74.0  1.647650

``result`` is a concatenation of the first and third columns of ``data`` (up to sorting) and a :py:class:`TWDTest` run on them.    
``result`` is sorted according to this last column. 

.. code-block:: python
    
    ecol.NormalizeTests(True)
    # or ecol = xt.ExtremalsCol(data, keys = ['col1', 'col3'], normalized = True)
    nor_result = ecol.Run()
    
    # nor_result is the dataframe
           col1      col3       TWD
    e       NaN  0.036613  0.036613
    i -0.083122       NaN  0.083122
    h -0.094124       NaN  0.094124
    l -0.182136  0.036613  0.218748
    f -0.083122 -0.198754  0.281877
    g  0.059897 -0.290286  0.350183
    a -0.149131 -0.237982  0.387113
    d -0.215140  0.337359  0.552499
    c -0.171134 -0.413199  0.584334
    b  0.918013  0.729637  1.647650

``nor_result`` is obtained from ``result`` normalizing the two columns. We would obtain the same result with

.. code-block:: python

    xt.ExtremalsCol(xt.Normalize(data), keys = ['col1', 'col3']).Run()

You can now bound the result using the :py:func:`Extremals.OutOfBound` method. See :py:class:`Extremals`.
"""


ExtremalsDiff.__doc__ = \
"""
This class applies a series of :py:class:`ColDiffTest` to the dataframe ``data``, one for each pair of specified columns.

:param pandas.DataFrame data: dataframe, which is then copied in ``self.data``
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param bool normalized: if True, the tests are normalized, default False



Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    ediff = xt.ExtremalsDiff(data)
    result = ediff.Run()
    
    # result is the dataframe
       (col2 - col1)  (col3 - col1)  (col3 - col2)       TWD
    e            NaN            NaN           14.0  0.076655
    h           -5.0            NaN            NaN  0.091928
    i            3.0            NaN            NaN  0.105723
    f          -43.5           -6.0           37.5  0.139379
    c         -124.0          -14.4          109.6  0.398671
    a           97.0           -3.0         -100.0  0.561860
    d            NaN           47.0            NaN  0.737463
    g           73.0          -26.0          -99.0  0.871779
    b          100.0          -26.0         -126.0  0.962763
    l         -567.0           21.0          588.0  2.083459
"""

TWDExtremals.__doc__ = \
"""
Applies a :py:class:`TWDTest` on ``data``

:param data: dataframe or series
:param list bound: list of two numbers following the same rules in :py:func:`.OutOfBound`, default ``[-1,-1]``: no bound applied
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param str name: name of the returned series, default ``'TWD'``

:rtype: pandas.Series


Examples:

.. code-block:: python
    
    data = ... # your dataframe
    keys = ... # list of columns you are interesting in
    twd_series = xt.TWDExtremals(data, keys = keys)

If one row ``x`` of ``data[keys]`` have values very far from the mean of the corresponding column then ``twd_series[x]`` will be higher than other rows.
Moreover the contribution of each column is uniform, because of the normalization process used (see :py:func:`Normalize`).

``twd_series`` can also be obtained running any of the following commands

.. code-block:: python
    
    xt.TWDExtremals(data[keys])
    xt.TWDTest(keys).Apply(data)
    xt.TWDTest().Apply(data[keys])
    
Up to sorting the rows, the concatenation of ``data[key]`` and ``twd_series`` in one dataframe is obtained with

.. code-block:: python
    
    xt.AddTWDTest(data[keys])
    
Any of the following commands will gave us the 2% higher values of ``twd_series``

.. code-block:: python

    xt.OutOfBound(twd_series, 0,0.02)
    xt.TWDExtremals(data[keys], bound = [0,0.02])
    

Now consider the dataframe :ref:`data <data>`

.. code-block:: python
    
    keys = ['col1', 'col3']
    twd_series = xt.TWDExtremals(data[keys])
    
    # twd_series is the last column of
        col1  col3       TWD
    e    NaN  21.0  0.036613
    i    9.0   NaN  0.083122
    h    8.0   NaN  0.094124
    l    0.0  21.0  0.218748
    f    9.0   3.0  0.281877
    g   22.0  -4.0  0.350183
    a    3.0   0.0  0.387113
    d   -3.0  44.0  0.552499
    c    1.0 -13.4  0.584334
    b  100.0  74.0  1.647650
    
Row ``b`` has values far away from the means and therefore its value on ``twd_series`` is higher.
"""

PurgeTWD.__doc__=\
"""
Iteratively applies a :py:class:`TWDTest` on ``data``, removing the ``high`` "worst" elements from ``data`` in ``steps`` steps.

:param data: a dataframe or a series
:param number high: positive number, expressing the number or percentage of items to remove
:param int steps: steps used, default 1
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param bool verbose: if True, it prints how many elements are removed each step, default False

:return: list of two dataframe
:rtype: list 

The number ``high`` must be positive. If ``high < 1`` it will be interpreted as a percentage, otherwise it will denotes the total number of elements
that will be removed. The removal of those elements is obtained in ``steps`` steps. In each one, a :py:class:`TWDTest` is applied on the remaining dataframe and a new set of
indexes is removed.

With ``keys`` and ``exclude`` it is possible to choose the columns to use in the test, so that it will not depend on the other ones.

At the end of the process, it returns two dataframes, in order the one of purged indexes and the one of remaining indexes. The indexes of the "purged" dataframe are ordered
according to the order of their removal.

Applying this purging operation in several steps refines the search of anomalous rows. At any step, the marginal rows selected to be drop make the means unbalanced 
toward their values. Removing them and updating the means give a more "accurate" situation for choosing the next new marginal elements to drop.
In conclusion a higher number of ``steps`` determines a better choice of extremal rows.

Examples:

.. code-block:: python
    
    data = ... # your dataframe
    keys = ... # list of columns you are interesting in
    purged, good = xt.PurgeTWD(data, high = 0.05, steps = 10, keys = keys)

With this command we remove 5% of the indexes in 10 steps from ``data``, but only looking at the columns in ``keys``. ``purged`` and ``good`` are
the complementary dataframe of purged and "good" indexes.

Now consider the dataframe :ref:`data <data>`

.. code-block:: python

    purged, good = xt.PurgeTWD(data, high = 0.3, steps = 1)
    
    # purged is the dataframe
        col1   col2  col3
    b  100.0  200.0  74.0
    l    0.0 -567.0  21.0
    c    1.0 -123.0 -13.4

In ``purged`` we removed 30% of ``data`` (that his ``0.3*10 ~ 3`` rows) in one cut. 
For convenience let's print the whole ``data`` ordered via the :py:class:`AddTWDTest` on it:

.. code-block:: python

    data_ordered = xt.AddTWDTest(data)
   
    #data_ordered is the dataframe
        col1   col2  col3   TWD
    e    NaN    7.0  21.0  0.10
    h    8.0    3.0   NaN  0.15
    i    9.0   12.0   NaN  0.16
    f    9.0  -34.5   3.0  0.28
    d   -3.0    NaN  44.0  0.55
    g   22.0   95.0  -4.0  0.56
    a    3.0  100.0   0.0  0.60
    c    1.0 -123.0 -13.4  0.73
    l    0.0 -567.0  21.0  1.08
    b  100.0  200.0  74.0  2.02
    
As you can see ``purged`` consists of the last three rows of ``data_ordered``, provided we remove the last column and
we reverse the order of the rows. Rows ``b`` and ``l`` are numerically different from the others, thus it makes sense they are
highlighted as special. Same is true for ``c``, but I can't help to think that also ``g`` looks even more different. Why is it not
ranking higher in the :py:class:`TWDTest`? It is because ``b`` is having too much an impact in the computation of the mean, for instance
``data['col1'].mean()`` is around 16.5. Same for ``l`` in the second column.

The solution is to first drop the last two rows and then computes the means again. This exactly what :py:func:`PurgeTWD` does increasing the steps:

.. code-block:: python

    purged2, good2 = xt.PurgeTWD(data, high = 0.3, steps = 2)
    
    # purged2 is the dataframe
        col1   col2  col3
    b  100.0  200.0  74.0
    l    0.0 -567.0  21.0
    g   22.0   95.0  -4.0

This time after ``b`` and ``l``, it appears the row ``g``. 

In theory the best solution would be to set ``steps`` as the number of elements we want to remove,
that is dropping one row at a time (it would have no effect in our example). Clearly this is not possible for big dataframes, but certainly the higher the number
of steps, the more accurate is the choice of the "bad" elements.

"""

AddTests.__doc__ = \
"""
Concatenate ``data`` with the dataframe results of the tests in ``tests``.

:param pandas.DataFrame data: dataframe
:param list tests: list of :py:class:`Test` instances
:param bool normalized: if True, data is normalized in the output, default False

:rtype: pandas.DataFrame
"""

AddTWDTest.__doc__ = \
"""
Append the result of a :py:func:`TWDTest` as a column to ``data``, sorting it according to their values.

:param pandas.DataFrame data: dataframe
:param list keys: list of columns to use, default ``None``: all columns used
:param list exclude: list of columns to exclude, default empty
:param bool normalized: if True, data is normalized in the output, default False

:rtype: pandas.DataFrame


Examples: we consider the dataframe :ref:`data <data>`

.. code-block:: python

    result  = xt.AddTWDTest(data)
    
    # result is the dataframe
        col1   col2  col3       TWD
    e    NaN    7.0  21.0  0.102827
    h    8.0    3.0   NaN  0.153905
    i    9.0   12.0   NaN  0.157379
    f    9.0  -34.5   3.0  0.282413
    d   -3.0    NaN  44.0  0.552499
    g   22.0   95.0  -4.0  0.557941
    a    3.0  100.0   0.0  0.602914
    c    1.0 -123.0 -13.4  0.727218
    l    0.0 -567.0  21.0  1.075787
    b  100.0  200.0  74.0  2.024297

    nor_result = xt.AddTWDTest(data, normalized = True)
    
    # nor_result is the dataframe
           col1      col2      col3       TWD
    e       NaN  0.066215  0.036613  0.102827
    h -0.094124  0.059781       NaN  0.153905
    i -0.083122  0.074257       NaN  0.157379
    f -0.083122 -0.000536 -0.198754  0.282413
    d -0.215140       NaN  0.337359  0.552499
    g  0.059897  0.207759 -0.290286  0.557941
    a -0.149131  0.215801 -0.237982  0.602914
    c -0.171134 -0.142884 -0.413199  0.727218
    l -0.182136 -0.857039  0.036613  1.075787
    b  0.918013  0.376647  0.729637  2.024297

Notice that the sum of the absolute values of all columns but last coincides with the last column. This follows by definition of :py:func:`TWD`.
We would have obtained the same dataframe by running

.. code-block:: python

    xt.AddTWDTest(xt.Normalize(data))
"""
