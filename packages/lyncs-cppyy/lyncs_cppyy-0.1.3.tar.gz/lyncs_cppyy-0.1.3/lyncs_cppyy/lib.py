"""
A Lib class for managing shared libraries
"""

import io
import os
import warnings
import cppyy
from lyncs_utils import redirect_stdout

__all__ = [
    "Lib",
    "loaded_libraries",
]


def loaded_libraries(short=False):
    """Returns the list of loaded libraries.
    If short, then only the names of the libraries without path and extension are returned.
    """
    fp = io.StringIO()
    with redirect_stdout(fp):
        cppyy.gbl.gSystem.ListLibraries()

    output = fp.getvalue().split("\n")
    start = output.index("=======================")
    end = output.index("-----------------------")

    libs = output[start + 1 : end]

    if not short:
        return libs

    libs = [lib.split("/")[-1].split(".")[0] for lib in libs]
    libs = ["lib" + lib[2:] if lib.startswith("-l") else lib for lib in libs]
    return libs


class Lib:
    """
    Lib can be used for managing shared libraries.

    Lib returns a variable that represents the library.
    The library is loaded at the first usage of the variable.
    In most of the cases, accessing attributes of the variable
    is like accessing attributed of `cppyy.gbl`.
    Exceptions are made for the attributes in __slots__
    or for macros defined in the loaded header.
    This latter feature is not supported by cppyy.gbl.

    Example
    -------

    >>> from lyncs_cppyy import Lib
    >>> zlib = Lib(header='zlib.h', library='libz')
    >>> zlib.zlibVersion()
     '1.2.11'

    The above is the equivalent of the following with cppyy

    >>> import cppyy
    >>> cppyy.include('zlib.h')        # bring in C++ definitions
    >>> cppyy.load_library('libz')     # load linker symbols
    >>> cppyy.gbl.zlibVersion()        # use a zlib API
     '1.2.11'
    """

    __slots__ = [
        "_cwd",
        "_loaded",
        "path",
        "include",
        "header",
        "library",
        "check",
        "c_include",
        "namespace",
        "defined",
    ]

    ignore = [
        "libpthread",
        "libm",
    ]

    @staticmethod
    def parse_arg(arg, name, types=str):
        "Auxiliary function for formatting the arguments"
        arg = () if arg is None else (arg,) if isinstance(arg, types) else tuple(arg)
        if not all((isinstance(_, types) for _ in arg)):
            raise TypeError(
                f"Expected {types} for {name} but got {list(type(_) for _ in arg)}"
            )
        return arg

    def __init__(
        self,
        header=None,
        library=None,
        check=None,
        include=None,
        path=".",
        c_include=False,
        namespace=None,
        defined=None,
        redefined=None,  # deprecated
    ):
        """
        Initializes a library class that can be pickled.

        Parameters
        ----------
        header: str or list
          Header(s) file to include.
        library: str or list
          Library(s) file to include. Also absolute paths are accepted.
        check: str or list
          Check function(s) to look for in the library to test if it has been loaded.
        include: str or list
          Path(s) to be included. Equivalent to `-I` used at compile time.
        path: str or list
          Path(s) where to look for headers and libraries.
          Headers are searched in path+"/include" and libraries in path+"/lib".
        c_include: bool
          Whether the library is a c library (False means it is a c++ library).
        namespace: str or list
          Namespace used across the library. Directly access object inside namespace.
          Similar to `using namespace ...` in c++.
        defined: dict
          List of symbols that have been defined
        """

        self._cwd = os.getcwd()
        self._loaded = False
        self.path = self.parse_arg(path, "path")
        self.header = self.parse_arg(header, "header")
        self.library = self.parse_arg(library, "library", (str, Lib))
        self.check = self.parse_arg(check, "check")
        self.include = self.parse_arg(include, "include")
        self.c_include = c_include
        self.namespace = self.parse_arg(namespace, "namespace")
        self.defined = dict(defined or redefined or ())
        if redefined:
            warnings.warn(
                "The use of redefined is deprecated. Please use defined",
                DeprecationWarning,
            )

    @property
    def loaded(self):
        "Returns if the library has been loaded"
        return self._loaded

    def load(self):
        "Loads the library"
        if self.loaded:
            raise RuntimeError("Library already loaded")

        for include in self.include:
            cppyy.add_include_path(include)

        for library in self.library:
            if isinstance(library, Lib) and not library.loaded:
                library.load()

        # Including headers
        self.define()

        for header in self.header:

            # Searching for headers in paths
            for path in self.path:
                if not path.startswith(os.sep):
                    path = self._cwd + "/" + path
                if os.path.isfile(path + "/include/" + header):
                    cppyy.add_include_path(path + "/include")
                    break

            if self.c_include:
                cppyy.c_include(header)
            else:
                cppyy.include(header)

        self.undef()

        # Loading libraries
        for library in self.library:
            if not isinstance(library, str):
                continue
            if library.startswith("-l"):
                library = "lib" + library[2:]
            if library in Lib.ignore:
                continue
            try:
                cppyy.load_library(library)
                continue
            except RuntimeError:
                pass
            tmp = library
            if not tmp.startswith(os.sep):
                tmp = self._cwd + "/" + tmp
            if not os.path.isfile(tmp):
                for path in self.path:
                    if not path.startswith(os.sep):
                        path = self._cwd + "/" + path
                    tmp = path + "/lib/" + library
                    if os.path.isfile(tmp):
                        break
            if not os.path.isfile(tmp):
                raise ImportError(
                    "Library %s not found in paths %s" % (library, self.path)
                )
            tmp = os.path.realpath(tmp)
            cppyy.load_library(tmp)

        self._loaded = True

        failed_checks = [_ for _ in self.check if not hasattr(self, _)]
        if failed_checks:
            raise RuntimeError(
                f"The following checks have not been found: {failed_checks}"
            )

    def define(self):
        "Defines the list of values in defined"
        cpp = ""
        for key, val in self.defined.items():
            cpp += f"#define {key} {val}\n"
        if cpp:
            cppyy.cppdef(cpp)

    def undef(self):
        "UnDefines the list of values in defined"
        cpp = ""
        for key in self.defined:
            cpp += f"#undef {key}\n"
        if cpp:
            cppyy.cppdef(cpp)

    def __getattr__(self, key):
        if not self.loaded:
            self.load()

        try:
            if self.defined:
                key = self.defined.get(key, key)
            if self.namespace:
                for namespace in self.namespace:
                    try:
                        return getattr(getattr(cppyy.gbl, namespace), key)
                    except AttributeError:
                        pass
            return getattr(cppyy.gbl, key)
        except AttributeError as err:
            try:
                return self.get_macro(key)
            except ValueError:
                pass
            raise err

    def __setattr__(self, key, value):
        try:
            return getattr(type(self), key).__set__(self, value)
        except AttributeError:
            pass

        if not self.loaded:
            self.load()

        if self.defined:
            key = self.defined.get(key, key)
        if self.namespace:
            for namespace in self.namespace:
                try:
                    getattr(getattr(cppyy.gbl, namespace), key)
                    return setattr(getattr(cppyy.gbl, namespace), key, value)
                except AttributeError:
                    pass
        getattr(cppyy.gbl, key)
        setattr(cppyy.gbl, key, value)

    def get_macro(self, key):
        "Returns the value of a defined macro by assigning it to a variable"
        try:
            return getattr(cppyy.gbl, "_" + key)
        except AttributeError:
            try:
                cppyy.cppdef(
                    """
                    auto _%s = %s;
                    """
                    % (key, key)
                )
                return self.get_macro(key)
            except SyntaxError as err:
                raise ValueError(f"{key} not found") from err
