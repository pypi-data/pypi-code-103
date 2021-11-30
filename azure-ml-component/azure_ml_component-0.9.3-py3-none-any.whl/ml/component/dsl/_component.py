# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A wrapper to analyze function annotations, generate component specs, and run component in command line."""
import argparse
import contextlib
import copy
import importlib
import multiprocessing
import os
import pathlib
import re
import sys
import tempfile
import inspect
import functools
import types
from io import StringIO
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import TypeVar, Callable, Any

from azure.ml.component._util._constants import LOCAL_PREFIX
from azure.ml.component._util._utils import _relative_to
from azure.ml.component._util._yaml_utils import YAML
from azure.ml.component._core._component_definition import ComponentType
from azure.ml.component.dsl._component_generator import DSLCommandLineGenerator
from azure.ml.component.dsl._module_spec import SPEC_EXT, ParallelRunModuleSpec
from azure.ml.component.dsl._utils import _resolve_source_directory, \
    is_dsl_component, _import_component_with_working_dir, logger
from azure.ml.component._core._component_definition import CommandComponentDefinition
from azure.ml.component.dsl.types import _InputFileList, Output, _Param, Input, _OutputFile, \
    _get_param_with_standard_annotation, String
from azure.ml.component.environment import Environment
from azure.ml.component._aml_core_dependencies import _get_tagged_image
from azure.ml.component._util._exceptions import DSLComponentDefiningError, NoDslComponentError, \
    RequiredComponentNameError, TooManyDSLComponentsError, RequiredParamParsingError
from azureml.exceptions import UserErrorException

OPENMPI_CPU_IMAGE = _get_tagged_image("mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu16.04")
# hint vscode intellisense
_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])


def _component(
    *, name=None, version='0.0.1', display_name=None, description=None, is_deterministic=None,
    tags=None, environment=None, code=None
):
    """Return a decorator which is used to declare a component with @dsl._component.

    A component is a reusable unit in an Azure Machine Learning workspace.
    With the decorator @dsl._component, a function could be registered as a component in the workspace.
    Then the component could be used to construct an Azure Machine Learning pipeline.
    The parameters of the decorator are the properties of the component spec,
    see https://aka.ms/azureml-component-specs.

    .. remarks::

        The following example shows how to use @dsl._component to declare a simple component.

        .. code-block:: python

            @dsl._component()
            def your_component_function(output: Output(), input: Input(), param='str_param'):
                pass

        The following example shows how to declare a component with detailed meta data.

        .. code-block:: python

            @dsl._component(name=name, version=version, namespace=namespace, description=description)
            def your_component_function(output: Output(), input: Input(), param='str_param'):
                pass

        The following example shows how to consumption the declared component function with dsl pipeline.

        .. code-block:: python

            # definition dsl pipeline with dsl._component function
            @dsl.pipeline()
            def your_pipeline_func(input, param):
                your_component_function(input=input, param=param)

            # create the pipeline
            pipeline = your_pipeline_func(your_input, 'your_str')

            # the dsl component will be registered anonymously
            pipeline.validate(workspace=your_workspace)

        With the Component.create, we could register the component to workspace explicitly.
        The following example shows how to register existing dsl component function.

        .. code-block:: python

            from azure.ml.component import Component

            # register dsl component
            your_registered_component_function = Component.create(
                function=your_component_function, version='0.0.1',
                set_as_default=True, workspace=target_workspace
            )

            # create component
            component = your_registered_component_function()

        With the dsl._component function, we could build a component specification yaml file.
        For more details of the component spec, see https://aka.ms/azureml-component-specs


    :param name: The name of the component. If None is set, camel cased function name is used.
    :type name: str
    :param description: The description of the component. If None is set, the doc string is used.
    :type description: str
    :param version: Version of the component.
    :type version: str
    :param display_name: Display name of the component.
    :type display_name: str
    :param is_deterministic: Specify whether the component will always generate the same result. The default value is
                             None, the component will be reused by default behavior, the same for True value. If
                             False, this component will never be reused.
    :type is_deterministic: bool
    :param tags: Tags of the component.
    :type tags: builtin.list
    :param environment: Environment config of component, could be a yaml file path, a dict or an Environment object.
                        If None, a default conda.yaml with 'azureml-defaults' and 'azure-ml-component' will be used.
    :type environment: Union[str, pathlib.path, dict, azure.ml.core.Environment]
    :param code: The source directory of dsl.component, with default value '.'.
                 i.e. The directory of dsl component file.
    :type code: str
    :return: An injected function which could be passed to ComponentExecutor
    """
    # Get the customer code directory to resolve absolute code path
    dsl_component_source_dir = _resolve_source_directory()
    environment = _refine_environment_to_obj(environment, dsl_component_source_dir)
    code = '.' if not code else code

    if name and not CommandComponentDefinition.is_valid_name(name):
        msg = "Name is not valid, it could only contains a-z, A-Z, 0-9 and '.-_', got '%s'." % name
        raise DSLComponentDefiningError(msg)

    spec_args = {k: v for k, v in locals().items() if v is not None
                 and k in inspect.signature(_component).parameters}
    wrap_callable = False
    if callable(name):
        wrap_callable = True
        spec_args = {}

    from ..component import Component

    def component_func_decorator(func: _TFunc) -> _TFunc:
        nonlocal spec_args
        spec_args = _refine_spec_args(spec_args)

        spec_args['name'] = spec_args.get('name', func.__name__)
        spec_args['display_name'] = spec_args.get('display_name', spec_args['name'])
        spec_args['description'] = spec_args.get('description', func.__doc__)
        func_entry_path = Path(inspect.getfile(func)).resolve().absolute()
        spec_args['code'] = (Path(dsl_component_source_dir) / code).resolve().absolute().as_posix()
        if not os.path.isdir(spec_args['code']):
            raise UserErrorException(f"Only folder can be supported as 'code' in dsl.component, got {code!r}")
        # Set entry name as relative path to code
        entry_relative_path = _relative_to(func_entry_path, spec_args['code'])
        if not entry_relative_path:
            raise UserErrorException(
                f"Func {func.__name__!r} source directory {func_entry_path!r} "
                f"not under code directory {spec_args['code']!r}")
        entry_relative_path = entry_relative_path.as_posix()
        spec_args['command'] = [
            'python', '-m', 'azure.ml.component.dsl.executor',
            '--file', str(entry_relative_path), '--function', func.__name__,
            ComponentExecutor.EXECUTION_PARAMETERS_KEY]
        # Initialize a ComponentExecutor to make sure it works and use it to update the component function.
        # Save the raw func as we will wrap it
        raw_func = copy.copy(func)
        executor = ComponentExecutor(raw_func, spec_args)
        executor._update_func(raw_func)
        executor._update_func(func)
        _component_func = None

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Component:
            nonlocal _component_func
            if not _component_func:
                _component_func = Component.from_yaml(yaml_file=executor._get_spec_file_path())
            return _component_func(*args, **kwargs)

        wrapper._is_dsl_component = True
        wrapper._executor = executor
        return wrapper

    return component_func_decorator(name) if wrap_callable else component_func_decorator


def _refine_environment_to_obj(environment, dsl_component_source_dir) -> Environment:
    if isinstance(environment, dict):
        # Write into a temp file.
        path = tempfile.mktemp()
        environment = _refine_path_in_environment_dict(environment, dsl_component_source_dir)
        with open(path, 'w') as f:
            YAML().dump(environment, f)
        environment = path
    if isinstance(environment, pathlib.Path):
        environment = str(environment)
    if isinstance(environment, str):
        environment = Environment(file=environment)
    if environment and not isinstance(environment, Environment):
        raise UserErrorException(
            f'Unexpected environment type {type(environment).__name__!r}, '
            f'expected str, path, dict or azure.ml.core.Environment object.')
    return environment


def _refine_path_in_environment_dict(env_dict: dict, source_dir: str) -> dict:
    """Refine relative path in env dict to abs path."""
    if 'conda' in env_dict:
        conda_dict = env_dict['conda']
        if 'pip_requirements_file' in conda_dict:
            conda_dict['pip_requirements_file'] = \
                (Path(source_dir) / conda_dict['pip_requirements_file']).resolve().absolute().as_posix()
        if 'conda_dependencies_file' in conda_dict:
            conda_dict['conda_dependencies_file'] = \
                (Path(source_dir) / conda_dict['conda_dependencies_file']).resolve().absolute().as_posix()
    if "docker" in env_dict and "build" in env_dict["docker"] and \
            "dockerfile" in env_dict["docker"]["build"]:
        dockerfile = env_dict["docker"]["build"]["dockerfile"]
        if dockerfile.startswith(LOCAL_PREFIX):
            env_dict["docker"]["build"]["dockerfile"] = \
                (Path(source_dir) / dockerfile[len(LOCAL_PREFIX):]).resolve().absolute().as_posix()
    return env_dict


def _refine_spec_args(spec_args: dict) -> dict:
    spec_args = copy.copy(spec_args)
    tags = spec_args.get('tags', {})

    # Convert the type to support old style list tags.
    if isinstance(tags, list):
        tags = {tag: None for tag in tags}

    if not isinstance(tags, dict):
        raise DSLComponentDefiningError("Keyword 'tags' must be a dict.")

    # Indicate the component is generated by dsl.component
    if 'codegenBy' not in tags:
        tags['codegenBy'] = 'dsl.component'
    spec_args['tags'] = tags

    environment = spec_args.pop('environment') if 'environment' in spec_args else Environment()
    core_env = environment._env
    if not core_env.docker or not core_env.docker.image:
        if not core_env.conda:
            # If docker image and conda are not specified, add empty conda to generate a default conda.yaml
            from azure.ml.component._core._environment import Conda
            core_env._conda = Conda()
    spec_args['environment'] = core_env
    return spec_args


class ComponentExecutor:
    """An executor to analyze the spec args of a function and convert it to a runnable component in AzureML."""

    INJECTED_FIELD = '_spec_args'  # The injected field is used to get the component spec args of the function.
    EXECUTION_PARAMETERS_KEY = '--params'

    def __init__(self, func: types.FunctionType, spec_args=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function wrapped by dsl.component.
        :type func: types.FunctionType
        """
        if not isinstance(func, types.FunctionType):
            raise TypeError("Only function type is allowed to initialize ComponentExecutor.")
        if spec_args is None:
            spec_args = getattr(func, self.INJECTED_FIELD, None)
            if spec_args is None:
                raise TypeError("You must wrap the function with @dsl._component() before using it.")
        self._raw_spec_args = copy.copy(spec_args)
        self._name = spec_args['name']
        self._type = spec_args.get('type', ComponentType.CommandComponent.value)
        executor_cls = self._get_executor_by_type(self.type)
        self._executor = executor_cls(func, spec_args=spec_args)
        # If is dsl component func, set the func as inner func
        self._func = func._executor._func if is_dsl_component(func) else func
        self._spec_file_path = None

    @property
    def name(self):
        """Return the name of the component."""
        return self._name

    @property
    def type(self):
        """Return the job type of the component."""
        return self._type

    @property
    def spec(self):
        """Return the module spec instance of the component.

        Initialized by the function annotations and the meta data.
        """
        return self._executor.spec

    @property
    def spec_dict(self):
        """Return the component spec data as a python dict."""
        return self._executor.spec._to_dict()

    def to_spec_yaml(self, folder=None, spec_file=None):
        """
        Generate spec dict object, and dump it as a yaml spec file.

        :param folder: Folder of spec file, will be function file folder if not specified.
        :type folder: Path
        :param spec_file: The spec file name, will be generated based on function file.
        :type spec_file: str
        :return: The path of spec file.
        :rtype: Path
        """
        pyfile = Path(inspect.getfile(self._func))
        if folder is None:
            # If the folder is not provided, we generate the spec file in the same folder of the function file.
            folder = pyfile.parent
        if spec_file is None:
            # If the spec file name is not provided, get the name from the file name.
            spec_file = pyfile.with_suffix(SPEC_EXT).name
        self.spec._save_to_code_folder(Path(folder), spec_file)
        return Path(folder) / spec_file

    def get_interface(self):
        """Return the interface of this component.

        :return: A dictionary including the definition of inputs/outputs/params.
        """
        return self._executor.get_interface()

    def execute(self, argv):
        """Execute the component with command line arguments."""
        return self._executor.execute(argv)

    def __call__(self, *args, **kwargs):
        """Directly calling a component executor equals to calling the underlying function directly."""
        return self._func(*args, **kwargs)

    @classmethod
    def collect_component_from_file(
            cls, py_file, working_dir=None, force_reload=False, func_name=None, from_executor=False):
        """Collect single dsl component in a file and return the executors of the components."""
        py_file = Path(py_file).absolute()
        if py_file.suffix != '.py':
            raise ValueError("%s is not a valid py file." % py_file)
        if working_dir is None:
            working_dir = py_file.parent
        working_dir = Path(working_dir).absolute()

        component_path = py_file.relative_to(working_dir).as_posix().split('.')[0].replace('/', '.')

        component = cls.collect_component_from_py_module(
            component_path, working_dir=working_dir, force_reload=force_reload,
            func_name=func_name, from_executor=from_executor)
        if not component and from_executor:
            raise NoDslComponentError(py_file, func_name)
        return component

    @classmethod
    def collect_component_from_py_module(
            cls, py_module, working_dir, force_reload=False, func_name=None, from_executor=False):
        """Collect single dsl component in a py module and return the executors of the components."""
        components = [component for component in cls.collect_components_from_py_module(py_module,
                                                                                       working_dir,
                                                                                       force_reload)]

        def defined_in_current_file(component):
            entry_file = Path(inspect.getfile(component._func))
            component_path = py_module.replace('.', '/') + '.py'
            return Path(entry_file).resolve().absolute() == (Path(working_dir) / component_path).resolve().absolute()

        components = [component for component in components if defined_in_current_file(component)
                      if not func_name or component._func.__name__ == func_name]
        if len(components) == 0:
            return None
        component = components[0]
        entry_file = Path(inspect.getfile(component._func))
        if len(components) > 1:
            if from_executor and not func_name:
                raise RequiredComponentNameError(entry_file)
            else:
                raise TooManyDSLComponentsError(len(components), entry_file)
        return component

    @classmethod
    def collect_components_from_py_module(cls, py_module, working_dir=None, force_reload=False):
        """Collect all components in a python module and return the executors of the components."""
        if isinstance(py_module, str):
            try:
                py_module = _import_component_with_working_dir(py_module, working_dir, force_reload)
            except Exception as e:
                raise ImportError("""Error occurs when import component '%s': %s.\n
                Please make sure all requirements inside conda.yaml has been installed.""" % (py_module, e)) from e
        for _, obj in inspect.getmembers(py_module):
            if cls.look_like_component(obj):
                component = cls(obj)
                component.check_py_module_valid(py_module)
                yield component

    @classmethod
    def look_like_component(cls, f):
        """Return True if f looks like a component."""
        if not isinstance(f, types.FunctionType):
            return False
        if not hasattr(f, cls.INJECTED_FIELD):
            return False
        return True

    @classmethod
    def _get_executor_by_type(cls, type):
        """Get the real executor class according to the type, currently we only support CommandComponent."""
        if type != ComponentType.CommandComponent.value:
            raise DSLComponentDefiningError("Currently only CommandComponent is supported, got '%s'." % type)
        return _CommandComponentExecutor

    def check_py_module_valid(self, py_module):
        """Check whether the entry py module is valid to make sure it could be run in AzureML."""
        return self._executor.check_py_module_valid(py_module)

    def _get_spec_file_path(self, force_regenerate=False):
        """Return the generated spec file path."""
        if not self._spec_file_path or not os.path.exists(self._spec_file_path) or force_regenerate:
            if force_regenerate:
                self._reload_func()
            temp_spec_folder = tempfile.mkdtemp()
            file_name = self.name + SPEC_EXT
            temp_spec_file = (Path(temp_spec_folder) / file_name).absolute()
            # Note: conda file will also be generated if necessary and not valid conda detected.
            self._spec_file_path = self.to_spec_yaml(
                folder=temp_spec_file.parent, spec_file=temp_spec_file.name)
        return self._spec_file_path

    def _update_func(self, func: types.FunctionType):
        # Set the injected field so the function could be used to initializing with `ComponentExecutor(func)`
        setattr(func, self.INJECTED_FIELD, self._raw_spec_args)
        if hasattr(self._executor, '_update_func'):
            self._executor._update_func(func)

    def _reload_func(self):
        """Reload the function to make sure the latest code is used to generate yaml."""
        f = self._func
        module = importlib.import_module(f.__module__)
        # if f.__name__ == '__main__', reload will throw an exception
        if f.__module__ != '__main__':
            from azure.ml.component.dsl._utils import _force_reload_module
            _force_reload_module(module)
        func = getattr(module, f.__name__)
        self._func = func._executor._func if is_dsl_component(func) else func
        executor_cls = self._get_executor_by_type(self.type)
        self._executor = executor_cls(self._func, spec_args=self._raw_spec_args)


class _CommandComponentExecutor:
    SPEC_CLASS = CommandComponentDefinition  # This class is used to initialize a definition instance.
    SPECIAL_FUNC_CHECKERS = {
        'Coroutine': inspect.iscoroutinefunction,
        'Generator': inspect.isgeneratorfunction,
    }
    # This is only available on Py3.6+
    if sys.version_info.major == 3 and sys.version_info.minor > 5:
        SPECIAL_FUNC_CHECKERS['Async generator'] = inspect.isasyncgenfunction

    VALID_SPECIAL_FUNCS = set()

    def __init__(self, func: types.FunctionType, spec_args=None):
        """Initialize a ComponentExecutor with a function."""
        if spec_args is None:
            spec_args = getattr(func, ComponentExecutor.INJECTED_FIELD)
        self._spec_args = copy.deepcopy(spec_args)
        self._assert_valid_func(func)
        # If is dsl component func, set the func as inner func
        self._func = func._executor._func if is_dsl_component(func) else func
        self._arg_mapping = self._analyze_annotations(func)
        self._parallel_inputs = None
        if 'parallel_inputs' in spec_args:
            self._parallel_inputs = _InputFileList(self._spec_args.pop('parallel_inputs'))

    @property
    def type(self):
        return self._spec_args.get('type', ComponentType.CommandComponent.value)

    @property
    def spec(self):
        """
        Return the module spec instance of the component.

        Initialized by the function annotations and the meta data.
        """
        io_properties = self._generate_spec_io_properties(self._arg_mapping, self._parallel_inputs)
        command, args = self._spec_args['command'], io_properties.pop('args')
        spec_args = copy.copy(self._spec_args)
        spec_args['command'] = self.get_command_str_by_command_args(command, args)
        return self.SPEC_CLASS._from_dict({**spec_args, **io_properties})

    @classmethod
    def get_command_str_by_command_args(cls, command, args):
        return ' '.join(command + args)

    def get_interface(self):
        """Return the interface of this component.

        :return: A dictionary including the definition of inputs/outputs/params.
        """
        properties = self._generate_spec_io_properties(self._arg_mapping, self._parallel_inputs)
        properties.pop('args')
        return properties

    def execute(self, argv):
        """Execute the component with command line arguments."""
        args = self._parse(argv)
        run = self._func(**args)
        if self._parallel_inputs is not None:
            run(self._parallel_inputs.load_from_argv(argv))

    def __call__(self, *args, **kwargs):
        """Directly calling a component executor equals to calling the underlying function directly."""
        return self._func(*args, **kwargs)

    @classmethod
    def is_valid_type(cls, type):
        return type in {None, ComponentType.CommandComponent.value}

    def _assert_valid_func(self, func):
        """Check whether the function is valid, if it is not valid, raise."""
        for k, checker in self.SPECIAL_FUNC_CHECKERS.items():
            if k not in self.VALID_SPECIAL_FUNCS:
                if checker(func):
                    raise NotImplementedError("%s function is not supported for %s now." % (k, self.type))

    def check_py_module_valid(self, py_module):
        pass

    @classmethod
    def _parse_with_mapping(cls, argv, arg_mapping):
        """Use the parameters info in arg_mapping to parse commandline params.

        :param argv: Command line arguments like ['--param-name', 'param-value']
        :param arg_mapping: A dict contains the mapping from param key 'param_name' to _ComponentBaseParam
        :return: params: The parsed params used for calling the user function.
        """
        parser = argparse.ArgumentParser()
        for param in arg_mapping.values():
            DSLCommandLineGenerator(param).add_to_arg_parser(parser)
        args, _ = parser.parse_known_args(argv)

        # Convert the string values to real params of the function.
        params = {}
        for name, param in arg_mapping.items():
            val = getattr(args, param.name)
            generator = DSLCommandLineGenerator(param)
            if val is None:
                # Note: here param value only contains user input except default value on function
                if isinstance(param, Output) or (not param.optional and param._default is None):
                    raise RequiredParamParsingError(name=param.name, arg_string=generator.arg_string)
                continue
            # If it is a parameter, we help the user to parse the parameter,
            # if it is an input port, we use load to get the param value of the port,
            # otherwise we just pass the raw value as the param value.
            param_value = val
            if isinstance(param, _Param):
                param_value = param._parse_and_validate(val)
            elif isinstance(param, Input):
                param_value = val
            params[name] = param_value
            # For OutputPath, we will create a folder for it.
            if isinstance(param, Output) and not isinstance(param, _OutputFile) and not Path(val).exists():
                Path(val).mkdir(parents=True, exist_ok=True)
        return params

    def _parse(self, argv):
        return self._parse_with_mapping(argv, self._arg_mapping)

    @classmethod
    def _generate_spec_outputs(cls, arg_mapping) -> dict:
        """Generate output ports of a component, from the return annotation and the arg annotations.

        The outputs including the return values and the special PathOutputPort in args.
        """
        return {val.name: val for val in arg_mapping.values() if isinstance(val, Output)}

    @classmethod
    def _generate_spec_inputs(cls, arg_mapping, parallel_inputs: _InputFileList = None) -> dict:
        """Generate input ports of the component according to the analyzed argument mapping."""
        input_ports = {val.name: val for val in arg_mapping.values() if isinstance(val, Input)}
        parallel_input_ports = {val.name: val for val in parallel_inputs.inputs} if parallel_inputs else {}
        return {**input_ports, **parallel_input_ports}

    @classmethod
    def _generate_spec_params(cls, arg_mapping) -> dict:
        """Generate parameters of the component according to the analyzed argument mapping."""
        return {val.name: val for val in arg_mapping.values() if isinstance(val, _Param)}

    @classmethod
    def _generate_spec_io_properties(cls, arg_mapping, parallel_inputs=None):
        """Generate the required properties for a component spec according to the annotation of a function."""
        inputs = cls._generate_spec_inputs(arg_mapping, parallel_inputs)
        outputs = cls._generate_spec_outputs(arg_mapping)
        params = cls._generate_spec_params(arg_mapping)
        args = []
        for val in list(inputs.values()) + list(outputs.values()) + list(params.values()):
            args.append(DSLCommandLineGenerator(val).arg_group_str())
        return {'inputs': inputs, 'outputs': outputs, 'parameters': params, 'args': args}

    @classmethod
    def _analyze_annotations(cls, func):
        """Analyze the annotation of the function to get the parameter mapping dict and the output port list.
        :param func:
        :return: (param_mapping, output_list)
            param_mapping: The mapping from function param names to input ports/component parameters;
            output_list: The output port list analyzed from return annotations.
        """
        mapping = _get_param_with_standard_annotation(func, is_func=True)
        for key, definition in mapping.items():
            # Not annotated param fall back to String type.
            if isinstance(definition, _Param) and not definition.type:
                definition._type = String.TYPE_NAME
        return mapping

    def _update_func(self, func):
        pass


class _ParallelComponentExecutor(_CommandComponentExecutor):
    """This executor handle parallel component specific operations to enable parallel component."""

    SPEC_CLASS = ParallelRunModuleSpec
    JOB_TYPE = 'parallel'
    FIELDS = {'init', 'run', 'shutdown'}
    CONFLICT_ERROR_TPL = "It is not allowed to declare {}() once a parallel component is defined."
    VALID_SPECIAL_FUNCS = {'Generator'}

    def __init__(self, func: callable, spec_args=None):
        """Initialize a ParallelComponentExecutor with a provided function."""
        super().__init__(func, spec_args)
        if not self._parallel_inputs:
            raise ValueError(
                "Parallel component should have at lease one parallel input, got 0.",
            )
        self._output_keys = [key for key, val in self._arg_mapping.items() if isinstance(val, Output)]
        if len(self._output_keys) == 0:
            raise ValueError(
                "Parallel component should have at least one OutputPath, got %d." % len(self._output_keys)
            )
        self._args = {}
        self._spec_args.update({
            'input_data': [port.name for port in self._parallel_inputs.inputs],
            # We use the first output as the parallel output data.
            # This is only a workaround according to current parallel run design, picking any output port is OK.
            'output_data': self._arg_mapping[self._output_keys[0]].name,
        })
        command = self._spec_args.pop('command')
        self._spec_args['entry'] = command[-1]
        self._spec_args.pop('job_type')
        self._run_func = None
        self._generator = None

    def execute(self, argv, batch_size=4):
        """Execute the component using parallel run style. This is used for local debugging."""
        self.init_argv(argv)

        files = self._parallel_inputs.load_from_argv(argv)
        # Use multiprocessing to run batches.
        count = len(files)
        batches = (count + batch_size - 1) // batch_size
        nprocess = min(max(batches, 1), multiprocessing.cpu_count())
        logger.info("Run %d batches to process %d files." % (batches, count))
        batch_files = [files[i * batch_size: (i + 1) * batch_size] for i in range(batches)]
        with ThreadPool(nprocess) as pool:
            batch_results = pool.map(self.run, batch_files)
        results = []
        for result in batch_results:
            results += result
        shutdown_result = self.shutdown()
        return shutdown_result if shutdown_result is not None else results

    @staticmethod
    def _remove_ambiguous_option_in_argv(argv: list, parse_method):
        """Remove ambiguous options in argv for an argparser method.

        This is a workaround to solve the issue that parallel run will add some other command options
        which will cause the problem 'ambiguous option'.
        """
        pattern = re.compile(r"error: ambiguous option: (\S+) could match")
        while True:
            stderr = StringIO()
            with contextlib.redirect_stderr(stderr):
                try:
                    parse_method(argv)
                except SystemExit:
                    stderr_value = stderr.getvalue()
                    match = pattern.search(stderr_value)
                    if not match:
                        # If we cannot found such pattern, which means other problems is raised, we directly raise.
                        sys.stdout.write(stderr_value)
                        raise
                    # Remove the option_str and the value of it.
                    option_str = match.group(1)
                    logger.debug("Ambiguous option '%s' is found in argv, remove it." % option_str)
                    idx = argv.index(option_str)
                    argv = argv[:idx] + argv[idx + 2:]
                else:
                    # If no exception is raised, return the ready args.
                    return argv

    def init(self):
        """Init params except for the InputFiles with the sys args when initializing parallel component.

        This method will only be called once in one process.
        """
        return self.init_argv(sys.argv)

    def init_argv(self, argv=None):
        """Init params except for the InputFiles with argv."""
        if argv is None:
            argv = sys.argv
        logger.info("Initializing parallel component, argv = %s" % argv)
        mapping = copy.copy(self._arg_mapping)
        argv = self._remove_ambiguous_option_in_argv(
            argv, functools.partial(self._parse_with_mapping, arg_mapping=mapping),
        )
        args = self._parse_with_mapping(argv, mapping)
        logger.info("Parallel component initialized, args = %s" % args)
        ret = self._func(**args)
        # If the init function is a generator, the first yielded result is the run function.
        if isinstance(ret, types.GeneratorType):
            self._generator = ret
            ret = next(ret)

        # Make sure the return result is a callable.
        if callable(ret):
            self._run_func = ret
        else:
            raise TypeError("Return/Yield result of the function must be a callable, got '%s'." % (type(ret)))

        sig = inspect.signature(self._run_func)
        if len(sig.parameters) != 1:
            raise ValueError(
                "The method {}() returned by {}() has incorrect signature {}."
                " It should have exact one parameter.".format(ret.__name__, self._func.__name__, sig)
            )
        return self._run_func

    def run(self, files):
        results = self._run_func(files)
        if results is not None:
            return files
        return results

    def shutdown(self):
        if self._generator:
            # If the function is using yield, call next to run the codes after yield.
            while True:
                try:
                    next(self._generator)
                except StopIteration as e:
                    return e.value

    def check_py_module_valid(self, py_module):
        # For parallel component, the init/run/shutdown in py_module should be
        # _ParallelComponentExecutor.init/run/shutdown
        for attr in self.FIELDS:
            func = getattr(py_module, attr)
            if not self.is_valid_init_run_shutdown(func, attr):
                raise AttributeError(self.CONFLICT_ERROR_TPL.format(attr))

    def _update_func(self, func: types.FunctionType):
        # For a parallel component, we should update init/run/shutdown for the script.
        # See "Write your inference script" in the following link.
        # https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-run-step
        py_module = importlib.import_module(func.__module__)
        for attr in self.FIELDS:
            func = getattr(py_module, attr, None)
            # We don't allow other init/run/shutdown in the script.
            if func is not None and not self.is_valid_init_run_shutdown(func, attr):
                raise AttributeError(self.CONFLICT_ERROR_TPL.format(attr))
            setattr(py_module, attr, getattr(self, attr))

    @classmethod
    def is_valid_init_run_shutdown(cls, func, attr):
        return isinstance(func, types.MethodType) and func.__func__ == getattr(_ParallelComponentExecutor, attr)

    @classmethod
    def _generate_spec_io_properties(cls, arg_mapping, parallel_inputs=None):
        """Generate the required properties for a component spec according to the annotation of a function.

        For parallel component, we need to remove InputFiles and --output in args.
        """
        properties = super()._generate_spec_io_properties(arg_mapping, parallel_inputs)
        args_to_remove = []
        for k, v in arg_mapping.items():
            # InputFiles and the output named --output need to be removed in the arguments.
            # For InputFiles: the control script will handle it and pass the files to run();
            # For the output, the control script will add an arg item --output so we should not define it again.
            if v.to_cli_option_str() == '--output':
                args_to_remove.append(v)
        if parallel_inputs:
            args_to_remove += [port for port in parallel_inputs.inputs]
        args = properties['args']
        for arg in args_to_remove:
            args.remove(arg.arg_group_str())
        return properties

    @property
    def spec(self):
        """
        Return the module spec instance of the component.

        Initialized by the function annotations and the meta data.
        """
        io_properties = self._generate_spec_io_properties(self._arg_mapping, self._parallel_inputs)
        return self.SPEC_CLASS._from_dict({**self._spec_args, **io_properties})

    @classmethod
    def is_valid_type(cls, job_type):
        return job_type == cls.JOB_TYPE
