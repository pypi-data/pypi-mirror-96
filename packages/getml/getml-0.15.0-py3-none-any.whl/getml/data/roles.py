# Copyright 2021 The SQLNet Company GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""A :class:`~getml.data.role` determines if and how
:mod:`~getml.data.columns` are handled during the construction of the
data model (see :ref:`data_model`) and used by the feature learning
algorithm (see :ref:`feature_engineering`).

Upon construction (via :func:`~getml.data.DataFrame.from_csv`,
:func:`~getml.data.DataFrame.from_pandas`,
:func:`~getml.data.DataFrame.from_db`, and
:func:`~getml.data.DataFrame.from_json`) a
:class:`~getml.data.DataFrame` will only consist of
:mod:`~getml.data.columns` holding either the role
:const:`~getml.data.role.unused_float` or
:const:`~getml.data.role.unused_string` depending on the underlying
data type. This tells the getML software to neither use these columns
during the creation of the data model, feature learning, nor the
training of the machine learning (ML) algorithms.

To make use of the imported data, you have to tell the getML suite how
you intend to use it by assigning another
:class:`~getml.data.role`. This can be done by either using the
:meth:`~getml.data.DataFrame.set_role` method of the
:class:`~getml.data.DataFrame` containing the particular column or by
providing a dictionary in the constructor function.

Each column must have at have a single role. But what if you e.g. want
to use a column to both create relations in your data model and to be
the basis of new features? You have to add it twice and assign
each of them a different role.
"""


categorical = "categorical"
"""Marks categorical ingredients for features.

This role tells the getML engine to include the associated
:class:`~getml.data.columns.StringColumn` during feature
learning.

It should be used for all data with no inherent ordering, even if the
categories are encoded as integer instead of strings in your provided
data set.
"""

join_key = "join_key"
"""Marks relations in the data model.

Role required to establish a relation between two
:class:`~getml.data.Placeholder`, the abstract representation of the
:class:`~getml.data.DataFrame`, by using the
:meth:`~getml.data.Placeholder.join` method (see
:ref:`data_model`). Please refer to the
chapter :ref:`data_model` for details.

The content of this column is allowed to contain NULL values. But
beware, columns with NULL in their join keys won't be matched to
anything, not even to NULL in other join keys.

:mod:`~getml.data.columns` of this role will *not* be handled by
the feature learning algorithm.

"""

numerical = "numerical"
"""Marks numerical ingredients for features.

This role tells the getML engine to include the associated
:class:`~getml.data.columns.FloatColumn` during feature
learning.

It should be used for all data with an inherent ordering, regardless
of whether it is sampled from a continuous quantity, like passed time or the
total amount of rainfall, or a discrete one, like the number of sugary
mulberries one has eaten since lunch.
"""

target = "target"
"""
Marks the column(s) we would like to predict.

The associated :mod:`~getml.data.columns` contain the variables we
want to predict. They are not used by the feature learning
algorithm unless we explicitly tell it to do so
(refer to ``allow_lagged_target`` in :meth:`~getml.data.Placeholder.join`).
But they
are such an important part of the analysis that the population table is required
to contain at least one of them (refer to :ref:`data_model_tables`).

The content of the target columns needs to be numerical.
For classification problems, target variables can only assume the values
0 or 1. Target variables can never be `NULL`.
"""

time_stamp = "time_stamp"
"""
Marks a column as a time stamp.

This role is used to prevent data leaks. When you join one table onto another,
you usually want to make sure that no data from the future is used. Time stamps
can be used to limit your joins.

In addition, the feature learning algorithm can aggregate time stamps or use them
for conditions. However, they will not be compared to fixed values unless you explicitly
change their units. This means
that conditions like this are not possible by default:

.. code-block:: sql

    ...
    WHERE time_stamp > some_fixed_date
    ...

Instead, time stamps will always be compared to other time stamps:

.. code-block:: sql

    ...
    WHERE time_stamp1 - time_stamp2 > some_value
    ...

This is because it is unlikely that comparing time stamps to a fixed date performs
well out-of-sample.

When assigning the role time stamp to a column that is currently a
:class:`~getml.data.columns.StringColumn`,
you need to specify the format of this string. You can do so by using
the :code:`time_formats` argument of
:meth:`~getml.data.DataFrame.set_role`. You can pass a list of time formats
that is used to try to interpret the input strings. Possible format options are

* %w - abbreviated weekday (Mon, Tue, ...)
* %W - full weekday (Monday, Tuesday, ...)
* %b - abbreviated month (Jan, Feb, ...)
* %B - full month (January, February, ...)
* %d - zero-padded day of month (01 .. 31)
* %e - day of month (1 .. 31)
* %f - space-padded day of month ( 1 .. 31)
* %m - zero-padded month (01 .. 12)
* %n - month (1 .. 12)
* %o - space-padded month ( 1 .. 12)
* %y - year without century (70)
* %Y - year with century (1970)
* %H - hour (00 .. 23)
* %h - hour (00 .. 12)
* %a - am/pm
* %A - AM/PM
* %M - minute (00 .. 59)
* %S - second (00 .. 59)
* %s - seconds and microseconds (equivalent to %S.%F)
* %i - millisecond (000 .. 999)
* %c - centisecond (0 .. 9)
* %F - fractional seconds/microseconds (000000 - 999999)
* %z - time zone differential in ISO 8601 format (Z or +NN.NN)
* %Z - time zone differential in RFC format (GMT or +NNNN)
* %% - percent sign

If none of the formats works, the getML engine will try to interpret
the time stamps as numerical values. If this fails, the time stamp will be set
to NULL.

>>> data_df = dict(
... date1=[getml.data.time.days(365), getml.data.time.days(366), getml.data.time.days(367)],
... date2=['1971-01-01', '1971-01-02', '1971-01-03'],
... date3=['1|1|71', '1|2|71', '1|3|71'],
)
>>> df = getml.data.DataFrame.from_dict(data_df, name='dates')
>>> df.set_role(['date1', 'date2', 'date3'], getml.data.roles.time_stamp, time_formats=['%Y-%m-%d', '%n|%e|%y'])
>>> df
| date1                       | date2                       | date3                       |
| time stamp                  | time stamp                  | time stamp                  |
-------------------------------------------------------------------------------------------
| 1971-01-01T00:00:00.000000Z | 1971-01-01T00:00:00.000000Z | 1971-01-01T00:00:00.000000Z |
| 1971-01-02T00:00:00.000000Z | 1971-01-02T00:00:00.000000Z | 1971-01-02T00:00:00.000000Z |
| 1971-01-03T00:00:00.000000Z | 1971-01-03T00:00:00.000000Z | 1971-01-03T00:00:00.000000Z |


.. note::

    getML time stamps are actually floats expressing the number of seconds since
    UNIX time (1970-01-01T00:00:00).
"""

unused_float = "unused_float"
"""Marks a :class:`~getml.data.column.FloatColumn` as unused.

The associated :mod:`~getml.data.column` will be neither used in the
data model nor during feature learning or prediction.
"""

unused_string = "unused_string"
"""Marks a :class:`~getml.data.column.StringColumn` as unused.

The associated :mod:`~getml.data.column` will be neither used in the
data model nor during feature learning or prediction.
"""
