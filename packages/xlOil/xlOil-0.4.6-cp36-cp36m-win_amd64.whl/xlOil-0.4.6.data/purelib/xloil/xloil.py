import inspect
import functools
import importlib
import importlib.util
import importlib.abc
import typing
import numpy as np
import os
import sys
import traceback

#
# If the xloil_core module can be found, we are being called from an xlOil
# embedded interpreter, so we go ahead and import the module. Otherwise we
# define skeletons of the imported types to support type-checking, linting,
# auto-completion and documentation.
#
if importlib.util.find_spec("xloil_core") is not None:
    import xloil_core         # pylint: disable=import-error
    from xloil_core import (  # pylint: disable=import-error
        CellError, FuncOpts, Range, ExcelArray, in_wizard, log,
        event, cache, RtdServer, RtdPublisher, get_event_loop,
        register_functions, deregister_functions,
        create_ribbon, RibbonUI, run_later, 
        get_excel_state, Caller,
        CannotConvert, set_return_converter,
        CustomConverter as _CustomConverter,
        CustomReturn as _CustomReturn,
        from_excel_date)

else:
    from .shadow_core import *
    from .shadow_core import (_CustomReturn)
    from .shadow_core import _CustomConverter
    

"""
Tag used to mark functions to register with Excel. It is added 
by the xloil.func decorator to the target func's __dict__
"""
_META_TAG = "_xloil_func_"

"""
This annotation includes all the types which can be passed from xlOil to
a function. There is not need to specify it to xlOil, but it could give 
useful type-checking information to other software which reads annotation.
"""
ExcelValue = typing.Union[bool, int, str, float, np.ndarray, dict, list, CellError]

"""
The special AllowRange annotation allows functions to receive the argument
as an ExcelRange object if appropriate. The argument may still be passed
as another type if it was not created from a sheet reference.
"""
AllowRange = typing.Union[ExcelValue, Range]

class Arg:
    """
    Holds the description of a function argument. Can be used with the 'func'
    decorator to specify the argument description.
    """
    def __init__(self, name, help="", typeof=None, default=None, is_keywords=False):
        """
        Parameters
        ----------

        name: str
            The name of the argument which appears in Excel's function wizard
        help: str, optional
            Help string to display in the function wizard
        typeof: object, optional
            Selects the type converter used to pass the argument value
        default: object, optional
            A default value to pass if the argument is not specified in Excel
        is_keywords: bool, optional
            Denotes the special kwargs argument. xlOil will expect a two-column array
            in Excel which it will interpret as key, value pairs and convert to a
            dictionary.
        """

        self.typeof = typeof
        self.name = str(name)
        self.help = help
        self.default = default
        self.is_keywords = is_keywords

    @property
    def has_default(self):
        """ 
        Since 'None' is a fairly likely default value, this property indicates 
        whether there was a user-specified default
        """
        return self.default is not inspect._empty

def _function_argspec(func):
    """
    Returns a list of Arg for a given function which describe
    the function's arguments
    """
    sig = inspect.signature(func)
    params = sig.parameters
    args = []
    for name, param in params.items():
        if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
            spec = Arg(name, default=param.default)
            anno = param.annotation
            if anno is not param.empty:
                spec.typeof = anno
                # Add a little help string based on the type annotation
                if isinstance(anno, type):
                    spec.help = f"({anno.__name__})"
                else:
                    spec.help = f"({str(anno)})"
            args.append(spec)
        elif param.kind == param.VAR_POSITIONAL:
             raise Exception(f"Unhandled argument type positional for {name}")
        elif param.kind == param.VAR_KEYWORD: # can type annotions make any sense here?
            args.append(Arg(name, is_keywords=True))
        else: 
            raise Exception(f"Unhandled argument type for {name}")
    return args, sig.return_annotation


def _get_typeconverter(type_name, from_excel=True):
    """
    Attempt to find converter with standardised name like `From_int`. Falls back
    to From_cache if none found
    """
    to_from = 'To' if from_excel else 'From'
    name = f"{to_from}_{type_name}"
    if not hasattr(xloil_core, name):
        name = f"{to_from}_cache"
    return getattr(xloil_core, name)()


class _Converter:
     _xloil_converter = None
     _xloil_allow_range = False

def converter(typ=typing.Callable, range=False):
    """
    Decorator which declares a function or a class to be a type converter.

    A type converter function is expected to take an argument of type:
    int, bool, float, str, ExcelArray, Range (optional)

    The type converter should return a python object, which could be an 
    ExcelArray or Range.

    A type converter class may take parameters into its constructor
    and hold state.  It should implement __call__ to behave as a type
    converter function.

    Both functions and classes are turned into a class which inherits from 
    ``typ``.  This is to support type hints only.

    If ``range`` is True, the xlOil may pass an ExcelRange or and ExcelArray
    object depending on how the function was invoked.  The type converter should 
    handle both cases consistently.

    Examples
    --------
    
    ::

        @converter(double)
        def arg_sum(x):
            if isinstance(x, ExcelArray):
                return np.sum(x.to_numpy())
            elif isinstance(x, str):
                raise Error('Unsupported')
            return x

        @func
        def pyTest(x: arg_sum):
            return x
            
    """

    def decorate(obj):
        if inspect.isclass(obj):

            #
            # The construction is a little cryptic here to support nice syntax. The
            # target `obj` is intented to be used in a typing expresion like x: obj(...).
            # Hence obj(...) must return something which inherits from the desired type
            # `typ` but is also identifiable to xlOil as a converter.
            #
            class TypingHolder(typ):

                def __init__(self):
                    pass # Keeps linter quiet

                def __call__(self, *args, **kwargs):
                    instance = obj(*args, **kwargs)
                    class Converter(typ or instance.target, _Converter):
                        _xloil_converter = _CustomConverter(instance)
                        _xloil_allow_range = range

                    return Converter

            return TypingHolder()

        else:

            class Converter(typ, _Converter):
                _xloil_converter = _CustomConverter(obj)
                _xloil_allow_range = range

            return Converter

    return decorate

class Cache:
    """
    Allows you to write `-> xloil.Cache` after a function declaration to force
    the output to be placed in the object cache. The class has no actual
    functionality.
    """
    pass

class FuncDescription:
    """
    Used to create the description of a worksheet function to register. 
    External users would not typically use this class directly.
    """
    def __init__(self, func):
        self._func = func
        self.args, self.return_type = _function_argspec(func)
        self.name = func.__name__
        self.help = func.__doc__
        self.is_async = False
        self.rtd = None
        self.macro = False
        self.threaded = False
        self.volatile = False
        self.local = None

    def create_holder(self):
        """
        Creates a core object which holds function info, argument converters,
        and a reference to the function object
        """
        
        info = xloil_core.FuncInfo()
        info.args = [xloil_core.FuncArg(x.name, x.help) for x in self.args]
        info.name = self.name
        
        if self.help:
            info.help = self.help
            
        has_kwargs = any(self.args) and self.args[-1].is_keywords

        holder = xloil_core.FuncHolder(info, self._func, has_kwargs)
        
        # Set the arg converters based on the typeof provided for 
        # each argument. If 'typeof' is a xloil typeconverter object
        # it's passed through.  If it is a general python type, we
        # attempt to create a suitable typeconverter
        for i, x in enumerate(self.args):
            if x.is_keywords:
                continue
            # Default option is the generic converter which tries to figure
            # out what to return based on the Excel type
            converter = xloil_core.To_object()
            this_arg = info.args[i]
            argtype = x.typeof
            if argtype is not None:
                if inspect.isclass(argtype) and issubclass(argtype, _Converter):
                    converter = argtype._xloil_converter
                    this_arg.allow_range = argtype._xloil_allow_range
                elif argtype is AllowRange:
                    this_arg.allow_range = True
                elif argtype is Range:
                    this_arg.allow_range = True
                    converter = _get_typeconverter("Range", from_excel=True)
                elif argtype is ExcelValue:
                    pass # This the explicit generic type, so do nothing
                elif isinstance(argtype, type) and argtype is not object:
                    converter = _get_typeconverter(argtype.__name__, from_excel=True)

            if x.has_default:
                this_arg.optional = True
                holder.set_arg_type_defaulted(i, converter, x.default)
            else:
                holder.set_arg_type(i, converter)

        if self.return_type is not inspect._empty:
            ret_type = self.return_type
            ret_con = None
            if issubclass(ret_type, _Converter):
                ret_con = _CustomReturn(ret_type._xloil_converter)
            elif isinstance(ret_type, Cache):
                ret_con = xloil_core.To_cache()
            elif isinstance(ret_type, type) and ret_type is not object:
                ret_con = _get_typeconverter(ret_type.__name__, from_excel=False)
            else:
                pass # Not sure how we get here
            holder.return_converter = ret_con

        # RTD-async is default unless rtd=False was explicitly specified.
        holder.rtd_async = self.is_async and (self.rtd is not False)
        holder.native_async = self.is_async and not holder.rtd_async

        holder.local = True if (self.local is None and not holder.native_async) else self.local

        func_options = ((FuncOpts.Macro if self.macro else 0)
                        | (FuncOpts.ThreadSafe if self.threaded else 0)
                        | (FuncOpts.Volatile if self.volatile else 0))

        if holder.local:
            if func_options != 0:
                log(f"Ignoring func options for local function {self.name}", level='info')
        else:
            holder.set_opts(func_options)
        return holder


def _get_meta(fn):
    return fn.__dict__.get(_META_TAG, None)


def _create_event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

def async_wrapper(fn):
    """
    Wraps an async function or generator with a function which runs that generator on the thread's
    event loop. The wrapped function requires an 'xloil_thread_context' argument which provides a 
    callback object to return a result. xlOil will pass this object automatically to functions 
    declared async.

    This function is used by the `func` decorator and generally should not be invoked
    directly.
    """

    import asyncio

    @functools.wraps(fn)
    def synchronised(*args, xloil_thread_context, **kwargs):

        loop = get_event_loop()
        ctx = xloil_thread_context

        async def run_async():
            result = None
            try:
                # TODO: is inspect.isasyncgenfunction expensive?
                if inspect.isasyncgenfunction(fn):
                    async for result in fn(*args, **kwargs):
                        ctx.set_result(result)
                else:
                    result = await fn(*args, **kwargs)
                    ctx.set_result(result)
            except (asyncio.CancelledError, StopAsyncIteration):
                ctx.set_done()
                raise
            except Exception as e:
                ctx.set_result(str(e) + ": " + traceback.format_exc())
                
            ctx.set_done()
            
        ctx.set_task(asyncio.run_coroutine_threadsafe(run_async(), loop))

    return synchronised    

def _pump_message_loop(loop, timeout):
    """
    Called internally to run the asyncio message loop.
    """
    import asyncio

    async def wait():
        await asyncio.sleep(timeout)
    
    loop.run_until_complete(wait())


def func(fn=None, 
         name=None, 
         help=None, 
         args=None,
         group=None, 
         local=None,
         is_async=False, 
         rtd=None,
         macro=False, 
         threaded=False, 
         volatile=False):
    """ 
    Decorator which tells xlOil to register the function in Excel. 
    If arguments are annotated using 'typing' annotations, xlOil will attempt to 
    convert values received from Excel to the specfied type, raising an exception 
    if this is not possible. The currently available types are

    * **int**
    * **float**
    * **str**: Note this disables cache lookup
    * **bool**
    * **numpy arrays**: see Array
    * **CellError**: Excel has various error types such as #NUM!, #N/A!, etc.
    * **None**: if the argument points to an empty cell
    * **cached objects**
    * **datetime.date**
    * **datetime.datetime**
    * **dict / kwargs**: this converter expects a two column array of key/value pairs

    If no annotations are specified, xlOil will pass a type from the first eight above types
    based on the value provided from Excel.

    If a parameter default is given in the function signature, that parameter becomes optional in 
    the declared Excel function.

    Parameters
    ----------

    name: str
        Overrides the funtion name registered with Excel otherwise the function's 
        declared name is used.
    help: str
        Overrides the help shown in the function wizard otherwise the function's 
        doc-string is used. The wizard cannot display strings longer than 255 chars.
        Longer help string can be retrieved with `xloHelp`
    args: dict
        A dictionary with key names matching function arguments and values specifying
        information for that argument. The information can be a string, which is 
        interpreted as the help to display in the function wizard or in can be an 
        xloil.Arg object which can contain defaults, help and type information. 
    group: str
        Specifes a category of functions in Excel's function wizard under which
        this function should be placed.
    local: bool
        Functions in a workbook-linked module, e.g. Book1.py, default to 
        workbook-level scope (i.e. not usable outside that workbook) itself. You 
        can override this behaviour with this parameter. It has no effect outside 
        workbook-linked modules.
    macro: bool
        If True, registers the function as Macro Type. This grants the function
        extra priveledges, such as the ability to see un-calced cells and 
        call the full range of Excel.Application functions. Functions which will
        be invoked as Excel macros, i.e. not functions appearing in a cell, should
        be declared with this attribute.
    is_async: bool
        Registers the function as asynchronous. It's better to use asyncio's
        'async def' syntax if it is available. Only async RTD functions are
        calculated in the background in Excel, non-RTD functions will be stopped
        if calculation is interrupted.
    threaded: bool
        Declares the function as safe for multi-threaded calculation. The
        function must be careful when accessing global objects. 
        Since python (at least CPython) is single-threaded there is
        no direct performance benefit from enabling this. However, if you make 
        frequent calls to C-based libraries like numpy or pandas you make
        be able to realise speed gains.
    volatile: bool
        Tells Excel to recalculate this function on every calc cycle: the same
        behaviour as the NOW() and INDIRECT() built-ins.  Due to the performance 
        hit this brings, it is rare that you will need to use this attribute.

    """

    arguments = locals()
    def decorate(fn):

        _is_async = is_async
        if inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn):
            fn = async_wrapper(fn)
            _is_async = True

        descr = FuncDescription(fn)

        for arg, val in arguments.items():
            if not arg in ['fn', 'args', 'name', 'help']:
                descr.__dict__[arg] = val
        if name is not None:
            descr.name = name
        if help is not None:
            descr.help = help

        if args is not None:
            arg_names = [x.name.casefold() for x in descr.args]
            if type(args) is dict:
                for arg_name, arg_help in args.items():
                    try:
                        i = arg_names.index(arg_name.casefold())
                        descr.args[i].help = arg_help
                    except ValueError:
                        raise Exception(f"No parameter '{arg_name}' in function {fn.__name__}")
            else:
                for arg in args:
                    try:
                        i = arg_names.index(arg.name.casefold())
                        descr.args[i] = arg
                    except ValueError:
                        raise Exception(f"No parameter '{arg_name}' in function {fn.__name__}")
        
        descr.is_async = _is_async

        fn.__dict__[_META_TAG] = descr
        return fn

    return decorate if fn is None else decorate(fn)

_excel_application_com_obj = None

# TODO: Option to use win32com instead of comtypes?
def app():
    """
        Returns a handle to the Excel.Application object using the *comtypes* 
        library. The Excel.Application object is the root of Excel's COM
        interface and supports a wide range of operations. It is well 
        documented by Microsoft, see 
        https://docs.microsoft.com/en-us/visualstudio/vsto/excel-object-model-overview
        and 
        https://docs.microsoft.com/en-us/office/vba/api/excel.application(object).
        
        Many operations using the Application object will only work in 
        functions declared as **macro type**.

        Examples
        --------

        To get the name of the active worksheet:

        ::
            
            @func(macro=True)
            def sheetName():
                return xlo.app().ActiveSheet.Name

    """
    global _excel_application_com_obj
    if _excel_application_com_obj is None:
        import comtypes.client
        import comtypes
        import ctypes
        clsid = comtypes.GUID.from_progid("Excel.Application")
        obj = ctypes.POINTER(comtypes.IUnknown)(xloil_core.application())
        _excel_application_com_obj = comtypes.client._manage(obj, clsid, None)
    return _excel_application_com_obj
     

class _ArrayType:
    """
    This object can be used in annotations or @xlo.arg decorators
    to tell xlOil to attempt to convert an argument to a numpy array.

    You don't use this type directly, ``Array`` is a static instance of 
    this type, so use the syntax as show in the examples below.

    If you don't specify this annotation, xlOil may still pass an array
    to your function if the user passes a range argument, e.g. A1:B2. In 
    this case you will get a 2-dim Array(object). If you know the data 
    type you want, it is more perfomant to specify it by annotation with 
    ``Array``.

    Examples
    --------

        @xlo.func
        def array1(x: xlo.Array(int)):
            pass

        @xlo.func
        def array2(y: xlo.Array(float, dims=1)):
            pass

        @xlo.func
        def array3(z: xlo.Array(str, trim=False)):
            pass
    
    Methods
    -------

    **(dtype, dims, trim)** :    
        Element types are converted to numpy dtypes, which means the only supported types are: 
        int, float, bool, str, datetime, object.
        (Numpy has a richer variety of dtypes than this but Excel does not.) 
        
        For the float data type, xlOil will convert #N/As to numpy.nan but other values will 
        causes errors.

    dims : int
        Arrays can be either 1 or 2 dimensional, 2 is the default.  Note the Excel has
        the following behaviour for writing arrays into an array formula range specified
        with Ctrl-Alt-Enter:
        "If you use a horizontal array for the second argument, it is duplicated down to
        fill the entire rectangle. If you use a vertical array, it is duplicated right to 
        fill the entire rectangle. If you use a rectangular array, and it is too small for
        the rectangular range you want to put it in, that range is padded with #N/As."

    trim : bool    
        By default xlOil trims arrays to the last row & column which contain a nonempty
        string or non-#N/A value. This is generally desirable, but can be disabled with 
        this paramter.

    """

    def __call__(self, dtype=object, dims=2, trim=True):
        name = f"To_Array_{dtype.__name__}_{dims or 2}d" 
        type_conv = getattr(xloil_core, name)(trim)

        class Arr(np.ndarray, _Converter):
            _xloil_converter = type_conv
            _xloil_allow_range = False

        return Arr
        
# Cheat to avoid needing Py 3.7+ for __class_getitem__
Array = _ArrayType() 

class EventsPaused():
    """
    A context manager which stops Excel events from firing whilst
    the context is in scope
    """
    def __enter__(self):
        event.pause()
        return self
    def __exit__(self, type, value, traceback):
        event.allow()

class _ModuleFinder(importlib.abc.MetaPathFinder):

    path_map = dict()

    def find_spec(self, fullname, path, target=None):
        path = self.path_map.get(fullname, None)
        if path is None:
            return None
        return importlib.util.spec_from_file_location(fullname, self.path_map[fullname])

    def find_module(self, fullname, path):
        return None


_module_finder = _ModuleFinder()
sys.meta_path.append(_module_finder)

def scan_module(module, workbook_name=None):
    """
        Parses a specified module looking for functions with with the xloil.func 
        decorator and register them. Does not search inside second level imports.

        The argument can be a module object, module name or path string. The module 
        is first imported if it has not already been loaded.
 
        Called by the xlOil C layer to import modules specified in the config.
    """

    with EventsPaused() as paused:

        if type(module) is str:
            mod_directory, filename = os.path.split(module)
            filename = filename.replace('.py', '')

            # avoid name collisions when loading workbook modules
            mod_name = filename if workbook_name is None else "xloil_wb_" + filename

            if len(mod_directory) > 0 or workbook_name is not None:
                _module_finder.path_map[mod_name] = module
   
            handle = importlib.import_module(mod_name)

            # Allows 'local' modules to know which workbook they link to
            if workbook_name is not None:
                handle._xloil_workbook = workbook_name
                handle._xloil_workbook_path = os.path.join(mod_directory, workbook_name)

        elif (inspect.ismodule(module) and hasattr(module, '__file__')) or module in sys.modules:
            # We can only reload modules with a __file__ attribute, e.g. not
            # xloil_core
            handle = importlib.reload(module)
        else:
            raise Exception(f"scan_module: could not process {str(module)}")

    
        # Look for functions with an xloil decorator (_META_TAG) and create
        # a function holder object for each of them
        xloil_funcs = inspect.getmembers(handle, 
            lambda obj: inspect.isfunction(obj) and hasattr(obj, _META_TAG))

        to_register = []
        for f_name, f in xloil_funcs:
            import traceback
            try:
                to_register.append(_get_meta(f).create_holder())
            except Exception as e:
                log(f"Register failed for {f_name}: {traceback.format_exc()}", level='error')

        if any(to_register):
            xloil_core.register_functions(handle, to_register)

        return handle

class _ReturnConverters:

    _converters = set()

    def add(self, conv):
        self._converters.add(conv)
        set_return_converter(_CustomReturn(self))
    
    def remove(self, conv):
        self._converters.remove(conv)
        if len(self._converters) == 0:
            set_return_converter(None)

    def __call__(self, obj):
        for c in self._converters:
            try:
                return c(obj)
            except (CannotConvert):
                continue
        raise CannotConvert()

return_converters = _ReturnConverters()
