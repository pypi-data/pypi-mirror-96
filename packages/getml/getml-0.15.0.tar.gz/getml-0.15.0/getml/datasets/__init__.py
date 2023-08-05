"""
The :mod:`getml.datasets` module includes utilities to load datasets,
including methods to load and fetch popular reference datasets. It also
features some artificial data generators.
"""

from .base import (
    load_air_pollution,
    load_atherosclerosis,
    load_biodegradability,
    load_consumer_expenditures,
    load_interstate94,
    load_loans,
    load_occupancy,
)
from .samples_generator import (
    _aggregate,
    make_categorical,
    make_discrete,
    make_numerical,
    make_same_units_categorical,
    make_same_units_numerical,
    make_snowflake,
)
