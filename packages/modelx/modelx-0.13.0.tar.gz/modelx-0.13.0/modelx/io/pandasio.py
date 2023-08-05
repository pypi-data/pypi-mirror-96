# Copyright (c) 2017-2021 Fumito Hamamura <fumito.ham@gmail.com>

# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation version 3.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see <http://www.gnu.org/licenses/>.

import pathlib
from .baseio import BaseDataClient, BaseSharedData
import pandas as pd


class PandasIO(BaseSharedData):

    def __init__(self, path, load_from):
        super().__init__(path, load_from)
        self.is_updated = True  # Not Used

    def _on_save(self, path):
        for c in self.clients.values():     # Only one client
            c._write_pandas(path)


class PandasData(BaseDataClient):
    """A subclass of :class:`~modelx.io.baseio.BaseDataClient` that
    associates a `pandas`_ `DataFrame`_ or `Series`_ with a file

    A :class:`PandasData` holds a pandas `DataFrame`_ or `Series`_ object,
    and associates it with a file for writing and reading the object.

    A :class:`PandasData` can be created only by
    :meth:`UserSpace.new_pandas<modelx.core.space.UserSpace.new_pandas>` or
    :meth:`Model.new_pandas<modelx.core.model.Model.new_pandas>`.

    The `DataFrame`_ or `Series`_ held in :class:`PandasData` objects
    are accessible through
    :attr:`~PandasData.value` property or a call ``()`` method.

    Args:
        path: Path to a file for saving data. If a relative
            path is given, it is relative to the model folder.
        data: a pandas DataFrame or Series.
        filetype(:obj:`str`): String to specify the file format.
            "excel" or "csv"

    See Also:
        :meth:`UserSpace.new_pandas<modelx.core.space.UserSpace.new_pandas>`
        :meth:`Model.new_pandas<modelx.core.model.Model.new_pandas>`
        :attr:`~modelx.core.model.Model.dataclients`

    Attributes:
        path: A path to the associated file as a `pathlib.Path`_ object.
        filetype(:obj:`str`): "excel" or "csv".

    .. _pathlib.Path:
        https://docs.python.org/3/library/pathlib.html#pathlib.Path

    .. _pandas: https://pandas.pydata.org

    .. _DataFrame:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

    .. _Series:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html

    """

    data_class = PandasIO

    def __init__(self, path, data, filetype, is_hidden):
        BaseDataClient.__init__(self, path, is_hidden=is_hidden)
        self.filetype = filetype.lower()
        self._value = data
        self.name = data.name if isinstance(data, pd.Series) else None

        self._read_args = {}
        if self.filetype == "excel" or self.filetype == "csv":
            if isinstance(data, pd.DataFrame) and data.columns.nlevels > 1:
                self._read_args["header"] = list(range(data.columns.nlevels))
            if data.index.nlevels > 1:
                self._read_args["index_col"] = list(range(data.index.nlevels))
            else:
                self._read_args["index_col"] = 0
            if isinstance(data, pd.Series):
                self._read_args["squeeze"] = True
            if self.filetype == "excel":
                if (len(self.path.suffix[1:]) > 3
                        and self.path.suffix[1:4] == "xls"):
                    self._read_args["engine"] = "openpyxl"
        else:
            raise ValueError("Pandas IO type not supported")

        if is_hidden:
            self._value._mx_dataclient = self

    def _on_load_value(self):
        pass

    def _on_pickle(self, state):
        state.update({
            "filetype": self.filetype,
            "value": self._value,
            "read_args": self._read_args,
            "name": self.name
        })
        return state

    def _on_unpickle(self, state):
        self.filetype = state["filetype"]
        self._value = state["value"]
        self._read_args = state["read_args"]
        self.name = state["name"]

    def _on_serialize(self, state):
        state.update({
            "filetype": self.filetype,
            "read_args": self._read_args,
            "name": self.name
        })
        return state

    def _on_unserialize(self, state):
        self.filetype = state["filetype"]
        self._read_args = state["read_args"]
        self.name = state["name"]
        self._read_pandas()

    def _can_add_other(self, other):
        return False

    def _read_pandas(self):
        if self.filetype == "excel":
            self._value = pd.read_excel(
                self._data.load_from, **self._read_args)
        elif self.filetype == "csv":
            self._value = pd.read_csv(
                self._data.load_from, **self._read_args)
        else:
            raise ValueError

        if isinstance(self._value, pd.Series):
            self._value.name = self.name

        if self._is_hidden:
            self._value._mx_dataclient = self

    def _write_pandas(self, path):
        if self.filetype == "excel":
            self._value.to_excel(path)
        elif self.filetype == "csv":
            self._value.to_csv(path)
        else:
            raise ValueError

    @property
    def value(self):
        """pandas DataFrame or Series held in the object"""
        return self._value

    def __call__(self):
        """Returns pandas DataFrame or Series held in the object"""
        return self._value
