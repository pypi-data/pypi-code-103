import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    Component as _Component_2b0ad27f,
    NodeProject as _NodeProject_1f001c1d,
    Project as _Project_57d89203,
)
from ..tasks import Task as _Task_fb843092


@jsii.data_type(
    jsii_type="projen.javascript.Bundle",
    jsii_struct_bases=[],
    name_mapping={
        "bundle_task": "bundleTask",
        "outfile": "outfile",
        "watch_task": "watchTask",
    },
)
class Bundle:
    def __init__(
        self,
        *,
        bundle_task: _Task_fb843092,
        outfile: builtins.str,
        watch_task: typing.Optional[_Task_fb843092] = None,
    ) -> None:
        '''
        :param bundle_task: (experimental) The task that produces this bundle.
        :param outfile: (experimental) Location of the output file (relative to project root).
        :param watch_task: (experimental) The "watch" task for this bundle.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bundle_task": bundle_task,
            "outfile": outfile,
        }
        if watch_task is not None:
            self._values["watch_task"] = watch_task

    @builtins.property
    def bundle_task(self) -> _Task_fb843092:
        '''(experimental) The task that produces this bundle.

        :stability: experimental
        '''
        result = self._values.get("bundle_task")
        assert result is not None, "Required property 'bundle_task' is missing"
        return typing.cast(_Task_fb843092, result)

    @builtins.property
    def outfile(self) -> builtins.str:
        '''(experimental) Location of the output file (relative to project root).

        :stability: experimental
        '''
        result = self._values.get("outfile")
        assert result is not None, "Required property 'outfile' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def watch_task(self) -> typing.Optional[_Task_fb843092]:
        '''(experimental) The "watch" task for this bundle.

        :stability: experimental
        '''
        result = self._values.get("watch_task")
        return typing.cast(typing.Optional[_Task_fb843092], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Bundle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Bundler(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.javascript.Bundler",
):
    '''(experimental) Adds support for bundling JavaScript applications and dependencies into a single file.

    In the future, this will also supports bundling websites.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        assets_dir: typing.Optional[builtins.str] = None,
        esbuild_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a ``Bundler``.

        :param project: -
        :param assets_dir: (experimental) Output directory for all bundles. Default: "assets"
        :param esbuild_version: (experimental) The semantic version requirement for ``esbuild``. Default: - no specific version (implies latest)

        :stability: experimental
        '''
        options = BundlerOptions(
            assets_dir=assets_dir, esbuild_version=esbuild_version
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, project: _Project_57d89203) -> typing.Optional["Bundler"]:
        '''(experimental) Returns the ``Bundler`` instance associated with a project or ``undefined`` if there is no Bundler.

        :param project: The project.

        :return: A bundler

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Bundler"], jsii.sinvoke(cls, "of", [project]))

    @jsii.member(jsii_name="addBundle")
    def add_bundle(
        self,
        entrypoint: builtins.str,
        *,
        platform: builtins.str,
        target: builtins.str,
        externals: typing.Optional[typing.Sequence[builtins.str]] = None,
        sourcemap: typing.Optional[builtins.bool] = None,
        watch_task: typing.Optional[builtins.bool] = None,
    ) -> Bundle:
        '''(experimental) Adds a task to the project which bundles a specific entrypoint and all of its dependencies into a single javascript output file.

        :param entrypoint: The relative path of the artifact within the project.
        :param platform: (experimental) esbuild platform.
        :param target: (experimental) esbuild target.
        :param externals: (experimental) You can mark a file or a package as external to exclude it from your build. Instead of being bundled, the import will be preserved (using require for the iife and cjs formats and using import for the esm format) and will be evaluated at run time instead. This has several uses. First of all, it can be used to trim unnecessary code from your bundle for a code path that you know will never be executed. For example, a package may contain code that only runs in node but you will only be using that package in the browser. It can also be used to import code in node at run time from a package that cannot be bundled. For example, the fsevents package contains a native extension, which esbuild doesn't support. Default: []
        :param sourcemap: (experimental) Include a source map in the bundle. Default: false
        :param watch_task: (experimental) In addition to the ``bundle:xyz`` task, creates ``bundle:xyz:watch`` task which will invoke the same esbuild command with the ``--watch`` flag. This can be used to continusouly watch for changes. Default: true

        :stability: experimental
        '''
        options = AddBundleOptions(
            platform=platform,
            target=target,
            externals=externals,
            sourcemap=sourcemap,
            watch_task=watch_task,
        )

        return typing.cast(Bundle, jsii.invoke(self, "addBundle", [entrypoint, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundledir")
    def bundledir(self) -> builtins.str:
        '''(experimental) Root bundle directory.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bundledir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleTask")
    def bundle_task(self) -> _Task_fb843092:
        '''(experimental) Gets or creates the singleton "bundle" task of the project.

        If the project doesn't have a "bundle" task, it will be created and spawned
        during the pre-compile phase.

        :stability: experimental
        '''
        return typing.cast(_Task_fb843092, jsii.get(self, "bundleTask"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="esbuildVersion")
    def esbuild_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The semantic version requirement for ``esbuild`` (if defined).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "esbuildVersion"))


@jsii.data_type(
    jsii_type="projen.javascript.BundlerOptions",
    jsii_struct_bases=[],
    name_mapping={"assets_dir": "assetsDir", "esbuild_version": "esbuildVersion"},
)
class BundlerOptions:
    def __init__(
        self,
        *,
        assets_dir: typing.Optional[builtins.str] = None,
        esbuild_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``Bundler``.

        :param assets_dir: (experimental) Output directory for all bundles. Default: "assets"
        :param esbuild_version: (experimental) The semantic version requirement for ``esbuild``. Default: - no specific version (implies latest)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if assets_dir is not None:
            self._values["assets_dir"] = assets_dir
        if esbuild_version is not None:
            self._values["esbuild_version"] = esbuild_version

    @builtins.property
    def assets_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Output directory for all bundles.

        :default: "assets"

        :stability: experimental
        '''
        result = self._values.get("assets_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def esbuild_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The semantic version requirement for ``esbuild``.

        :default: - no specific version (implies latest)

        :stability: experimental
        '''
        result = self._values.get("esbuild_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BundlerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.javascript.BundlingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "externals": "externals",
        "sourcemap": "sourcemap",
        "watch_task": "watchTask",
    },
)
class BundlingOptions:
    def __init__(
        self,
        *,
        externals: typing.Optional[typing.Sequence[builtins.str]] = None,
        sourcemap: typing.Optional[builtins.bool] = None,
        watch_task: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for bundling.

        :param externals: (experimental) You can mark a file or a package as external to exclude it from your build. Instead of being bundled, the import will be preserved (using require for the iife and cjs formats and using import for the esm format) and will be evaluated at run time instead. This has several uses. First of all, it can be used to trim unnecessary code from your bundle for a code path that you know will never be executed. For example, a package may contain code that only runs in node but you will only be using that package in the browser. It can also be used to import code in node at run time from a package that cannot be bundled. For example, the fsevents package contains a native extension, which esbuild doesn't support. Default: []
        :param sourcemap: (experimental) Include a source map in the bundle. Default: false
        :param watch_task: (experimental) In addition to the ``bundle:xyz`` task, creates ``bundle:xyz:watch`` task which will invoke the same esbuild command with the ``--watch`` flag. This can be used to continusouly watch for changes. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if externals is not None:
            self._values["externals"] = externals
        if sourcemap is not None:
            self._values["sourcemap"] = sourcemap
        if watch_task is not None:
            self._values["watch_task"] = watch_task

    @builtins.property
    def externals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) You can mark a file or a package as external to exclude it from your build.

        Instead of being bundled, the import will be preserved (using require for
        the iife and cjs formats and using import for the esm format) and will be
        evaluated at run time instead.

        This has several uses. First of all, it can be used to trim unnecessary
        code from your bundle for a code path that you know will never be executed.
        For example, a package may contain code that only runs in node but you will
        only be using that package in the browser. It can also be used to import
        code in node at run time from a package that cannot be bundled. For
        example, the fsevents package contains a native extension, which esbuild
        doesn't support.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("externals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sourcemap(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a source map in the bundle.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("sourcemap")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def watch_task(self) -> typing.Optional[builtins.bool]:
        '''(experimental) In addition to the ``bundle:xyz`` task, creates ``bundle:xyz:watch`` task which will invoke the same esbuild command with the ``--watch`` flag.

        This can be used
        to continusouly watch for changes.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("watch_task")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BundlingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NpmConfig(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.javascript.NpmConfig",
):
    '''(experimental) File representing the local NPM config in .npmrc.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _NodeProject_1f001c1d,
        *,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param registry: (experimental) URL of the registry mirror to use. You can change this or add scoped registries using the addRegistry method Default: - use npmjs default registry

        :stability: experimental
        '''
        options = NpmConfigOptions(registry=registry)

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addConfig")
    def add_config(self, name: builtins.str, value: builtins.str) -> None:
        '''(experimental) configure a generic property.

        :param name: the name of the property.
        :param value: the value of the property.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addConfig", [name, value]))

    @jsii.member(jsii_name="addRegistry")
    def add_registry(
        self,
        url: builtins.str,
        scope: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) configure a scoped registry.

        :param url: the URL of the registry to use.
        :param scope: the scope the registry is used for; leave empty for the default registry

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addRegistry", [url, scope]))


@jsii.data_type(
    jsii_type="projen.javascript.NpmConfigOptions",
    jsii_struct_bases=[],
    name_mapping={"registry": "registry"},
)
class NpmConfigOptions:
    def __init__(self, *, registry: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Options to configure the local NPM config.

        :param registry: (experimental) URL of the registry mirror to use. You can change this or add scoped registries using the addRegistry method Default: - use npmjs default registry

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL of the registry mirror to use.

        You can change this or add scoped registries using the addRegistry method

        :default: - use npmjs default registry

        :stability: experimental
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NpmConfigOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Projenrc(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.javascript.Projenrc",
):
    '''(experimental) Sets up a javascript project to use TypeScript for projenrc.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        filename: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.js"

        :stability: experimental
        '''
        options = ProjenrcOptions(filename=filename)

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.javascript.ProjenrcOptions",
    jsii_struct_bases=[],
    name_mapping={"filename": "filename"},
)
class ProjenrcOptions:
    def __init__(self, *, filename: typing.Optional[builtins.str] = None) -> None:
        '''
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.js"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filename is not None:
            self._values["filename"] = filename

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the projenrc file.

        :default: ".projenrc.js"

        :stability: experimental
        '''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjenrcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.javascript.AddBundleOptions",
    jsii_struct_bases=[BundlingOptions],
    name_mapping={
        "externals": "externals",
        "sourcemap": "sourcemap",
        "watch_task": "watchTask",
        "platform": "platform",
        "target": "target",
    },
)
class AddBundleOptions(BundlingOptions):
    def __init__(
        self,
        *,
        externals: typing.Optional[typing.Sequence[builtins.str]] = None,
        sourcemap: typing.Optional[builtins.bool] = None,
        watch_task: typing.Optional[builtins.bool] = None,
        platform: builtins.str,
        target: builtins.str,
    ) -> None:
        '''(experimental) Options for ``addBundle()``.

        :param externals: (experimental) You can mark a file or a package as external to exclude it from your build. Instead of being bundled, the import will be preserved (using require for the iife and cjs formats and using import for the esm format) and will be evaluated at run time instead. This has several uses. First of all, it can be used to trim unnecessary code from your bundle for a code path that you know will never be executed. For example, a package may contain code that only runs in node but you will only be using that package in the browser. It can also be used to import code in node at run time from a package that cannot be bundled. For example, the fsevents package contains a native extension, which esbuild doesn't support. Default: []
        :param sourcemap: (experimental) Include a source map in the bundle. Default: false
        :param watch_task: (experimental) In addition to the ``bundle:xyz`` task, creates ``bundle:xyz:watch`` task which will invoke the same esbuild command with the ``--watch`` flag. This can be used to continusouly watch for changes. Default: true
        :param platform: (experimental) esbuild platform.
        :param target: (experimental) esbuild target.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "platform": platform,
            "target": target,
        }
        if externals is not None:
            self._values["externals"] = externals
        if sourcemap is not None:
            self._values["sourcemap"] = sourcemap
        if watch_task is not None:
            self._values["watch_task"] = watch_task

    @builtins.property
    def externals(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) You can mark a file or a package as external to exclude it from your build.

        Instead of being bundled, the import will be preserved (using require for
        the iife and cjs formats and using import for the esm format) and will be
        evaluated at run time instead.

        This has several uses. First of all, it can be used to trim unnecessary
        code from your bundle for a code path that you know will never be executed.
        For example, a package may contain code that only runs in node but you will
        only be using that package in the browser. It can also be used to import
        code in node at run time from a package that cannot be bundled. For
        example, the fsevents package contains a native extension, which esbuild
        doesn't support.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("externals")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sourcemap(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include a source map in the bundle.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("sourcemap")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def watch_task(self) -> typing.Optional[builtins.bool]:
        '''(experimental) In addition to the ``bundle:xyz`` task, creates ``bundle:xyz:watch`` task which will invoke the same esbuild command with the ``--watch`` flag.

        This can be used
        to continusouly watch for changes.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("watch_task")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def platform(self) -> builtins.str:
        '''(experimental) esbuild platform.

        :stability: experimental

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            "node"
        '''
        result = self._values.get("platform")
        assert result is not None, "Required property 'platform' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''(experimental) esbuild target.

        :stability: experimental

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            "node12"
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddBundleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddBundleOptions",
    "Bundle",
    "Bundler",
    "BundlerOptions",
    "BundlingOptions",
    "NpmConfig",
    "NpmConfigOptions",
    "Projenrc",
    "ProjenrcOptions",
]

publication.publish()
