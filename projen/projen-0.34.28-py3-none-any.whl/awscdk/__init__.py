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
    JsonFile as _JsonFile_fa8164db,
    LoggerOptions as _LoggerOptions_eb0f6309,
    Project as _Project_57d89203,
    ProjectType as _ProjectType_fd80c725,
    SampleReadmeProps as _SampleReadmeProps_3518b03b,
)
from ..github import (
    AutoApproveOptions as _AutoApproveOptions_dac86cbe,
    AutoMergeOptions as _AutoMergeOptions_d112cd3c,
    GitHubOptions as _GitHubOptions_21553699,
    MergifyOptions as _MergifyOptions_a6faaab3,
    StaleOptions as _StaleOptions_929db764,
)
from ..java import (
    JavaProject as _JavaProject_7f51a7ab,
    JavaProjectOptions as _JavaProjectOptions_7dbf778f,
    JunitOptions as _JunitOptions_e5b597b7,
    MavenCompileOptions as _MavenCompileOptions_c5c0ec48,
    MavenPackagingOptions as _MavenPackagingOptions_bc96fb36,
    ProjenrcOptions as _ProjenrcOptions_65cd3dd8,
)
from ..javascript import BundlingOptions as _BundlingOptions_fc10f395
from ..json import ProjenrcOptions as _ProjenrcOptions_985561af
from ..tasks import Task as _Task_fb843092


@jsii.enum(jsii_type="projen.awscdk.ApprovalLevel")
class ApprovalLevel(enum.Enum):
    '''(experimental) Which approval is required when deploying CDK apps.

    :stability: experimental
    '''

    NEVER = "NEVER"
    '''(experimental) Approval is never required.

    :stability: experimental
    '''
    ANY_CHANGE = "ANY_CHANGE"
    '''(experimental) Requires approval on any IAM or security-group-related change.

    :stability: experimental
    '''
    BROADENING = "BROADENING"
    '''(experimental) Requires approval when IAM statements or traffic rules are added;

    removals don't require approval

    :stability: experimental
    '''


class AutoDiscover(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.awscdk.AutoDiscover",
):
    '''(experimental) Automatically creates a ``LambdaFunction`` for all ``.lambda.ts`` files under the source directory of the project.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        srcdir: builtins.str,
        lambda_options: typing.Optional["LambdaFunctionCommonOptions"] = None,
    ) -> None:
        '''
        :param project: -
        :param srcdir: (experimental) Project source tree (relative to project output directory).
        :param lambda_options: (experimental) Options for auto-discovery of AWS Lambda functions.

        :stability: experimental
        '''
        options = AutoDiscoverOptions(srcdir=srcdir, lambda_options=lambda_options)

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.awscdk.AutoDiscoverOptions",
    jsii_struct_bases=[],
    name_mapping={"srcdir": "srcdir", "lambda_options": "lambdaOptions"},
)
class AutoDiscoverOptions:
    def __init__(
        self,
        *,
        srcdir: builtins.str,
        lambda_options: typing.Optional["LambdaFunctionCommonOptions"] = None,
    ) -> None:
        '''(experimental) Options for ``AutoDiscover``.

        :param srcdir: (experimental) Project source tree (relative to project output directory).
        :param lambda_options: (experimental) Options for auto-discovery of AWS Lambda functions.

        :stability: experimental
        '''
        if isinstance(lambda_options, dict):
            lambda_options = LambdaFunctionCommonOptions(**lambda_options)
        self._values: typing.Dict[str, typing.Any] = {
            "srcdir": srcdir,
        }
        if lambda_options is not None:
            self._values["lambda_options"] = lambda_options

    @builtins.property
    def srcdir(self) -> builtins.str:
        '''(experimental) Project source tree (relative to project output directory).

        :stability: experimental
        '''
        result = self._values.get("srcdir")
        assert result is not None, "Required property 'srcdir' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_options(self) -> typing.Optional["LambdaFunctionCommonOptions"]:
        '''(experimental) Options for auto-discovery of AWS Lambda functions.

        :stability: experimental
        '''
        result = self._values.get("lambda_options")
        return typing.cast(typing.Optional["LambdaFunctionCommonOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoDiscoverOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsCdkJavaApp(
    _JavaProject_7f51a7ab,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.awscdk.AwsCdkJavaApp",
):
    '''(experimental) AWS CDK app in Java.

    :stability: experimental
    :pjid: awscdk-app-java
    '''

    def __init__(
        self,
        *,
        cdk_version: builtins.str,
        main_class: builtins.str,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample: typing.Optional[builtins.bool] = None,
        sample_java_package: typing.Optional[builtins.str] = None,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[ApprovalLevel] = None,
        compile_options: typing.Optional[_MavenCompileOptions_c5c0ec48] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        distdir: typing.Optional[builtins.str] = None,
        junit: typing.Optional[builtins.bool] = None,
        junit_options: typing.Optional[_JunitOptions_e5b597b7] = None,
        packaging_options: typing.Optional[_MavenPackagingOptions_bc96fb36] = None,
        projenrc_java: typing.Optional[builtins.bool] = None,
        projenrc_java_options: typing.Optional[_ProjenrcOptions_65cd3dd8] = None,
        test_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_approve_options: typing.Optional[_AutoApproveOptions_dac86cbe] = None,
        auto_merge_options: typing.Optional[_AutoMergeOptions_d112cd3c] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[_GitHubOptions_21553699] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[_MergifyOptions_a6faaab3] = None,
        project_type: typing.Optional[_ProjectType_fd80c725] = None,
        readme: typing.Optional[_SampleReadmeProps_3518b03b] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[_StaleOptions_929db764] = None,
        vscode: typing.Optional[builtins.bool] = None,
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_985561af] = None,
    ) -> None:
        '''
        :param cdk_version: (experimental) AWS CDK version to use (you can use semantic versioning). Default: "^1.130.0"
        :param main_class: (experimental) The name of the Java class with the static ``main()`` method. This method should call ``app.synth()`` on the CDK app. Default: "org.acme.App"
        :param cdk_dependencies: (experimental) Which AWS CDK modules this app uses. The ``core`` module is included by default and you can add additional modules here by stating only the package name (e.g. ``aws-lambda``).
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist.
        :param sample_java_package: (experimental) The java package to use for the code sample. Default: "org.acme"
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param compile_options: (experimental) Compile options. Default: - defaults
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param distdir: (experimental) Final artifact output directory. Default: "dist/java"
        :param junit: (experimental) Include junit tests. Default: true
        :param junit_options: (experimental) junit options. Default: - defaults
        :param packaging_options: (experimental) Packaging options. Default: - defaults
        :param projenrc_java: (experimental) Use projenrc in java. This will install ``projen`` as a java dependency and will add a ``synth`` task which will compile & execute ``main()`` from ``src/main/java/projenrc.java``. Default: true
        :param projenrc_java_options: (experimental) Options related to projenrc in java. Default: - default options
        :param test_deps: (experimental) List of test dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addTestDependency()``. Default: []
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options

        :stability: experimental
        '''
        options = AwsCdkJavaAppOptions(
            cdk_version=cdk_version,
            main_class=main_class,
            cdk_dependencies=cdk_dependencies,
            sample=sample,
            sample_java_package=sample_java_package,
            cdkout=cdkout,
            context=context,
            feature_flags=feature_flags,
            require_approval=require_approval,
            compile_options=compile_options,
            deps=deps,
            distdir=distdir,
            junit=junit,
            junit_options=junit_options,
            packaging_options=packaging_options,
            projenrc_java=projenrc_java,
            projenrc_java_options=projenrc_java_options,
            test_deps=test_deps,
            auto_approve_options=auto_approve_options,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            artifact_id=artifact_id,
            group_id=group_id,
            version=version,
            description=description,
            packaging=packaging,
            url=url,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="addCdkDependency")
    def add_cdk_dependency(self, *modules: builtins.str) -> None:
        '''(experimental) Adds an AWS CDK module dependencies.

        :param modules: The list of modules to depend on (e.g. "core", "aws-lambda", etc).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addCdkDependency", [*modules]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdkConfig")
    def cdk_config(self) -> "CdkConfig":
        '''(experimental) The ``cdk.json`` file.

        :stability: experimental
        '''
        return typing.cast("CdkConfig", jsii.get(self, "cdkConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdkTasks")
    def cdk_tasks(self) -> "CdkTasks":
        '''(experimental) CDK tasks.

        :stability: experimental
        '''
        return typing.cast("CdkTasks", jsii.get(self, "cdkTasks"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdkVersion")
    def cdk_version(self) -> builtins.str:
        '''(experimental) The CDK version this app is using.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "cdkVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainClass")
    def main_class(self) -> builtins.str:
        '''(experimental) The full name of the main class of the java app (package.Class).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "mainClass"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainClassName")
    def main_class_name(self) -> builtins.str:
        '''(experimental) The name of the Java class with the static ``main()`` method.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "mainClassName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mainPackage")
    def main_package(self) -> builtins.str:
        '''(experimental) The name of the Java package that includes the main class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "mainPackage"))


class CdkConfig(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.awscdk.CdkConfig",
):
    '''(experimental) Represents cdk.json file.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        app: builtins.str,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[ApprovalLevel] = None,
    ) -> None:
        '''
        :param project: -
        :param app: (experimental) The command line to execute in order to synthesize the CDK application (language specific).
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        options = CdkConfigOptions(
            app=app,
            cdkout=cdkout,
            context=context,
            feature_flags=feature_flags,
            require_approval=require_approval,
        )

        jsii.create(self.__class__, self, [project, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cdkout")
    def cdkout(self) -> builtins.str:
        '''(experimental) Name of the cdk.out directory.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "cdkout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="json")
    def json(self) -> _JsonFile_fa8164db:
        '''(experimental) Represents the JSON file.

        :stability: experimental
        '''
        return typing.cast(_JsonFile_fa8164db, jsii.get(self, "json"))


@jsii.data_type(
    jsii_type="projen.awscdk.CdkConfigCommonOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cdkout": "cdkout",
        "context": "context",
        "feature_flags": "featureFlags",
        "require_approval": "requireApproval",
    },
)
class CdkConfigCommonOptions:
    def __init__(
        self,
        *,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[ApprovalLevel] = None,
    ) -> None:
        '''(experimental) Common options for ``cdk.json``.

        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cdkout is not None:
            self._values["cdkout"] = cdkout
        if context is not None:
            self._values["context"] = context
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if require_approval is not None:
            self._values["require_approval"] = require_approval

    @builtins.property
    def cdkout(self) -> typing.Optional[builtins.str]:
        '''(experimental) cdk.out directory.

        :default: "cdk.out"

        :stability: experimental
        '''
        result = self._values.get("cdkout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional context to include in ``cdk.json``.

        :default: - no additional context

        :stability: experimental
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include all feature flags in cdk.json.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[ApprovalLevel]:
        '''(experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them.

        :default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[ApprovalLevel], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkConfigCommonOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.awscdk.CdkConfigOptions",
    jsii_struct_bases=[CdkConfigCommonOptions],
    name_mapping={
        "cdkout": "cdkout",
        "context": "context",
        "feature_flags": "featureFlags",
        "require_approval": "requireApproval",
        "app": "app",
    },
)
class CdkConfigOptions(CdkConfigCommonOptions):
    def __init__(
        self,
        *,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[ApprovalLevel] = None,
        app: builtins.str,
    ) -> None:
        '''(experimental) Options for ``CdkJson``.

        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param app: (experimental) The command line to execute in order to synthesize the CDK application (language specific).

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app": app,
        }
        if cdkout is not None:
            self._values["cdkout"] = cdkout
        if context is not None:
            self._values["context"] = context
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if require_approval is not None:
            self._values["require_approval"] = require_approval

    @builtins.property
    def cdkout(self) -> typing.Optional[builtins.str]:
        '''(experimental) cdk.out directory.

        :default: "cdk.out"

        :stability: experimental
        '''
        result = self._values.get("cdkout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional context to include in ``cdk.json``.

        :default: - no additional context

        :stability: experimental
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include all feature flags in cdk.json.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[ApprovalLevel]:
        '''(experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them.

        :default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[ApprovalLevel], result)

    @builtins.property
    def app(self) -> builtins.str:
        '''(experimental) The command line to execute in order to synthesize the CDK application (language specific).

        :stability: experimental
        '''
        result = self._values.get("app")
        assert result is not None, "Required property 'app' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkConfigOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdkTasks(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.awscdk.CdkTasks",
):
    '''(experimental) Adds standard AWS CDK tasks to your project.

    :stability: experimental
    '''

    def __init__(self, project: _Project_57d89203) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [project])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploy")
    def deploy(self) -> _Task_fb843092:
        '''(experimental) Deploys your app.

        :stability: experimental
        '''
        return typing.cast(_Task_fb843092, jsii.get(self, "deploy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroy")
    def destroy(self) -> _Task_fb843092:
        '''(experimental) Destroys all the stacks.

        :stability: experimental
        '''
        return typing.cast(_Task_fb843092, jsii.get(self, "destroy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="diff")
    def diff(self) -> _Task_fb843092:
        '''(experimental) Diff against production.

        :stability: experimental
        '''
        return typing.cast(_Task_fb843092, jsii.get(self, "diff"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="synth")
    def synth(self) -> _Task_fb843092:
        '''(experimental) Synthesizes your app.

        :stability: experimental
        '''
        return typing.cast(_Task_fb843092, jsii.get(self, "synth"))


class LambdaFunction(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.awscdk.LambdaFunction",
):
    '''(experimental) Generates a pre-bundled AWS Lambda function construct from handler code.

    To use this, create an AWS Lambda handler file under your source tree with
    the ``.lambda.ts`` extension and add a ``LambdaFunction`` component to your
    typescript project pointing to this entrypoint.

    This will add a task to your "compile" step which will use ``esbuild`` to
    bundle the handler code into the build directory. It will also generate a
    file ``src/foo-function.ts`` with a custom AWS construct called ``FooFunction``
    which extends ``@aws-cdk/aws-lambda.Function`` which is bound to the bundled
    handle through an asset.

    :stability: experimental

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        LambdaFunction(my_project,
            srcdir=my_project.srcdir,
            entrypoint="src/foo.lambda.ts"
        )
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        entrypoint: builtins.str,
        construct_file: typing.Optional[builtins.str] = None,
        construct_name: typing.Optional[builtins.str] = None,
        bundling_options: typing.Optional[_BundlingOptions_fc10f395] = None,
        runtime: typing.Optional["LambdaRuntime"] = None,
    ) -> None:
        '''(experimental) Defines a pre-bundled AWS Lambda function construct from handler code.

        :param project: The project to use.
        :param entrypoint: (experimental) A path from the project root directory to a TypeScript file which contains the AWS Lambda handler entrypoint (exports a ``handler`` function). This is relative to the root directory of the project.
        :param construct_file: (experimental) The name of the generated TypeScript source file. This file should also be under the source tree. Default: - The name of the entrypoint file, with the ``-function.ts`` suffix instead of ``.lambda.ts``.
        :param construct_name: (experimental) The name of the generated ``lambda.Function`` subclass. Default: - A pascal cased version of the name of the entrypoint file, with the extension ``Function`` (e.g. ``ResizeImageFunction``).
        :param bundling_options: (experimental) Bundling options for this AWS Lambda function. If not specified the default bundling options specified for the project ``Bundler`` instance will be used. Default: - defaults
        :param runtime: (experimental) The node.js version to target. Default: Runtime.NODEJS_14_X

        :stability: experimental
        '''
        options = LambdaFunctionOptions(
            entrypoint=entrypoint,
            construct_file=construct_file,
            construct_name=construct_name,
            bundling_options=bundling_options,
            runtime=runtime,
        )

        jsii.create(self.__class__, self, [project, options])


@jsii.data_type(
    jsii_type="projen.awscdk.LambdaFunctionCommonOptions",
    jsii_struct_bases=[],
    name_mapping={"bundling_options": "bundlingOptions", "runtime": "runtime"},
)
class LambdaFunctionCommonOptions:
    def __init__(
        self,
        *,
        bundling_options: typing.Optional[_BundlingOptions_fc10f395] = None,
        runtime: typing.Optional["LambdaRuntime"] = None,
    ) -> None:
        '''(experimental) Common options for ``LambdaFunction``.

        Applies to all functions in
        auto-discovery.

        :param bundling_options: (experimental) Bundling options for this AWS Lambda function. If not specified the default bundling options specified for the project ``Bundler`` instance will be used. Default: - defaults
        :param runtime: (experimental) The node.js version to target. Default: Runtime.NODEJS_14_X

        :stability: experimental
        '''
        if isinstance(bundling_options, dict):
            bundling_options = _BundlingOptions_fc10f395(**bundling_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if bundling_options is not None:
            self._values["bundling_options"] = bundling_options
        if runtime is not None:
            self._values["runtime"] = runtime

    @builtins.property
    def bundling_options(self) -> typing.Optional[_BundlingOptions_fc10f395]:
        '''(experimental) Bundling options for this AWS Lambda function.

        If not specified the default bundling options specified for the project
        ``Bundler`` instance will be used.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("bundling_options")
        return typing.cast(typing.Optional[_BundlingOptions_fc10f395], result)

    @builtins.property
    def runtime(self) -> typing.Optional["LambdaRuntime"]:
        '''(experimental) The node.js version to target.

        :default: Runtime.NODEJS_14_X

        :stability: experimental
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional["LambdaRuntime"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionCommonOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.awscdk.LambdaFunctionOptions",
    jsii_struct_bases=[LambdaFunctionCommonOptions],
    name_mapping={
        "bundling_options": "bundlingOptions",
        "runtime": "runtime",
        "entrypoint": "entrypoint",
        "construct_file": "constructFile",
        "construct_name": "constructName",
    },
)
class LambdaFunctionOptions(LambdaFunctionCommonOptions):
    def __init__(
        self,
        *,
        bundling_options: typing.Optional[_BundlingOptions_fc10f395] = None,
        runtime: typing.Optional["LambdaRuntime"] = None,
        entrypoint: builtins.str,
        construct_file: typing.Optional[builtins.str] = None,
        construct_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``Function``.

        :param bundling_options: (experimental) Bundling options for this AWS Lambda function. If not specified the default bundling options specified for the project ``Bundler`` instance will be used. Default: - defaults
        :param runtime: (experimental) The node.js version to target. Default: Runtime.NODEJS_14_X
        :param entrypoint: (experimental) A path from the project root directory to a TypeScript file which contains the AWS Lambda handler entrypoint (exports a ``handler`` function). This is relative to the root directory of the project.
        :param construct_file: (experimental) The name of the generated TypeScript source file. This file should also be under the source tree. Default: - The name of the entrypoint file, with the ``-function.ts`` suffix instead of ``.lambda.ts``.
        :param construct_name: (experimental) The name of the generated ``lambda.Function`` subclass. Default: - A pascal cased version of the name of the entrypoint file, with the extension ``Function`` (e.g. ``ResizeImageFunction``).

        :stability: experimental
        '''
        if isinstance(bundling_options, dict):
            bundling_options = _BundlingOptions_fc10f395(**bundling_options)
        self._values: typing.Dict[str, typing.Any] = {
            "entrypoint": entrypoint,
        }
        if bundling_options is not None:
            self._values["bundling_options"] = bundling_options
        if runtime is not None:
            self._values["runtime"] = runtime
        if construct_file is not None:
            self._values["construct_file"] = construct_file
        if construct_name is not None:
            self._values["construct_name"] = construct_name

    @builtins.property
    def bundling_options(self) -> typing.Optional[_BundlingOptions_fc10f395]:
        '''(experimental) Bundling options for this AWS Lambda function.

        If not specified the default bundling options specified for the project
        ``Bundler`` instance will be used.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("bundling_options")
        return typing.cast(typing.Optional[_BundlingOptions_fc10f395], result)

    @builtins.property
    def runtime(self) -> typing.Optional["LambdaRuntime"]:
        '''(experimental) The node.js version to target.

        :default: Runtime.NODEJS_14_X

        :stability: experimental
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional["LambdaRuntime"], result)

    @builtins.property
    def entrypoint(self) -> builtins.str:
        '''(experimental) A path from the project root directory to a TypeScript file which contains the AWS Lambda handler entrypoint (exports a ``handler`` function).

        This is relative to the root directory of the project.

        :stability: experimental

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            "src/subdir/foo.lambda.ts"
        '''
        result = self._values.get("entrypoint")
        assert result is not None, "Required property 'entrypoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def construct_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the generated TypeScript source file.

        This file should also be
        under the source tree.

        :default:

        - The name of the entrypoint file, with the ``-function.ts`` suffix
        instead of ``.lambda.ts``.

        :stability: experimental
        '''
        result = self._values.get("construct_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def construct_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the generated ``lambda.Function`` subclass.

        :default:

        - A pascal cased version of the name of the entrypoint file, with
        the extension ``Function`` (e.g. ``ResizeImageFunction``).

        :stability: experimental
        '''
        result = self._values.get("construct_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaFunctionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaRuntime(metaclass=jsii.JSIIMeta, jsii_type="projen.awscdk.LambdaRuntime"):
    '''(experimental) The runtime for the AWS Lambda function.

    :stability: experimental
    '''

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NODEJS_10_X")
    def NODEJS_10_X(cls) -> "LambdaRuntime":
        '''(experimental) Node.js 10.x.

        :stability: experimental
        '''
        return typing.cast("LambdaRuntime", jsii.sget(cls, "NODEJS_10_X"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NODEJS_12_X")
    def NODEJS_12_X(cls) -> "LambdaRuntime":
        '''(experimental) Node.js 12.x.

        :stability: experimental
        '''
        return typing.cast("LambdaRuntime", jsii.sget(cls, "NODEJS_12_X"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NODEJS_14_X")
    def NODEJS_14_X(cls) -> "LambdaRuntime":
        '''(experimental) Node.js 14.x.

        :stability: experimental
        '''
        return typing.cast("LambdaRuntime", jsii.sget(cls, "NODEJS_14_X"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="esbuildPlatform")
    def esbuild_platform(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "esbuildPlatform"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="esbuildTarget")
    def esbuild_target(self) -> builtins.str:
        '''(experimental) The esbuild setting to use.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "esbuildTarget"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionRuntime")
    def function_runtime(self) -> builtins.str:
        '''(experimental) The aws-lambda.Runtime member name to use.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionRuntime"))


@jsii.data_type(
    jsii_type="projen.awscdk.AwsCdkJavaAppOptions",
    jsii_struct_bases=[_JavaProjectOptions_7dbf778f, CdkConfigCommonOptions],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
        "artifact_id": "artifactId",
        "group_id": "groupId",
        "version": "version",
        "description": "description",
        "packaging": "packaging",
        "url": "url",
        "compile_options": "compileOptions",
        "deps": "deps",
        "distdir": "distdir",
        "junit": "junit",
        "junit_options": "junitOptions",
        "packaging_options": "packagingOptions",
        "projenrc_java": "projenrcJava",
        "projenrc_java_options": "projenrcJavaOptions",
        "test_deps": "testDeps",
        "sample": "sample",
        "sample_java_package": "sampleJavaPackage",
        "cdkout": "cdkout",
        "context": "context",
        "feature_flags": "featureFlags",
        "require_approval": "requireApproval",
        "cdk_version": "cdkVersion",
        "main_class": "mainClass",
        "cdk_dependencies": "cdkDependencies",
    },
)
class AwsCdkJavaAppOptions(_JavaProjectOptions_7dbf778f, CdkConfigCommonOptions):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_985561af] = None,
        auto_approve_options: typing.Optional[_AutoApproveOptions_dac86cbe] = None,
        auto_merge_options: typing.Optional[_AutoMergeOptions_d112cd3c] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[_GitHubOptions_21553699] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional[_MergifyOptions_a6faaab3] = None,
        project_type: typing.Optional[_ProjectType_fd80c725] = None,
        readme: typing.Optional[_SampleReadmeProps_3518b03b] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional[_StaleOptions_929db764] = None,
        vscode: typing.Optional[builtins.bool] = None,
        artifact_id: builtins.str,
        group_id: builtins.str,
        version: builtins.str,
        description: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        compile_options: typing.Optional[_MavenCompileOptions_c5c0ec48] = None,
        deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        distdir: typing.Optional[builtins.str] = None,
        junit: typing.Optional[builtins.bool] = None,
        junit_options: typing.Optional[_JunitOptions_e5b597b7] = None,
        packaging_options: typing.Optional[_MavenPackagingOptions_bc96fb36] = None,
        projenrc_java: typing.Optional[builtins.bool] = None,
        projenrc_java_options: typing.Optional[_ProjenrcOptions_65cd3dd8] = None,
        test_deps: typing.Optional[typing.Sequence[builtins.str]] = None,
        sample: typing.Optional[builtins.bool] = None,
        sample_java_package: typing.Optional[builtins.str] = None,
        cdkout: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        feature_flags: typing.Optional[builtins.bool] = None,
        require_approval: typing.Optional[ApprovalLevel] = None,
        cdk_version: builtins.str,
        main_class: builtins.str,
        cdk_dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param artifact_id: (experimental) The artifactId is generally the name that the project is known by. Although the groupId is important, people within the group will rarely mention the groupId in discussion (they are often all be the same ID, such as the MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId, creates a key that separates this project from every other project in the world (at least, it should :) ). Along with the groupId, the artifactId fully defines the artifact's living quarters within the repository. In the case of the above project, my-project lives in $M2_REPO/org/codehaus/mojo/my-project. Default: "my-app"
        :param group_id: (experimental) This is generally unique amongst an organization or a project. For example, all core Maven artifacts do (well, should) live under the groupId org.apache.maven. Group ID's do not necessarily use the dot notation, for example, the junit project. Note that the dot-notated groupId does not have to correspond to the package structure that the project contains. It is, however, a good practice to follow. When stored within a repository, the group acts much like the Java packaging structure does in an operating system. The dots are replaced by OS specific directory separators (such as '/' in Unix) which becomes a relative directory structure from the base repository. In the example given, the org.codehaus.mojo group lives within the directory $M2_REPO/org/codehaus/mojo. Default: "org.acme"
        :param version: (experimental) This is the last piece of the naming puzzle. groupId:artifactId denotes a single project but they cannot delineate which incarnation of that project we are talking about. Do we want the junit:junit of 2018 (version 4.12), or of 2007 (version 3.8.2)? In short: code changes, those changes should be versioned, and this element keeps those versions in line. It is also used within an artifact's repository to separate versions from each other. my-project version 1.0 files live in the directory structure $M2_REPO/org/codehaus/mojo/my-project/1.0. Default: "0.1.0"
        :param description: (experimental) Description of a project is always good. Although this should not replace formal documentation, a quick comment to any readers of the POM is always helpful. Default: undefined
        :param packaging: (experimental) Project packaging format. Default: "jar"
        :param url: (experimental) The URL, like the name, is not required. This is a nice gesture for projects users, however, so that they know where the project lives. Default: undefined
        :param compile_options: (experimental) Compile options. Default: - defaults
        :param deps: (experimental) List of runtime dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addDependency()``. Default: []
        :param distdir: (experimental) Final artifact output directory. Default: "dist/java"
        :param junit: (experimental) Include junit tests. Default: true
        :param junit_options: (experimental) junit options. Default: - defaults
        :param packaging_options: (experimental) Packaging options. Default: - defaults
        :param projenrc_java: (experimental) Use projenrc in java. This will install ``projen`` as a java dependency and will add a ``synth`` task which will compile & execute ``main()`` from ``src/main/java/projenrc.java``. Default: true
        :param projenrc_java_options: (experimental) Options related to projenrc in java. Default: - default options
        :param test_deps: (experimental) List of test dependencies for this project. Dependencies use the format: ``<groupId>/<artifactId>@<semver>`` Additional dependencies can be added via ``project.addTestDependency()``. Default: []
        :param sample: (experimental) Include sample code and test if the relevant directories don't exist.
        :param sample_java_package: (experimental) The java package to use for the code sample. Default: "org.acme"
        :param cdkout: (experimental) cdk.out directory. Default: "cdk.out"
        :param context: (experimental) Additional context to include in ``cdk.json``. Default: - no additional context
        :param feature_flags: (experimental) Include all feature flags in cdk.json. Default: true
        :param require_approval: (experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them. Default: ApprovalLevel.BROADENING
        :param cdk_version: (experimental) AWS CDK version to use (you can use semantic versioning). Default: "^1.130.0"
        :param main_class: (experimental) The name of the Java class with the static ``main()`` method. This method should call ``app.synth()`` on the CDK app. Default: "org.acme.App"
        :param cdk_dependencies: (experimental) Which AWS CDK modules this app uses. The ``core`` module is included by default and you can add additional modules here by stating only the package name (e.g. ``aws-lambda``).

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = _LoggerOptions_eb0f6309(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _ProjenrcOptions_985561af(**projenrc_json_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = _AutoApproveOptions_dac86cbe(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = _AutoMergeOptions_d112cd3c(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = _GitHubOptions_21553699(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = _MergifyOptions_a6faaab3(**mergify_options)
        if isinstance(readme, dict):
            readme = _SampleReadmeProps_3518b03b(**readme)
        if isinstance(stale_options, dict):
            stale_options = _StaleOptions_929db764(**stale_options)
        if isinstance(compile_options, dict):
            compile_options = _MavenCompileOptions_c5c0ec48(**compile_options)
        if isinstance(junit_options, dict):
            junit_options = _JunitOptions_e5b597b7(**junit_options)
        if isinstance(packaging_options, dict):
            packaging_options = _MavenPackagingOptions_bc96fb36(**packaging_options)
        if isinstance(projenrc_java_options, dict):
            projenrc_java_options = _ProjenrcOptions_65cd3dd8(**projenrc_java_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "artifact_id": artifact_id,
            "group_id": group_id,
            "version": version,
            "cdk_version": cdk_version,
            "main_class": main_class,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode
        if description is not None:
            self._values["description"] = description
        if packaging is not None:
            self._values["packaging"] = packaging
        if url is not None:
            self._values["url"] = url
        if compile_options is not None:
            self._values["compile_options"] = compile_options
        if deps is not None:
            self._values["deps"] = deps
        if distdir is not None:
            self._values["distdir"] = distdir
        if junit is not None:
            self._values["junit"] = junit
        if junit_options is not None:
            self._values["junit_options"] = junit_options
        if packaging_options is not None:
            self._values["packaging_options"] = packaging_options
        if projenrc_java is not None:
            self._values["projenrc_java"] = projenrc_java
        if projenrc_java_options is not None:
            self._values["projenrc_java_options"] = projenrc_java_options
        if test_deps is not None:
            self._values["test_deps"] = test_deps
        if sample is not None:
            self._values["sample"] = sample
        if sample_java_package is not None:
            self._values["sample_java_package"] = sample_java_package
        if cdkout is not None:
            self._values["cdkout"] = cdkout
        if context is not None:
            self._values["context"] = context
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if require_approval is not None:
            self._values["require_approval"] = require_approval
        if cdk_dependencies is not None:
            self._values["cdk_dependencies"] = cdk_dependencies

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[_LoggerOptions_eb0f6309]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_LoggerOptions_eb0f6309], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_Project_57d89203]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_Project_57d89203], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[_ProjenrcOptions_985561af]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_ProjenrcOptions_985561af], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[_AutoApproveOptions_dac86cbe]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[_AutoApproveOptions_dac86cbe], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[_AutoMergeOptions_d112cd3c]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[_AutoMergeOptions_d112cd3c], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[_GitHubOptions_21553699]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[_GitHubOptions_21553699], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional[_MergifyOptions_a6faaab3]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional[_MergifyOptions_a6faaab3], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_ProjectType_fd80c725]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_ProjectType_fd80c725], result)

    @builtins.property
    def readme(self) -> typing.Optional[_SampleReadmeProps_3518b03b]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[_SampleReadmeProps_3518b03b], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional[_StaleOptions_929db764]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional[_StaleOptions_929db764], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def artifact_id(self) -> builtins.str:
        '''(experimental) The artifactId is generally the name that the project is known by.

        Although
        the groupId is important, people within the group will rarely mention the
        groupId in discussion (they are often all be the same ID, such as the
        MojoHaus project groupId: org.codehaus.mojo). It, along with the groupId,
        creates a key that separates this project from every other project in the
        world (at least, it should :) ). Along with the groupId, the artifactId
        fully defines the artifact's living quarters within the repository. In the
        case of the above project, my-project lives in
        $M2_REPO/org/codehaus/mojo/my-project.

        :default: "my-app"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("artifact_id")
        assert result is not None, "Required property 'artifact_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_id(self) -> builtins.str:
        '''(experimental) This is generally unique amongst an organization or a project.

        For example,
        all core Maven artifacts do (well, should) live under the groupId
        org.apache.maven. Group ID's do not necessarily use the dot notation, for
        example, the junit project. Note that the dot-notated groupId does not have
        to correspond to the package structure that the project contains. It is,
        however, a good practice to follow. When stored within a repository, the
        group acts much like the Java packaging structure does in an operating
        system. The dots are replaced by OS specific directory separators (such as
        '/' in Unix) which becomes a relative directory structure from the base
        repository. In the example given, the org.codehaus.mojo group lives within
        the directory $M2_REPO/org/codehaus/mojo.

        :default: "org.acme"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("group_id")
        assert result is not None, "Required property 'group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) This is the last piece of the naming puzzle.

        groupId:artifactId denotes a
        single project but they cannot delineate which incarnation of that project
        we are talking about. Do we want the junit:junit of 2018 (version 4.12), or
        of 2007 (version 3.8.2)? In short: code changes, those changes should be
        versioned, and this element keeps those versions in line. It is also used
        within an artifact's repository to separate versions from each other.
        my-project version 1.0 files live in the directory structure
        $M2_REPO/org/codehaus/mojo/my-project/1.0.

        :default: "0.1.0"

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of a project is always good.

        Although this should not replace
        formal documentation, a quick comment to any readers of the POM is always
        helpful.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def packaging(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project packaging format.

        :default: "jar"

        :stability: experimental
        '''
        result = self._values.get("packaging")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The URL, like the name, is not required.

        This is a nice gesture for
        projects users, however, so that they know where the project lives.

        :default: undefined

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compile_options(self) -> typing.Optional[_MavenCompileOptions_c5c0ec48]:
        '''(experimental) Compile options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("compile_options")
        return typing.cast(typing.Optional[_MavenCompileOptions_c5c0ec48], result)

    @builtins.property
    def deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of runtime dependencies for this project.

        Dependencies use the format: ``<groupId>/<artifactId>@<semver>``

        Additional dependencies can be added via ``project.addDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def distdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Final artifact output directory.

        :default: "dist/java"

        :stability: experimental
        '''
        result = self._values.get("distdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def junit(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include junit tests.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("junit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def junit_options(self) -> typing.Optional[_JunitOptions_e5b597b7]:
        '''(experimental) junit options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("junit_options")
        return typing.cast(typing.Optional[_JunitOptions_e5b597b7], result)

    @builtins.property
    def packaging_options(self) -> typing.Optional[_MavenPackagingOptions_bc96fb36]:
        '''(experimental) Packaging options.

        :default: - defaults

        :stability: experimental
        '''
        result = self._values.get("packaging_options")
        return typing.cast(typing.Optional[_MavenPackagingOptions_bc96fb36], result)

    @builtins.property
    def projenrc_java(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use projenrc in java.

        This will install ``projen`` as a java dependency and will add a ``synth`` task which
        will compile & execute ``main()`` from ``src/main/java/projenrc.java``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("projenrc_java")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_java_options(self) -> typing.Optional[_ProjenrcOptions_65cd3dd8]:
        '''(experimental) Options related to projenrc in java.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_java_options")
        return typing.cast(typing.Optional[_ProjenrcOptions_65cd3dd8], result)

    @builtins.property
    def test_deps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of test dependencies for this project.

        Dependencies use the format: ``<groupId>/<artifactId>@<semver>``

        Additional dependencies can be added via ``project.addTestDependency()``.

        :default: []

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("test_deps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sample(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include sample code and test if the relevant directories don't exist.

        :stability: experimental
        '''
        result = self._values.get("sample")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sample_java_package(self) -> typing.Optional[builtins.str]:
        '''(experimental) The java package to use for the code sample.

        :default: "org.acme"

        :stability: experimental
        '''
        result = self._values.get("sample_java_package")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cdkout(self) -> typing.Optional[builtins.str]:
        '''(experimental) cdk.out directory.

        :default: "cdk.out"

        :stability: experimental
        '''
        result = self._values.get("cdkout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional context to include in ``cdk.json``.

        :default: - no additional context

        :stability: experimental
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Include all feature flags in cdk.json.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_approval(self) -> typing.Optional[ApprovalLevel]:
        '''(experimental) To protect you against unintended changes that affect your security posture, the AWS CDK Toolkit prompts you to approve security-related changes before deploying them.

        :default: ApprovalLevel.BROADENING

        :stability: experimental
        '''
        result = self._values.get("require_approval")
        return typing.cast(typing.Optional[ApprovalLevel], result)

    @builtins.property
    def cdk_version(self) -> builtins.str:
        '''(experimental) AWS CDK version to use (you can use semantic versioning).

        :default: "^1.130.0"

        :stability: experimental
        '''
        result = self._values.get("cdk_version")
        assert result is not None, "Required property 'cdk_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def main_class(self) -> builtins.str:
        '''(experimental) The name of the Java class with the static ``main()`` method.

        This method
        should call ``app.synth()`` on the CDK app.

        :default: "org.acme.App"

        :stability: experimental
        '''
        result = self._values.get("main_class")
        assert result is not None, "Required property 'main_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdk_dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Which AWS CDK modules this app uses.

        The ``core`` module is included by
        default and you can add additional modules here by stating only the package
        name (e.g. ``aws-lambda``).

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("cdk_dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsCdkJavaAppOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApprovalLevel",
    "AutoDiscover",
    "AutoDiscoverOptions",
    "AwsCdkJavaApp",
    "AwsCdkJavaAppOptions",
    "CdkConfig",
    "CdkConfigCommonOptions",
    "CdkConfigOptions",
    "CdkTasks",
    "LambdaFunction",
    "LambdaFunctionCommonOptions",
    "LambdaFunctionOptions",
    "LambdaRuntime",
]

publication.publish()
