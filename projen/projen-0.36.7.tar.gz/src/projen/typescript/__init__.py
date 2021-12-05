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
    Component as _Component_2b0ad27f, TypeScriptProject as _TypeScriptProject_a4bb5fa6
)


class Projenrc(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.typescript.Projenrc",
):
    '''(experimental) Sets up a typescript project to use TypeScript for projenrc.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _TypeScriptProject_a4bb5fa6,
        *,
        filename: typing.Optional[builtins.str] = None,
        projen_code_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.ts"
        :param projen_code_dir: (experimental) A directory tree that may contain *.ts files that can be referenced from your projenrc typescript file. Default: "projenrc"

        :stability: experimental
        '''
        options = ProjenrcOptions(filename=filename, projen_code_dir=projen_code_dir)

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.typescript.ProjenrcOptions",
    jsii_struct_bases=[],
    name_mapping={"filename": "filename", "projen_code_dir": "projenCodeDir"},
)
class ProjenrcOptions:
    def __init__(
        self,
        *,
        filename: typing.Optional[builtins.str] = None,
        projen_code_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param filename: (experimental) The name of the projenrc file. Default: ".projenrc.ts"
        :param projen_code_dir: (experimental) A directory tree that may contain *.ts files that can be referenced from your projenrc typescript file. Default: "projenrc"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filename is not None:
            self._values["filename"] = filename
        if projen_code_dir is not None:
            self._values["projen_code_dir"] = projen_code_dir

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the projenrc file.

        :default: ".projenrc.ts"

        :stability: experimental
        '''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projen_code_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory tree that may contain *.ts files that can be referenced from your projenrc typescript file.

        :default: "projenrc"

        :stability: experimental
        '''
        result = self._values.get("projen_code_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjenrcOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Projenrc",
    "ProjenrcOptions",
]

publication.publish()
