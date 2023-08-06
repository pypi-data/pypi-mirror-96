'''
# cdk8s+ (cdk8s-plus)

### High level constructs for Kubernetes

<br>

![Beta](https://img.shields.io/badge/beta-informational.svg?style=for-the-badge)

**cdk8s+** is a software development framework that provides high level abstractions for authoring Kubernetes applications.
Built on top of the auto generated building blocks provided by [cdk8s](../cdk8s), this library includes a hand crafted *construct*
for each native kubernetes object, exposing richer API's with reduced complexity.

## Documentation

See [cdk8s.io](https://cdk8s.io/docs/latest/plus).

## License

This project is distributed under the [Apache License, Version 2.0](./LICENSE).

This module is part of the [cdk8s project](https://github.com/awslabs/cdk8s).
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import cdk8s
import constructs


@jsii.data_type(
    jsii_type="cdk8s-plus-17.AddDirectoryOptions",
    jsii_struct_bases=[],
    name_mapping={"exclude": "exclude", "key_prefix": "keyPrefix"},
)
class AddDirectoryOptions:
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.List[builtins.str]] = None,
        key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for ``configmap.addDirectory()``.

        :param exclude: (experimental) Glob patterns to exclude when adding files. Default: - include all files
        :param key_prefix: (experimental) A prefix to add to all keys in the config map. Default: ""

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude is not None:
            self._values["exclude"] = exclude
        if key_prefix is not None:
            self._values["key_prefix"] = key_prefix

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Glob patterns to exclude when adding files.

        :default: - include all files

        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix to add to all keys in the config map.

        :default: ""

        :stability: experimental
        '''
        result = self._values.get("key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddDirectoryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ConfigMapVolumeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "default_mode": "defaultMode",
        "items": "items",
        "name": "name",
        "optional": "optional",
    },
)
class ConfigMapVolumeOptions:
    def __init__(
        self,
        *,
        default_mode: typing.Optional[jsii.Number] = None,
        items: typing.Optional[typing.Mapping[builtins.str, "PathMapping"]] = None,
        name: typing.Optional[builtins.str] = None,
        optional: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for the ConfigMap-based volume.

        :param default_mode: (experimental) Mode bits to use on created files by default. Must be a value between 0 and 0777. Defaults to 0644. Directories within the path are not affected by this setting. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set. Default: 644. Directories within the path are not affected by this setting. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set.
        :param items: (experimental) If unspecified, each key-value pair in the Data field of the referenced ConfigMap will be projected into the volume as a file whose name is the key and content is the value. If specified, the listed keys will be projected into the specified paths, and unlisted keys will not be present. If a key is specified which is not present in the ConfigMap, the volume setup will error unless it is marked optional. Paths must be relative and may not contain the '..' path or start with '..'. Default: - no mapping
        :param name: (experimental) The volume name. Default: - auto-generated
        :param optional: (experimental) Specify whether the ConfigMap or its keys must be defined. Default: - undocumented

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if default_mode is not None:
            self._values["default_mode"] = default_mode
        if items is not None:
            self._values["items"] = items
        if name is not None:
            self._values["name"] = name
        if optional is not None:
            self._values["optional"] = optional

    @builtins.property
    def default_mode(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Mode bits to use on created files by default.

        Must be a value between 0 and
        0777. Defaults to 0644. Directories within the path are not affected by
        this setting. This might be in conflict with other options that affect the
        file mode, like fsGroup, and the result can be other mode bits set.

        :default:

        644. Directories within the path are not affected by this
        setting. This might be in conflict with other options that affect the file
        mode, like fsGroup, and the result can be other mode bits set.

        :stability: experimental
        '''
        result = self._values.get("default_mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def items(self) -> typing.Optional[typing.Mapping[builtins.str, "PathMapping"]]:
        '''(experimental) If unspecified, each key-value pair in the Data field of the referenced ConfigMap will be projected into the volume as a file whose name is the key and content is the value.

        If specified, the listed keys will be projected
        into the specified paths, and unlisted keys will not be present. If a key
        is specified which is not present in the ConfigMap, the volume setup will
        error unless it is marked optional. Paths must be relative and may not
        contain the '..' path or start with '..'.

        :default: - no mapping

        :stability: experimental
        '''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "PathMapping"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The volume name.

        :default: - auto-generated

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def optional(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specify whether the ConfigMap or its keys must be defined.

        :default: - undocumented

        :stability: experimental
        '''
        result = self._values.get("optional")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigMapVolumeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Container(metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.Container"):
    '''(experimental) A single application container that you want to run within a pod.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, "EnvValue"]] = None,
        image_pull_policy: typing.Optional["ImagePullPolicy"] = None,
        liveness: typing.Optional["Probe"] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional["Probe"] = None,
        startup: typing.Optional["Probe"] = None,
        volume_mounts: typing.Optional[typing.List["VolumeMount"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        props = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        jsii.create(Container, self, [props])

    @jsii.member(jsii_name="addEnv")
    def add_env(self, name: builtins.str, value: "EnvValue") -> None:
        '''(experimental) Add an environment value to the container.

        The variable value can come
        from various dynamic sources such a secrets of config maps.

        :param name: - The variable name.
        :param value: - The variable value.

        :see: EnvValue.fromXXX
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addEnv", [name, value]))

    @jsii.member(jsii_name="mount")
    def mount(
        self,
        path: builtins.str,
        volume: "Volume",
        *,
        propagation: typing.Optional["MountPropagation"] = None,
        read_only: typing.Optional[builtins.bool] = None,
        sub_path: typing.Optional[builtins.str] = None,
        sub_path_expr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Mount a volume to a specific path so that it is accessible by the container.

        Every pod that is configured to use this container will autmoatically have access to the volume.

        :param path: - The desired path in the container.
        :param volume: - The volume to mount.
        :param propagation: (experimental) Determines how mounts are propagated from the host to container and the other way around. When not set, MountPropagationNone is used. Mount propagation allows for sharing volumes mounted by a Container to other Containers in the same Pod, or even to other Pods on the same node. This field is beta in 1.10. Default: MountPropagation.NONE
        :param read_only: (experimental) Mounted read-only if true, read-write otherwise (false or unspecified). Defaults to false. Default: false
        :param sub_path: (experimental) Path within the volume from which the container's volume should be mounted.). Default: "" the volume's root
        :param sub_path_expr: (experimental) Expanded path within the volume from which the container's volume should be mounted. Behaves similarly to SubPath but environment variable references $(VAR_NAME) are expanded using the container's environment. Defaults to "" (volume's root). SubPathExpr and SubPath are mutually exclusive. This field is beta in 1.15. ``subPathExpr`` and ``subPath`` are mutually exclusive. This field is beta in 1.15. Default: "" volume's root.

        :stability: experimental
        '''
        options = MountOptions(
            propagation=propagation,
            read_only=read_only,
            sub_path=sub_path,
            sub_path_expr=sub_path_expr,
        )

        return typing.cast(None, jsii.invoke(self, "mount", [path, volume, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.Mapping[builtins.str, "EnvValue"]:
        '''(experimental) The environment variables for this container.

        Returns a copy. To add environment variables use ``addEnv()``.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "EnvValue"], jsii.get(self, "env"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        '''(experimental) The container image.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imagePullPolicy")
    def image_pull_policy(self) -> "ImagePullPolicy":
        '''(experimental) Image pull policy for this container.

        :stability: experimental
        '''
        return typing.cast("ImagePullPolicy", jsii.get(self, "imagePullPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mounts")
    def mounts(self) -> typing.List["VolumeMount"]:
        '''(experimental) Volume mounts configured for this container.

        :stability: experimental
        '''
        return typing.cast(typing.List["VolumeMount"], jsii.get(self, "mounts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the container.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="args")
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Arguments to the entrypoint.

        :return: a copy of the arguments array, cannot be modified.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "args"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Entrypoint array (the command to execute when the container starts).

        :return: a copy of the entrypoint array, cannot be modified

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "command"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port this container exposes.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDir")
    def working_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The working directory inside the container.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDir"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ContainerProps",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "args": "args",
        "command": "command",
        "env": "env",
        "image_pull_policy": "imagePullPolicy",
        "liveness": "liveness",
        "name": "name",
        "port": "port",
        "readiness": "readiness",
        "startup": "startup",
        "volume_mounts": "volumeMounts",
        "working_dir": "workingDir",
    },
)
class ContainerProps:
    def __init__(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, "EnvValue"]] = None,
        image_pull_policy: typing.Optional["ImagePullPolicy"] = None,
        liveness: typing.Optional["Probe"] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional["Probe"] = None,
        startup: typing.Optional["Probe"] = None,
        volume_mounts: typing.Optional[typing.List["VolumeMount"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for creating a container.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if args is not None:
            self._values["args"] = args
        if command is not None:
            self._values["command"] = command
        if env is not None:
            self._values["env"] = env
        if image_pull_policy is not None:
            self._values["image_pull_policy"] = image_pull_policy
        if liveness is not None:
            self._values["liveness"] = liveness
        if name is not None:
            self._values["name"] = name
        if port is not None:
            self._values["port"] = port
        if readiness is not None:
            self._values["readiness"] = readiness
        if startup is not None:
            self._values["startup"] = startup
        if volume_mounts is not None:
            self._values["volume_mounts"] = volume_mounts
        if working_dir is not None:
            self._values["working_dir"] = working_dir

    @builtins.property
    def image(self) -> builtins.str:
        '''(experimental) Docker image name.

        :stability: experimental
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided.

        Variable references $(VAR_NAME) are expanded using the container's
        environment. If a variable cannot be resolved, the reference in the input
        string will be unchanged. The $(VAR_NAME) syntax can be escaped with a
        double $$, ie: $$(VAR_NAME). Escaped references will never be expanded,
        regardless of whether the variable exists or not.

        Cannot be updated.

        :default: []

        :see: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell
        :stability: experimental
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Entrypoint array.

        Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment.
        If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME).
        Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated.
        More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell

        :default: - The docker image's ENTRYPOINT.

        :stability: experimental
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, "EnvValue"]]:
        '''(experimental) List of environment variables to set in the container.

        Cannot be updated.

        :default: - No environment variables.

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "EnvValue"]], result)

    @builtins.property
    def image_pull_policy(self) -> typing.Optional["ImagePullPolicy"]:
        '''(experimental) Image pull policy for this container.

        :default: ImagePullPolicy.ALWAYS

        :stability: experimental
        '''
        result = self._values.get("image_pull_policy")
        return typing.cast(typing.Optional["ImagePullPolicy"], result)

    @builtins.property
    def liveness(self) -> typing.Optional["Probe"]:
        '''(experimental) Periodic probe of container liveness.

        Container will be restarted if the probe fails.

        :default: - no liveness probe is defined

        :stability: experimental
        '''
        result = self._values.get("liveness")
        return typing.cast(typing.Optional["Probe"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the container specified as a DNS_LABEL.

        Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated.

        :default: 'main'

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of port to expose on the pod's IP address.

        This must be a valid port number, 0 < x < 65536.

        :default: - No port is exposed.

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def readiness(self) -> typing.Optional["Probe"]:
        '''(experimental) Determines when the container is ready to serve traffic.

        :default: - no readiness probe is defined

        :stability: experimental
        '''
        result = self._values.get("readiness")
        return typing.cast(typing.Optional["Probe"], result)

    @builtins.property
    def startup(self) -> typing.Optional["Probe"]:
        '''(experimental) StartupProbe indicates that the Pod has successfully initialized.

        If specified, no other probes are executed until this completes successfully

        :default: - no startup probe is defined.

        :stability: experimental
        '''
        result = self._values.get("startup")
        return typing.cast(typing.Optional["Probe"], result)

    @builtins.property
    def volume_mounts(self) -> typing.Optional[typing.List["VolumeMount"]]:
        '''(experimental) Pod volumes to mount into the container's filesystem.

        Cannot be updated.

        :stability: experimental
        '''
        result = self._values.get("volume_mounts")
        return typing.cast(typing.Optional[typing.List["VolumeMount"]], result)

    @builtins.property
    def working_dir(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container's working directory.

        If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated.

        :default: - The container runtime's default.

        :stability: experimental
        '''
        result = self._values.get("working_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-plus-17.EmptyDirMedium")
class EmptyDirMedium(enum.Enum):
    '''(experimental) The medium on which to store the volume.

    :stability: experimental
    '''

    DEFAULT = "DEFAULT"
    '''(experimental) The default volume of the backing node.

    :stability: experimental
    '''
    MEMORY = "MEMORY"
    '''(experimental) Mount a tmpfs (RAM-backed filesystem) for you instead.

    While tmpfs is very
    fast, be aware that unlike disks, tmpfs is cleared on node reboot and any
    files you write will count against your Container's memory limit.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk8s-plus-17.EmptyDirVolumeOptions",
    jsii_struct_bases=[],
    name_mapping={"medium": "medium", "size_limit": "sizeLimit"},
)
class EmptyDirVolumeOptions:
    def __init__(
        self,
        *,
        medium: typing.Optional[EmptyDirMedium] = None,
        size_limit: typing.Optional[cdk8s.Size] = None,
    ) -> None:
        '''(experimental) Options for volumes populated with an empty directory.

        :param medium: (experimental) By default, emptyDir volumes are stored on whatever medium is backing the node - that might be disk or SSD or network storage, depending on your environment. However, you can set the emptyDir.medium field to ``EmptyDirMedium.MEMORY`` to tell Kubernetes to mount a tmpfs (RAM-backed filesystem) for you instead. While tmpfs is very fast, be aware that unlike disks, tmpfs is cleared on node reboot and any files you write will count against your Container's memory limit. Default: EmptyDirMedium.DEFAULT
        :param size_limit: (experimental) Total amount of local storage required for this EmptyDir volume. The size limit is also applicable for memory medium. The maximum usage on memory medium EmptyDir would be the minimum value between the SizeLimit specified here and the sum of memory limits of all containers in a pod. Default: - limit is undefined

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if medium is not None:
            self._values["medium"] = medium
        if size_limit is not None:
            self._values["size_limit"] = size_limit

    @builtins.property
    def medium(self) -> typing.Optional[EmptyDirMedium]:
        '''(experimental) By default, emptyDir volumes are stored on whatever medium is backing the node - that might be disk or SSD or network storage, depending on your environment.

        However, you can set the emptyDir.medium field to
        ``EmptyDirMedium.MEMORY`` to tell Kubernetes to mount a tmpfs (RAM-backed
        filesystem) for you instead. While tmpfs is very fast, be aware that unlike
        disks, tmpfs is cleared on node reboot and any files you write will count
        against your Container's memory limit.

        :default: EmptyDirMedium.DEFAULT

        :stability: experimental
        '''
        result = self._values.get("medium")
        return typing.cast(typing.Optional[EmptyDirMedium], result)

    @builtins.property
    def size_limit(self) -> typing.Optional[cdk8s.Size]:
        '''(experimental) Total amount of local storage required for this EmptyDir volume.

        The size
        limit is also applicable for memory medium. The maximum usage on memory
        medium EmptyDir would be the minimum value between the SizeLimit specified
        here and the sum of memory limits of all containers in a pod.

        :default: - limit is undefined

        :stability: experimental
        '''
        result = self._values.get("size_limit")
        return typing.cast(typing.Optional[cdk8s.Size], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmptyDirVolumeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnvValue(metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.EnvValue"):
    '''(experimental) Utility class for creating reading env values from various sources.

    :stability: experimental
    '''

    @jsii.member(jsii_name="fromConfigMap") # type: ignore[misc]
    @builtins.classmethod
    def from_config_map(
        cls,
        config_map: "IConfigMap",
        key: builtins.str,
        *,
        optional: typing.Optional[builtins.bool] = None,
    ) -> "EnvValue":
        '''(experimental) Create a value by reading a specific key inside a config map.

        :param config_map: - The config map.
        :param key: - The key to extract the value from.
        :param optional: (experimental) Specify whether the ConfigMap or its key must be defined. Default: false

        :stability: experimental
        '''
        options = EnvValueFromConfigMapOptions(optional=optional)

        return typing.cast("EnvValue", jsii.sinvoke(cls, "fromConfigMap", [config_map, key, options]))

    @jsii.member(jsii_name="fromProcess") # type: ignore[misc]
    @builtins.classmethod
    def from_process(
        cls,
        key: builtins.str,
        *,
        required: typing.Optional[builtins.bool] = None,
    ) -> "EnvValue":
        '''(experimental) Create a value from a key in the current process environment.

        :param key: - The key to read.
        :param required: (experimental) Specify whether the key must exist in the environment. If this is set to true, and the key does not exist, an error will thrown. Default: false

        :stability: experimental
        '''
        options = EnvValueFromProcessOptions(required=required)

        return typing.cast("EnvValue", jsii.sinvoke(cls, "fromProcess", [key, options]))

    @jsii.member(jsii_name="fromSecretValue") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_value(
        cls,
        secret_value: "SecretValue",
        *,
        optional: typing.Optional[builtins.bool] = None,
    ) -> "EnvValue":
        '''(experimental) Defines an environment value from a secret JSON value.

        :param secret_value: The secret value (secrent + key).
        :param optional: (experimental) Specify whether the Secret or its key must be defined. Default: false

        :stability: experimental
        '''
        options = EnvValueFromSecretOptions(optional=optional)

        return typing.cast("EnvValue", jsii.sinvoke(cls, "fromSecretValue", [secret_value, options]))

    @jsii.member(jsii_name="fromValue") # type: ignore[misc]
    @builtins.classmethod
    def from_value(cls, value: builtins.str) -> "EnvValue":
        '''(experimental) Create a value from the given argument.

        :param value: - The value.

        :stability: experimental
        '''
        return typing.cast("EnvValue", jsii.sinvoke(cls, "fromValue", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Any:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.get(self, "value"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="valueFrom")
    def value_from(self) -> typing.Any:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.get(self, "valueFrom"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.EnvValueFromConfigMapOptions",
    jsii_struct_bases=[],
    name_mapping={"optional": "optional"},
)
class EnvValueFromConfigMapOptions:
    def __init__(self, *, optional: typing.Optional[builtins.bool] = None) -> None:
        '''(experimental) Options to specify an envionment variable value from a ConfigMap key.

        :param optional: (experimental) Specify whether the ConfigMap or its key must be defined. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if optional is not None:
            self._values["optional"] = optional

    @builtins.property
    def optional(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specify whether the ConfigMap or its key must be defined.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("optional")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvValueFromConfigMapOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.EnvValueFromProcessOptions",
    jsii_struct_bases=[],
    name_mapping={"required": "required"},
)
class EnvValueFromProcessOptions:
    def __init__(self, *, required: typing.Optional[builtins.bool] = None) -> None:
        '''(experimental) Options to specify an environment variable value from the process environment.

        :param required: (experimental) Specify whether the key must exist in the environment. If this is set to true, and the key does not exist, an error will thrown. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def required(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specify whether the key must exist in the environment.

        If this is set to true, and the key does not exist, an error will thrown.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvValueFromProcessOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.EnvValueFromSecretOptions",
    jsii_struct_bases=[],
    name_mapping={"optional": "optional"},
)
class EnvValueFromSecretOptions:
    def __init__(self, *, optional: typing.Optional[builtins.bool] = None) -> None:
        '''(experimental) Options to specify an environment variable value from a Secret.

        :param optional: (experimental) Specify whether the Secret or its key must be defined. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if optional is not None:
            self._values["optional"] = optional

    @builtins.property
    def optional(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specify whether the Secret or its key must be defined.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("optional")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvValueFromSecretOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ExposeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "protocol": "protocol",
        "service_type": "serviceType",
        "target_port": "targetPort",
    },
)
class ExposeOptions:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional["Protocol"] = None,
        service_type: typing.Optional["ServiceType"] = None,
        target_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Options for exposing a deployment via a service.

        :param name: (experimental) The name of the service to expose. This will be set on the Service.metadata and must be a DNS_LABEL Default: undefined Uses the system generated name.
        :param protocol: (experimental) The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP. Default: Protocol.TCP
        :param service_type: (experimental) The type of the exposed service. Default: - ClusterIP.
        :param target_port: (experimental) The port number the service will redirect to. Default: - The port of the first container in the deployment (ie. containers[0].port)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if protocol is not None:
            self._values["protocol"] = protocol
        if service_type is not None:
            self._values["service_type"] = service_type
        if target_port is not None:
            self._values["target_port"] = target_port

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the service to expose.

        This will be set on the Service.metadata and must be a DNS_LABEL

        :default: undefined Uses the system generated name.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional["Protocol"]:
        '''(experimental) The IP protocol for this port.

        Supports "TCP", "UDP", and "SCTP". Default is TCP.

        :default: Protocol.TCP

        :stability: experimental
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional["Protocol"], result)

    @builtins.property
    def service_type(self) -> typing.Optional["ServiceType"]:
        '''(experimental) The type of the exposed service.

        :default: - ClusterIP.

        :stability: experimental
        '''
        result = self._values.get("service_type")
        return typing.cast(typing.Optional["ServiceType"], result)

    @builtins.property
    def target_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port number the service will redirect to.

        :default: - The port of the first container in the deployment (ie. containers[0].port)

        :stability: experimental
        '''
        result = self._values.get("target_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExposeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk8s-plus-17.IPodSpec")
class IPodSpec(typing_extensions.Protocol):
    '''(experimental) Represents a resource that can be configured with a kuberenets pod spec. (e.g ``Deployment``, ``Job``, ``Pod``, ...).

    Use the ``PodSpec`` class as an implementation helper.

    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_IPodSpecProxy"]:
        return _IPodSpecProxy

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List["Volume"]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional["RestartPolicy"]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional["IServiceAccount"]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional["ImagePullPolicy"] = None,
        liveness: typing.Optional["Probe"] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional["Probe"] = None,
        startup: typing.Optional["Probe"] = None,
        volume_mounts: typing.Optional[typing.List["VolumeMount"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: "Volume") -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: The volume.

        :stability: experimental
        '''
        ...


class _IPodSpecProxy:
    '''(experimental) Represents a resource that can be configured with a kuberenets pod spec. (e.g ``Deployment``, ``Job``, ``Pod``, ...).

    Use the ``PodSpec`` class as an implementation helper.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-plus-17.IPodSpec"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        return typing.cast(typing.List[Container], jsii.get(self, "containers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List["Volume"]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        return typing.cast(typing.List["Volume"], jsii.get(self, "volumes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional["RestartPolicy"]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["RestartPolicy"], jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional["IServiceAccount"]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["IServiceAccount"], jsii.get(self, "serviceAccount"))

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional["ImagePullPolicy"] = None,
        liveness: typing.Optional["Probe"] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional["Probe"] = None,
        startup: typing.Optional["Probe"] = None,
        volume_mounts: typing.Optional[typing.List["VolumeMount"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        container = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        return typing.cast(Container, jsii.invoke(self, "addContainer", [container]))

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: "Volume") -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: The volume.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVolume", [volume]))


@jsii.interface(jsii_type="cdk8s-plus-17.IPodTemplate")
class IPodTemplate(IPodSpec, typing_extensions.Protocol):
    '''(experimental) Represents a resource that can be configured with a kuberenets pod template. (e.g ``Deployment``, ``Job``, ...).

    Use the ``PodTemplate`` class as an implementation helper.

    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_IPodTemplateProxy"]:
        return _IPodTemplateProxy

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podMetadata")
    def pod_metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''(experimental) Provides read/write access to the underlying pod metadata of the resource.

        :stability: experimental
        '''
        ...


class _IPodTemplateProxy(
    jsii.proxy_for(IPodSpec) # type: ignore[misc]
):
    '''(experimental) Represents a resource that can be configured with a kuberenets pod template. (e.g ``Deployment``, ``Job``, ...).

    Use the ``PodTemplate`` class as an implementation helper.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-plus-17.IPodTemplate"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podMetadata")
    def pod_metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''(experimental) Provides read/write access to the underlying pod metadata of the resource.

        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObjectMetadataDefinition, jsii.get(self, "podMetadata"))


@jsii.interface(jsii_type="cdk8s-plus-17.IResource")
class IResource(typing_extensions.Protocol):
    '''(experimental) Represents a resource.

    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_IResourceProxy"]:
        return _IResourceProxy

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The Kubernetes name of this resource.

        :stability: experimental
        '''
        ...


class _IResourceProxy:
    '''(experimental) Represents a resource.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-plus-17.IResource"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The Kubernetes name of this resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.interface(jsii_type="cdk8s-plus-17.ISecret")
class ISecret(IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_ISecretProxy"]:
        return _ISecretProxy


class _ISecretProxy(
    jsii.proxy_for(IResource) # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-plus-17.ISecret"
    pass


@jsii.interface(jsii_type="cdk8s-plus-17.IServiceAccount")
class IServiceAccount(IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_IServiceAccountProxy"]:
        return _IServiceAccountProxy


class _IServiceAccountProxy(
    jsii.proxy_for(IResource) # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-plus-17.IServiceAccount"
    pass


@jsii.enum(jsii_type="cdk8s-plus-17.ImagePullPolicy")
class ImagePullPolicy(enum.Enum):
    '''
    :stability: experimental
    '''

    ALWAYS = "ALWAYS"
    '''(experimental) Every time the kubelet launches a container, the kubelet queries the container image registry to resolve the name to an image digest.

    If the kubelet has a container image with that exact
    digest cached locally, the kubelet uses its cached image; otherwise, the kubelet downloads
    (pulls) the image with the resolved digest, and uses that image to launch the container.

    Default is Always if ImagePullPolicy is omitted and either the image tag is :latest or
    the image tag is omitted.

    :stability: experimental
    '''
    IF_NOT_PRESENT = "IF_NOT_PRESENT"
    '''(experimental) The image is pulled only if it is not already present locally.

    Default is IfNotPresent if ImagePullPolicy is omitted and the image tag is present but
    not :latest

    :stability: experimental
    '''
    NEVER = "NEVER"
    '''(experimental) The image is assumed to exist locally.

    No attempt is made to pull the image.

    :stability: experimental
    '''


class IngressV1Beta1Backend(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-plus-17.IngressV1Beta1Backend",
):
    '''(experimental) The backend for an ingress path.

    :stability: experimental
    '''

    @jsii.member(jsii_name="fromService") # type: ignore[misc]
    @builtins.classmethod
    def from_service(
        cls,
        service: "Service",
        *,
        port: typing.Optional[jsii.Number] = None,
    ) -> "IngressV1Beta1Backend":
        '''(experimental) A Kubernetes ``Service`` to use as the backend for this path.

        :param service: The service object.
        :param port: (experimental) The port to use to access the service. - This option will fail if the service does not expose any ports. - If the service exposes multiple ports, this option must be specified. - If the service exposes a single port, this option is optional and if specified, it must be the same port exposed by the service. Default: - if the service exposes a single port, this port will be used.

        :stability: experimental
        '''
        options = ServiceIngressV1BetaBackendOptions(port=port)

        return typing.cast("IngressV1Beta1Backend", jsii.sinvoke(cls, "fromService", [service, options]))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.IngressV1Beta1Rule",
    jsii_struct_bases=[],
    name_mapping={"backend": "backend", "host": "host", "path": "path"},
)
class IngressV1Beta1Rule:
    def __init__(
        self,
        *,
        backend: IngressV1Beta1Backend,
        host: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Represents the rules mapping the paths under a specified host to the related backend services.

        Incoming requests are first evaluated for a host match,
        then routed to the backend associated with the matching path.

        :param backend: (experimental) Backend defines the referenced service endpoint to which the traffic will be forwarded to.
        :param host: (experimental) Host is the fully qualified domain name of a network host, as defined by RFC 3986. Note the following deviations from the "host" part of the URI as defined in the RFC: 1. IPs are not allowed. Currently an IngressRuleValue can only apply to the IP in the Spec of the parent Ingress. 2. The ``:`` delimiter is not respected because ports are not allowed. Currently the port of an Ingress is implicitly :80 for http and :443 for https. Both these may change in the future. Incoming requests are matched against the host before the IngressRuleValue. Default: - If the host is unspecified, the Ingress routes all traffic based on the specified IngressRuleValue.
        :param path: (experimental) Path is an extended POSIX regex as defined by IEEE Std 1003.1, (i.e this follows the egrep/unix syntax, not the perl syntax) matched against the path of an incoming request. Currently it can contain characters disallowed from the conventional "path" part of a URL as defined by RFC 3986. Paths must begin with a '/'. Default: - If unspecified, the path defaults to a catch all sending traffic to the backend.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "backend": backend,
        }
        if host is not None:
            self._values["host"] = host
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def backend(self) -> IngressV1Beta1Backend:
        '''(experimental) Backend defines the referenced service endpoint to which the traffic will be forwarded to.

        :stability: experimental
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(IngressV1Beta1Backend, result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''(experimental) Host is the fully qualified domain name of a network host, as defined by RFC 3986.

        Note the following deviations from the "host" part of the URI as
        defined in the RFC: 1. IPs are not allowed. Currently an IngressRuleValue
        can only apply to the IP in the Spec of the parent Ingress. 2. The ``:``
        delimiter is not respected because ports are not allowed. Currently the
        port of an Ingress is implicitly :80 for http and :443 for https. Both
        these may change in the future. Incoming requests are matched against the
        host before the IngressRuleValue.

        :default:

        - If the host is unspecified, the Ingress routes all traffic based
        on the specified IngressRuleValue.

        :stability: experimental
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path is an extended POSIX regex as defined by IEEE Std 1003.1, (i.e this follows the egrep/unix syntax, not the perl syntax) matched against the path of an incoming request. Currently it can contain characters disallowed from the conventional "path" part of a URL as defined by RFC 3986. Paths must begin with a '/'.

        :default:

        - If unspecified, the path defaults to a catch all sending traffic
        to the backend.

        :stability: experimental
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressV1Beta1Rule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.MountOptions",
    jsii_struct_bases=[],
    name_mapping={
        "propagation": "propagation",
        "read_only": "readOnly",
        "sub_path": "subPath",
        "sub_path_expr": "subPathExpr",
    },
)
class MountOptions:
    def __init__(
        self,
        *,
        propagation: typing.Optional["MountPropagation"] = None,
        read_only: typing.Optional[builtins.bool] = None,
        sub_path: typing.Optional[builtins.str] = None,
        sub_path_expr: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for mounts.

        :param propagation: (experimental) Determines how mounts are propagated from the host to container and the other way around. When not set, MountPropagationNone is used. Mount propagation allows for sharing volumes mounted by a Container to other Containers in the same Pod, or even to other Pods on the same node. This field is beta in 1.10. Default: MountPropagation.NONE
        :param read_only: (experimental) Mounted read-only if true, read-write otherwise (false or unspecified). Defaults to false. Default: false
        :param sub_path: (experimental) Path within the volume from which the container's volume should be mounted.). Default: "" the volume's root
        :param sub_path_expr: (experimental) Expanded path within the volume from which the container's volume should be mounted. Behaves similarly to SubPath but environment variable references $(VAR_NAME) are expanded using the container's environment. Defaults to "" (volume's root). SubPathExpr and SubPath are mutually exclusive. This field is beta in 1.15. ``subPathExpr`` and ``subPath`` are mutually exclusive. This field is beta in 1.15. Default: "" volume's root.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if propagation is not None:
            self._values["propagation"] = propagation
        if read_only is not None:
            self._values["read_only"] = read_only
        if sub_path is not None:
            self._values["sub_path"] = sub_path
        if sub_path_expr is not None:
            self._values["sub_path_expr"] = sub_path_expr

    @builtins.property
    def propagation(self) -> typing.Optional["MountPropagation"]:
        '''(experimental) Determines how mounts are propagated from the host to container and the other way around.

        When not set, MountPropagationNone is used.

        Mount propagation allows for sharing volumes mounted by a Container to
        other Containers in the same Pod, or even to other Pods on the same node.

        This field is beta in 1.10.

        :default: MountPropagation.NONE

        :stability: experimental
        '''
        result = self._values.get("propagation")
        return typing.cast(typing.Optional["MountPropagation"], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Mounted read-only if true, read-write otherwise (false or unspecified).

        Defaults to false.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sub_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path within the volume from which the container's volume should be mounted.).

        :default: "" the volume's root

        :stability: experimental
        '''
        result = self._values.get("sub_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sub_path_expr(self) -> typing.Optional[builtins.str]:
        '''(experimental) Expanded path within the volume from which the container's volume should be mounted.

        Behaves similarly to SubPath but environment variable references
        $(VAR_NAME) are expanded using the container's environment. Defaults to ""
        (volume's root). SubPathExpr and SubPath are mutually exclusive. This field
        is beta in 1.15.

        ``subPathExpr`` and ``subPath`` are mutually exclusive. This field is beta in
        1.15.

        :default: "" volume's root.

        :stability: experimental
        '''
        result = self._values.get("sub_path_expr")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-plus-17.MountPropagation")
class MountPropagation(enum.Enum):
    '''
    :stability: experimental
    '''

    NONE = "NONE"
    '''(experimental) This volume mount will not receive any subsequent mounts that are mounted to this volume or any of its subdirectories by the host.

    In similar
    fashion, no mounts created by the Container will be visible on the host.

    This is the default mode.

    This mode is equal to ``private`` mount propagation as described in the Linux
    kernel documentation

    :stability: experimental
    '''
    HOST_TO_CONTAINER = "HOST_TO_CONTAINER"
    '''(experimental) This volume mount will receive all subsequent mounts that are mounted to this volume or any of its subdirectories.

    In other words, if the host mounts anything inside the volume mount, the
    Container will see it mounted there.

    Similarly, if any Pod with Bidirectional mount propagation to the same
    volume mounts anything there, the Container with HostToContainer mount
    propagation will see it.

    This mode is equal to ``rslave`` mount propagation as described in the Linux
    kernel documentation

    :stability: experimental
    '''
    BIDIRECTIONAL = "BIDIRECTIONAL"
    '''(experimental) This volume mount behaves the same the HostToContainer mount.

    In addition,
    all volume mounts created by the Container will be propagated back to the
    host and to all Containers of all Pods that use the same volume

    A typical use case for this mode is a Pod with a FlexVolume or CSI driver
    or a Pod that needs to mount something on the host using a hostPath volume.

    This mode is equal to ``rshared`` mount propagation as described in the Linux
    kernel documentation

    Caution: Bidirectional mount propagation can be dangerous. It can damage
    the host operating system and therefore it is allowed only in privileged
    Containers. Familiarity with Linux kernel behavior is strongly recommended.
    In addition, any volume mounts created by Containers in Pods must be
    destroyed (unmounted) by the Containers on termination.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk8s-plus-17.PathMapping",
    jsii_struct_bases=[],
    name_mapping={"path": "path", "mode": "mode"},
)
class PathMapping:
    def __init__(
        self,
        *,
        path: builtins.str,
        mode: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Maps a string key to a path within a volume.

        :param path: (experimental) The relative path of the file to map the key to. May not be an absolute path. May not contain the path element '..'. May not start with the string '..'.
        :param mode: (experimental) Optional: mode bits to use on this file, must be a value between 0 and 0777. If not specified, the volume defaultMode will be used. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
        }
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) The relative path of the file to map the key to.

        May not be an absolute
        path. May not contain the path element '..'. May not start with the string
        '..'.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mode(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Optional: mode bits to use on this file, must be a value between 0 and 0777.

        If not specified, the volume defaultMode will be used. This might be
        in conflict with other options that affect the file mode, like fsGroup, and
        the result can be other mode bits set.

        :stability: experimental
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PathMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-plus-17.PodManagementPolicy")
class PodManagementPolicy(enum.Enum):
    '''(experimental) Controls how pods are created during initial scale up, when replacing pods on nodes, or when scaling down.

    The default policy is ``OrderedReady``, where pods are created in increasing order
    (pod-0, then pod-1, etc) and the controller will wait until each pod is ready before
    continuing. When scaling down, the pods are removed in the opposite order.

    The alternative policy is ``Parallel`` which will create pods in parallel to match the
    desired scale without waiting, and on scale down will delete all pods at once.

    :stability: experimental
    '''

    ORDERED_READY = "ORDERED_READY"
    '''
    :stability: experimental
    '''
    PARALLEL = "PARALLEL"
    '''
    :stability: experimental
    '''


@jsii.implements(IPodSpec)
class PodSpec(metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.PodSpec"):
    '''(experimental) Provides read/write capabilities ontop of a ``PodSpecProps``.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional["RestartPolicy"] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List["Volume"]] = None,
    ) -> None:
        '''
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        props = PodSpecProps(
            containers=containers,
            restart_policy=restart_policy,
            service_account=service_account,
            volumes=volumes,
        )

        jsii.create(PodSpec, self, [props])

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional[ImagePullPolicy] = None,
        liveness: typing.Optional["Probe"] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional["Probe"] = None,
        startup: typing.Optional["Probe"] = None,
        volume_mounts: typing.Optional[typing.List["VolumeMount"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        container = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        return typing.cast(Container, jsii.invoke(self, "addContainer", [container]))

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: "Volume") -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVolume", [volume]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        return typing.cast(typing.List[Container], jsii.get(self, "containers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List["Volume"]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        return typing.cast(typing.List["Volume"], jsii.get(self, "volumes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional["RestartPolicy"]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["RestartPolicy"], jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IServiceAccount], jsii.get(self, "serviceAccount"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.PodSpecProps",
    jsii_struct_bases=[],
    name_mapping={
        "containers": "containers",
        "restart_policy": "restartPolicy",
        "service_account": "serviceAccount",
        "volumes": "volumes",
    },
)
class PodSpecProps:
    def __init__(
        self,
        *,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional["RestartPolicy"] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List["Volume"]] = None,
    ) -> None:
        '''(experimental) Properties of a ``PodSpec``.

        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if containers is not None:
            self._values["containers"] = containers
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def containers(self) -> typing.Optional[typing.List[ContainerProps]]:
        '''(experimental) List of containers belonging to the pod.

        Containers cannot currently be
        added or removed. There must be at least one container in a Pod.

        You can add additionnal containers using ``podSpec.addContainer()``

        :default: - No containers. Note that a pod spec must include at least one container.

        :stability: experimental
        '''
        result = self._values.get("containers")
        return typing.cast(typing.Optional[typing.List[ContainerProps]], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional["RestartPolicy"]:
        '''(experimental) Restart policy for all containers within the pod.

        :default: RestartPolicy.ALWAYS

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy
        :stability: experimental
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional["RestartPolicy"], result)

    @builtins.property
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) A service account provides an identity for processes that run in a Pod.

        When you (a human) access the cluster (for example, using kubectl), you are
        authenticated by the apiserver as a particular User Account (currently this
        is usually admin, unless your cluster administrator has customized your
        cluster). Processes in containers inside pods can also contact the
        apiserver. When they do, they are authenticated as a particular Service
        Account (for example, default).

        :default: - No service account.

        :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[IServiceAccount], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List["Volume"]]:
        '''(experimental) List of volumes that can be mounted by containers belonging to the pod.

        You can also add volumes later using ``podSpec.addVolume()``

        :default: - No volumes.

        :see: https://kubernetes.io/docs/concepts/storage/volumes
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List["Volume"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PodSpecProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPodTemplate)
class PodTemplate(
    PodSpec,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-plus-17.PodTemplate",
):
    '''(experimental) Provides read/write capabilities ontop of a ``PodTemplateProps``.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional["RestartPolicy"] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List["Volume"]] = None,
    ) -> None:
        '''
        :param pod_metadata: (experimental) The pod metadata.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        props = PodTemplateProps(
            pod_metadata=pod_metadata,
            containers=containers,
            restart_policy=restart_policy,
            service_account=service_account,
            volumes=volumes,
        )

        jsii.create(PodTemplate, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podMetadata")
    def pod_metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''(experimental) Provides read/write access to the underlying pod metadata of the resource.

        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObjectMetadataDefinition, jsii.get(self, "podMetadata"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.PodTemplateProps",
    jsii_struct_bases=[PodSpecProps],
    name_mapping={
        "containers": "containers",
        "restart_policy": "restartPolicy",
        "service_account": "serviceAccount",
        "volumes": "volumes",
        "pod_metadata": "podMetadata",
    },
)
class PodTemplateProps(PodSpecProps):
    def __init__(
        self,
        *,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional["RestartPolicy"] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List["Volume"]] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''(experimental) Properties of a ``PodTemplate``.

        Adds metadata information on top of the spec.

        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.
        :param pod_metadata: (experimental) The pod metadata.

        :stability: experimental
        '''
        if isinstance(pod_metadata, dict):
            pod_metadata = cdk8s.ApiObjectMetadata(**pod_metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if containers is not None:
            self._values["containers"] = containers
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if volumes is not None:
            self._values["volumes"] = volumes
        if pod_metadata is not None:
            self._values["pod_metadata"] = pod_metadata

    @builtins.property
    def containers(self) -> typing.Optional[typing.List[ContainerProps]]:
        '''(experimental) List of containers belonging to the pod.

        Containers cannot currently be
        added or removed. There must be at least one container in a Pod.

        You can add additionnal containers using ``podSpec.addContainer()``

        :default: - No containers. Note that a pod spec must include at least one container.

        :stability: experimental
        '''
        result = self._values.get("containers")
        return typing.cast(typing.Optional[typing.List[ContainerProps]], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional["RestartPolicy"]:
        '''(experimental) Restart policy for all containers within the pod.

        :default: RestartPolicy.ALWAYS

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy
        :stability: experimental
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional["RestartPolicy"], result)

    @builtins.property
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) A service account provides an identity for processes that run in a Pod.

        When you (a human) access the cluster (for example, using kubectl), you are
        authenticated by the apiserver as a particular User Account (currently this
        is usually admin, unless your cluster administrator has customized your
        cluster). Processes in containers inside pods can also contact the
        apiserver. When they do, they are authenticated as a particular Service
        Account (for example, default).

        :default: - No service account.

        :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[IServiceAccount], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List["Volume"]]:
        '''(experimental) List of volumes that can be mounted by containers belonging to the pod.

        You can also add volumes later using ``podSpec.addVolume()``

        :default: - No volumes.

        :see: https://kubernetes.io/docs/concepts/storage/volumes
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List["Volume"]], result)

    @builtins.property
    def pod_metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) The pod metadata.

        :stability: experimental
        '''
        result = self._values.get("pod_metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PodTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Probe(metaclass=jsii.JSIIAbstractClass, jsii_type="cdk8s-plus-17.Probe"):
    '''(experimental) Probe describes a health check to be performed against a container to determine whether it is alive or ready to receive traffic.

    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_ProbeProxy"]:
        return _ProbeProxy

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(Probe, self, [])

    @jsii.member(jsii_name="fromCommand") # type: ignore[misc]
    @builtins.classmethod
    def from_command(
        cls,
        command: typing.List[builtins.str],
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
        initial_delay_seconds: typing.Optional[cdk8s.Duration] = None,
        period_seconds: typing.Optional[cdk8s.Duration] = None,
        success_threshold: typing.Optional[jsii.Number] = None,
        timeout_seconds: typing.Optional[cdk8s.Duration] = None,
    ) -> "Probe":
        '''(experimental) Defines a probe based on a command which is executed within the container.

        :param command: The command to execute.
        :param failure_threshold: (experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded. Defaults to 3. Minimum value is 1. Default: 3
        :param initial_delay_seconds: (experimental) Number of seconds after the container has started before liveness probes are initiated. Default: - immediate
        :param period_seconds: (experimental) How often (in seconds) to perform the probe. Default to 10 seconds. Minimum value is 1. Default: Duration.seconds(10) Minimum value is 1.
        :param success_threshold: (experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1. Must be 1 for liveness and startup. Minimum value is 1. Default: 1 Must be 1 for liveness and startup. Minimum value is 1.
        :param timeout_seconds: (experimental) Number of seconds after which the probe times out. Defaults to 1 second. Minimum value is 1. Default: Duration.seconds(1)

        :stability: experimental
        '''
        options = CommandProbeOptions(
            failure_threshold=failure_threshold,
            initial_delay_seconds=initial_delay_seconds,
            period_seconds=period_seconds,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
        )

        return typing.cast("Probe", jsii.sinvoke(cls, "fromCommand", [command, options]))

    @jsii.member(jsii_name="fromHttpGet") # type: ignore[misc]
    @builtins.classmethod
    def from_http_get(
        cls,
        path: builtins.str,
        *,
        port: typing.Optional[jsii.Number] = None,
        failure_threshold: typing.Optional[jsii.Number] = None,
        initial_delay_seconds: typing.Optional[cdk8s.Duration] = None,
        period_seconds: typing.Optional[cdk8s.Duration] = None,
        success_threshold: typing.Optional[jsii.Number] = None,
        timeout_seconds: typing.Optional[cdk8s.Duration] = None,
    ) -> "Probe":
        '''(experimental) Defines a probe based on an HTTP GET request to the IP address of the container.

        :param path: The URL path to hit.
        :param port: (experimental) The TCP port to use when sending the GET request. Default: - defaults to ``container.port``.
        :param failure_threshold: (experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded. Defaults to 3. Minimum value is 1. Default: 3
        :param initial_delay_seconds: (experimental) Number of seconds after the container has started before liveness probes are initiated. Default: - immediate
        :param period_seconds: (experimental) How often (in seconds) to perform the probe. Default to 10 seconds. Minimum value is 1. Default: Duration.seconds(10) Minimum value is 1.
        :param success_threshold: (experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1. Must be 1 for liveness and startup. Minimum value is 1. Default: 1 Must be 1 for liveness and startup. Minimum value is 1.
        :param timeout_seconds: (experimental) Number of seconds after which the probe times out. Defaults to 1 second. Minimum value is 1. Default: Duration.seconds(1)

        :stability: experimental
        '''
        options = HttpGetProbeOptions(
            port=port,
            failure_threshold=failure_threshold,
            initial_delay_seconds=initial_delay_seconds,
            period_seconds=period_seconds,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
        )

        return typing.cast("Probe", jsii.sinvoke(cls, "fromHttpGet", [path, options]))


class _ProbeProxy(Probe):
    pass


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ProbeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "failure_threshold": "failureThreshold",
        "initial_delay_seconds": "initialDelaySeconds",
        "period_seconds": "periodSeconds",
        "success_threshold": "successThreshold",
        "timeout_seconds": "timeoutSeconds",
    },
)
class ProbeOptions:
    def __init__(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
        initial_delay_seconds: typing.Optional[cdk8s.Duration] = None,
        period_seconds: typing.Optional[cdk8s.Duration] = None,
        success_threshold: typing.Optional[jsii.Number] = None,
        timeout_seconds: typing.Optional[cdk8s.Duration] = None,
    ) -> None:
        '''(experimental) Probe options.

        :param failure_threshold: (experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded. Defaults to 3. Minimum value is 1. Default: 3
        :param initial_delay_seconds: (experimental) Number of seconds after the container has started before liveness probes are initiated. Default: - immediate
        :param period_seconds: (experimental) How often (in seconds) to perform the probe. Default to 10 seconds. Minimum value is 1. Default: Duration.seconds(10) Minimum value is 1.
        :param success_threshold: (experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1. Must be 1 for liveness and startup. Minimum value is 1. Default: 1 Must be 1 for liveness and startup. Minimum value is 1.
        :param timeout_seconds: (experimental) Number of seconds after which the probe times out. Defaults to 1 second. Minimum value is 1. Default: Duration.seconds(1)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if failure_threshold is not None:
            self._values["failure_threshold"] = failure_threshold
        if initial_delay_seconds is not None:
            self._values["initial_delay_seconds"] = initial_delay_seconds
        if period_seconds is not None:
            self._values["period_seconds"] = period_seconds
        if success_threshold is not None:
            self._values["success_threshold"] = success_threshold
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds

    @builtins.property
    def failure_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded.

        Defaults to 3. Minimum value is 1.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def initial_delay_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Number of seconds after the container has started before liveness probes are initiated.

        :default: - immediate

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#container-probes
        :stability: experimental
        '''
        result = self._values.get("initial_delay_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def period_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) How often (in seconds) to perform the probe.

        Default to 10 seconds. Minimum value is 1.

        :default: Duration.seconds(10) Minimum value is 1.

        :stability: experimental
        '''
        result = self._values.get("period_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def success_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1.

        Must be 1 for liveness and startup. Minimum value is 1.

        :default: 1 Must be 1 for liveness and startup. Minimum value is 1.

        :stability: experimental
        '''
        result = self._values.get("success_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Number of seconds after which the probe times out.

        Defaults to 1 second. Minimum value is 1.

        :default: Duration.seconds(1)

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#container-probes
        :stability: experimental
        '''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProbeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-plus-17.Protocol")
class Protocol(enum.Enum):
    '''
    :stability: experimental
    '''

    TCP = "TCP"
    '''
    :stability: experimental
    '''
    UDP = "UDP"
    '''
    :stability: experimental
    '''
    SCTP = "SCTP"
    '''
    :stability: experimental
    '''


@jsii.implements(IResource)
class Resource(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk8s-plus-17.Resource",
):
    '''(experimental) Base class for all Kubernetes objects in stdk8s.

    Represents a single
    resource.

    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_ResourceProxy"]:
        return _ResourceProxy

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        node_factory: typing.Optional[constructs.INodeFactory] = None,
    ) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        :param node_factory: A factory for attaching ``Node``s to the construct. Default: - the default ``Node`` is associated
        '''
        options = constructs.ConstructOptions(node_factory=node_factory)

        jsii.create(Resource, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    @abc.abstractmethod
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObjectMetadataDefinition, jsii.get(self, "metadata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of this API object.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))


class _ResourceProxy(Resource):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ResourceProps",
    jsii_struct_bases=[],
    name_mapping={"metadata": "metadata"},
)
class ResourceProps:
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''(experimental) Initialization properties for resources.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-plus-17.RestartPolicy")
class RestartPolicy(enum.Enum):
    '''(experimental) Restart policy for all containers within the pod.

    :stability: experimental
    '''

    ALWAYS = "ALWAYS"
    '''(experimental) Always restart the pod after it exits.

    :stability: experimental
    '''
    ON_FAILURE = "ON_FAILURE"
    '''(experimental) Only restart if the pod exits with a non-zero exit code.

    :stability: experimental
    '''
    NEVER = "NEVER"
    '''(experimental) Never restart the pod.

    :stability: experimental
    '''


@jsii.implements(ISecret)
class Secret(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.Secret"):
    '''(experimental) Kubernetes Secrets let you store and manage sensitive information, such as passwords, OAuth tokens, and ssh keys.

    Storing confidential information in a
    Secret is safer and more flexible than putting it verbatim in a Pod
    definition or in a container image.

    :see: https://kubernetes.io/docs/concepts/configuration/secret
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        string_data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param string_data: (experimental) stringData allows specifying non-binary secret data in string form. It is provided as a write-only convenience method. All keys and values are merged into the data field on write, overwriting any existing values. It is never output when reading from the API.
        :param type: (experimental) Optional type associated with the secret. Used to facilitate programmatic handling of secret data by various controllers. Default: undefined - Don't set a type.
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        props = SecretProps(string_data=string_data, type=type, metadata=metadata)

        jsii.create(Secret, self, [scope, id, props])

    @jsii.member(jsii_name="fromSecretName") # type: ignore[misc]
    @builtins.classmethod
    def from_secret_name(cls, name: builtins.str) -> ISecret:
        '''(experimental) Imports a secret from the cluster as a reference.

        :param name: The name of the secret to reference.

        :stability: experimental
        '''
        return typing.cast(ISecret, jsii.sinvoke(cls, "fromSecretName", [name]))

    @jsii.member(jsii_name="addStringData")
    def add_string_data(self, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Adds a string data field to the secert.

        :param key: Key.
        :param value: Value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addStringData", [key, value]))

    @jsii.member(jsii_name="getStringData")
    def get_string_data(self, key: builtins.str) -> typing.Optional[builtins.str]:
        '''(experimental) Gets a string data by key or undefined.

        :param key: Key.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "getStringData", [key]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.SecretProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={"metadata": "metadata", "string_data": "stringData", "type": "type"},
)
class SecretProps(ResourceProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        string_data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param string_data: (experimental) stringData allows specifying non-binary secret data in string form. It is provided as a write-only convenience method. All keys and values are merged into the data field on write, overwriting any existing values. It is never output when reading from the API.
        :param type: (experimental) Optional type associated with the secret. Used to facilitate programmatic handling of secret data by various controllers. Default: undefined - Don't set a type.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if string_data is not None:
            self._values["string_data"] = string_data
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def string_data(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) stringData allows specifying non-binary secret data in string form.

        It is
        provided as a write-only convenience method. All keys and values are merged
        into the data field on write, overwriting any existing values. It is never
        output when reading from the API.

        :stability: experimental
        '''
        result = self._values.get("string_data")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional type associated with the secret.

        Used to facilitate programmatic
        handling of secret data by various controllers.

        :default: undefined - Don't set a type.

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.SecretValue",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "secret": "secret"},
)
class SecretValue:
    def __init__(self, *, key: builtins.str, secret: ISecret) -> None:
        '''(experimental) Represents a specific value in JSON secret.

        :param key: (experimental) The JSON key.
        :param secret: (experimental) The secret.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "secret": secret,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''(experimental) The JSON key.

        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret(self) -> ISecret:
        '''(experimental) The secret.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Service(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.Service"):
    '''(experimental) An abstract way to expose an application running on a set of Pods as a network service.

    With Kubernetes you don't need to modify your application to use an unfamiliar service discovery mechanism.
    Kubernetes gives Pods their own IP addresses and a single DNS name for a set of Pods, and can load-balance across them.

    For example, consider a stateless image-processing backend which is running with 3 replicas. Those replicas are fungible—frontends do not care which backend they use.
    While the actual Pods that compose the backend set may change, the frontend clients should not need to be aware of that,
    nor should they need to keep track of the set of backends themselves.
    The Service abstraction enables this decoupling.

    If you're able to use Kubernetes APIs for service discovery in your application, you can query the API server for Endpoints,
    that get updated whenever the set of Pods in a Service changes. For non-native applications, Kubernetes offers ways to place a network port
    or load balancer in between your application and the backend Pods.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_ip: typing.Optional[builtins.str] = None,
        external_i_ps: typing.Optional[typing.List[builtins.str]] = None,
        external_name: typing.Optional[builtins.str] = None,
        load_balancer_source_ranges: typing.Optional[typing.List[builtins.str]] = None,
        ports: typing.Optional[typing.List["ServicePort"]] = None,
        type: typing.Optional["ServiceType"] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_ip: (experimental) The IP address of the service and is usually assigned randomly by the master. If an address is specified manually and is not in use by others, it will be allocated to the service; otherwise, creation of the service will fail. This field can not be changed through updates. Valid values are "None", empty string (""), or a valid IP address. "None" can be specified for headless services when proxying is not required. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. Default: - Automatically assigned.
        :param external_i_ps: (experimental) A list of IP addresses for which nodes in the cluster will also accept traffic for this service. These IPs are not managed by Kubernetes. The user is responsible for ensuring that traffic arrives at a node with this IP. A common example is external load-balancers that are not part of the Kubernetes system. Default: - No external IPs.
        :param external_name: (experimental) The externalName to be used when ServiceType.EXTERNAL_NAME is set. Default: - No external name.
        :param load_balancer_source_ranges: (experimental) A list of CIDR IP addresses, if specified and supported by the platform, will restrict traffic through the cloud-provider load-balancer to the specified client IPs. More info: https://kubernetes.io/docs/tasks/access-application-cluster/configure-cloud-provider-firewall/
        :param ports: (experimental) The port exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies
        :param type: (experimental) Determines how the Service is exposed. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types Default: ServiceType.ClusterIP
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        props = ServiceProps(
            cluster_ip=cluster_ip,
            external_i_ps=external_i_ps,
            external_name=external_name,
            load_balancer_source_ranges=load_balancer_source_ranges,
            ports=ports,
            type=type,
            metadata=metadata,
        )

        jsii.create(Service, self, [scope, id, props])

    @jsii.member(jsii_name="addDeployment")
    def add_deployment(
        self,
        deployment: "Deployment",
        port: jsii.Number,
        *,
        name: typing.Optional[builtins.str] = None,
        node_port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[Protocol] = None,
        target_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Associate a deployment to this service.

        If not targetPort is specific in the portOptions, then requests will be routed
        to the port exposed by the first container in the deployment's pods.
        The deployment's ``labelSelector`` will be used to select pods.

        :param deployment: The deployment to expose.
        :param port: The external port.
        :param name: (experimental) The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. This maps to the 'Name' field in EndpointPort objects. Optional if only one ServicePort is defined on this service.
        :param node_port: (experimental) The port on each node on which this service is exposed when type=NodePort or LoadBalancer. Usually assigned by the system. If specified, it will be allocated to the service if unused or else creation of the service will fail. Default is to auto-allocate a port if the ServiceType of this Service requires one. Default: to auto-allocate a port if the ServiceType of this Service requires one.
        :param protocol: (experimental) The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP. Default: Protocol.TCP
        :param target_port: (experimental) The port number the service will redirect to. Default: - The value of ``port`` will be used.

        :stability: experimental
        '''
        options = ServicePortOptions(
            name=name, node_port=node_port, protocol=protocol, target_port=target_port
        )

        return typing.cast(None, jsii.invoke(self, "addDeployment", [deployment, port, options]))

    @jsii.member(jsii_name="addSelector")
    def add_selector(self, label: builtins.str, value: builtins.str) -> None:
        '''(experimental) Services defined using this spec will select pods according the provided label.

        :param label: The label key.
        :param value: The label value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addSelector", [label, value]))

    @jsii.member(jsii_name="serve")
    def serve(
        self,
        port: jsii.Number,
        *,
        name: typing.Optional[builtins.str] = None,
        node_port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[Protocol] = None,
        target_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Configure a port the service will bind to.

        This method can be called multiple times.

        :param port: The port definition.
        :param name: (experimental) The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. This maps to the 'Name' field in EndpointPort objects. Optional if only one ServicePort is defined on this service.
        :param node_port: (experimental) The port on each node on which this service is exposed when type=NodePort or LoadBalancer. Usually assigned by the system. If specified, it will be allocated to the service if unused or else creation of the service will fail. Default is to auto-allocate a port if the ServiceType of this Service requires one. Default: to auto-allocate a port if the ServiceType of this Service requires one.
        :param protocol: (experimental) The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP. Default: Protocol.TCP
        :param target_port: (experimental) The port number the service will redirect to. Default: - The value of ``port`` will be used.

        :stability: experimental
        '''
        options = ServicePortOptions(
            name=name, node_port=node_port, protocol=protocol, target_port=target_port
        )

        return typing.cast(None, jsii.invoke(self, "serve", [port, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List["ServicePort"]:
        '''(experimental) Ports for this service.

        Use ``serve()`` to expose additional service ports.

        :stability: experimental
        '''
        return typing.cast(typing.List["ServicePort"], jsii.get(self, "ports"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="selector")
    def selector(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Returns the labels which are used to select pods for this service.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "selector"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> "ServiceType":
        '''(experimental) Determines how the Service is exposed.

        :stability: experimental
        '''
        return typing.cast("ServiceType", jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIP")
    def cluster_ip(self) -> typing.Optional[builtins.str]:
        '''(experimental) The IP address of the service and is usually assigned randomly by the master.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIP"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalName")
    def external_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The externalName to be used for EXTERNAL_NAME types.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalName"))


@jsii.implements(IServiceAccount)
class ServiceAccount(
    Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-plus-17.ServiceAccount",
):
    '''(experimental) A service account provides an identity for processes that run in a Pod.

    When you (a human) access the cluster (for example, using kubectl), you are
    authenticated by the apiserver as a particular User Account (currently this
    is usually admin, unless your cluster administrator has customized your
    cluster). Processes in containers inside pods can also contact the apiserver.
    When they do, they are authenticated as a particular Service Account (for
    example, default).

    :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secrets: typing.Optional[typing.List[ISecret]] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secrets: (experimental) List of secrets allowed to be used by pods running using this ServiceAccount.
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        props = ServiceAccountProps(secrets=secrets, metadata=metadata)

        jsii.create(ServiceAccount, self, [scope, id, props])

    @jsii.member(jsii_name="fromServiceAccountName") # type: ignore[misc]
    @builtins.classmethod
    def from_service_account_name(cls, name: builtins.str) -> IServiceAccount:
        '''(experimental) Imports a service account from the cluster as a reference.

        :param name: The name of the service account resource.

        :stability: experimental
        '''
        return typing.cast(IServiceAccount, jsii.sinvoke(cls, "fromServiceAccountName", [name]))

    @jsii.member(jsii_name="addSecret")
    def add_secret(self, secret: ISecret) -> None:
        '''(experimental) Allow a secret to be accessed by pods using this service account.

        :param secret: The secret.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addSecret", [secret]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secrets")
    def secrets(self) -> typing.List[ISecret]:
        '''(experimental) List of secrets allowed to be used by pods running using this service account.

        Returns a copy. To add a secret, use ``addSecret()``.

        :stability: experimental
        '''
        return typing.cast(typing.List[ISecret], jsii.get(self, "secrets"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ServiceAccountProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={"metadata": "metadata", "secrets": "secrets"},
)
class ServiceAccountProps(ResourceProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        secrets: typing.Optional[typing.List[ISecret]] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``ServiceAccount``.

        Properties for initialization of ``ServiceAccount``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param secrets: (experimental) List of secrets allowed to be used by pods running using this ServiceAccount.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if secrets is not None:
            self._values["secrets"] = secrets

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def secrets(self) -> typing.Optional[typing.List[ISecret]]:
        '''(experimental) List of secrets allowed to be used by pods running using this ServiceAccount.

        :see: https://kubernetes.io/docs/concepts/configuration/secret
        :stability: experimental
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.List[ISecret]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ServiceIngressV1BetaBackendOptions",
    jsii_struct_bases=[],
    name_mapping={"port": "port"},
)
class ServiceIngressV1BetaBackendOptions:
    def __init__(self, *, port: typing.Optional[jsii.Number] = None) -> None:
        '''(experimental) Options for setting up backends for ingress rules.

        :param port: (experimental) The port to use to access the service. - This option will fail if the service does not expose any ports. - If the service exposes multiple ports, this option must be specified. - If the service exposes a single port, this option is optional and if specified, it must be the same port exposed by the service. Default: - if the service exposes a single port, this port will be used.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port to use to access the service.

        - This option will fail if the service does not expose any ports.
        - If the service exposes multiple ports, this option must be specified.
        - If the service exposes a single port, this option is optional and if
          specified, it must be the same port exposed by the service.

        :default: - if the service exposes a single port, this port will be used.

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceIngressV1BetaBackendOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ServicePortOptions",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "node_port": "nodePort",
        "protocol": "protocol",
        "target_port": "targetPort",
    },
)
class ServicePortOptions:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        node_port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[Protocol] = None,
        target_port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: (experimental) The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. This maps to the 'Name' field in EndpointPort objects. Optional if only one ServicePort is defined on this service.
        :param node_port: (experimental) The port on each node on which this service is exposed when type=NodePort or LoadBalancer. Usually assigned by the system. If specified, it will be allocated to the service if unused or else creation of the service will fail. Default is to auto-allocate a port if the ServiceType of this Service requires one. Default: to auto-allocate a port if the ServiceType of this Service requires one.
        :param protocol: (experimental) The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP. Default: Protocol.TCP
        :param target_port: (experimental) The port number the service will redirect to. Default: - The value of ``port`` will be used.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if node_port is not None:
            self._values["node_port"] = node_port
        if protocol is not None:
            self._values["protocol"] = protocol
        if target_port is not None:
            self._values["target_port"] = target_port

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of this port within the service.

        This must be a DNS_LABEL. All
        ports within a ServiceSpec must have unique names. This maps to the 'Name'
        field in EndpointPort objects. Optional if only one ServicePort is defined
        on this service.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port on each node on which this service is exposed when type=NodePort or LoadBalancer.

        Usually assigned by the system. If specified, it will be
        allocated to the service if unused or else creation of the service will
        fail. Default is to auto-allocate a port if the ServiceType of this Service
        requires one.

        :default:

        to auto-allocate a port if the ServiceType of this Service
        requires one.

        :see: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport
        :stability: experimental
        '''
        result = self._values.get("node_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol(self) -> typing.Optional[Protocol]:
        '''(experimental) The IP protocol for this port.

        Supports "TCP", "UDP", and "SCTP". Default is TCP.

        :default: Protocol.TCP

        :stability: experimental
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[Protocol], result)

    @builtins.property
    def target_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port number the service will redirect to.

        :default: - The value of ``port`` will be used.

        :stability: experimental
        '''
        result = self._values.get("target_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServicePortOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ServiceProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={
        "metadata": "metadata",
        "cluster_ip": "clusterIP",
        "external_i_ps": "externalIPs",
        "external_name": "externalName",
        "load_balancer_source_ranges": "loadBalancerSourceRanges",
        "ports": "ports",
        "type": "type",
    },
)
class ServiceProps(ResourceProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        cluster_ip: typing.Optional[builtins.str] = None,
        external_i_ps: typing.Optional[typing.List[builtins.str]] = None,
        external_name: typing.Optional[builtins.str] = None,
        load_balancer_source_ranges: typing.Optional[typing.List[builtins.str]] = None,
        ports: typing.Optional[typing.List["ServicePort"]] = None,
        type: typing.Optional["ServiceType"] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``Service``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param cluster_ip: (experimental) The IP address of the service and is usually assigned randomly by the master. If an address is specified manually and is not in use by others, it will be allocated to the service; otherwise, creation of the service will fail. This field can not be changed through updates. Valid values are "None", empty string (""), or a valid IP address. "None" can be specified for headless services when proxying is not required. Only applies to types ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName. Default: - Automatically assigned.
        :param external_i_ps: (experimental) A list of IP addresses for which nodes in the cluster will also accept traffic for this service. These IPs are not managed by Kubernetes. The user is responsible for ensuring that traffic arrives at a node with this IP. A common example is external load-balancers that are not part of the Kubernetes system. Default: - No external IPs.
        :param external_name: (experimental) The externalName to be used when ServiceType.EXTERNAL_NAME is set. Default: - No external name.
        :param load_balancer_source_ranges: (experimental) A list of CIDR IP addresses, if specified and supported by the platform, will restrict traffic through the cloud-provider load-balancer to the specified client IPs. More info: https://kubernetes.io/docs/tasks/access-application-cluster/configure-cloud-provider-firewall/
        :param ports: (experimental) The port exposed by this service. More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies
        :param type: (experimental) Determines how the Service is exposed. More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types Default: ServiceType.ClusterIP

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if cluster_ip is not None:
            self._values["cluster_ip"] = cluster_ip
        if external_i_ps is not None:
            self._values["external_i_ps"] = external_i_ps
        if external_name is not None:
            self._values["external_name"] = external_name
        if load_balancer_source_ranges is not None:
            self._values["load_balancer_source_ranges"] = load_balancer_source_ranges
        if ports is not None:
            self._values["ports"] = ports
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def cluster_ip(self) -> typing.Optional[builtins.str]:
        '''(experimental) The IP address of the service and is usually assigned randomly by the master.

        If an address is specified manually and is not in use by others, it
        will be allocated to the service; otherwise, creation of the service will
        fail. This field can not be changed through updates. Valid values are
        "None", empty string (""), or a valid IP address. "None" can be specified
        for headless services when proxying is not required. Only applies to types
        ClusterIP, NodePort, and LoadBalancer. Ignored if type is ExternalName.

        :default: - Automatically assigned.

        :see: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies
        :stability: experimental
        '''
        result = self._values.get("cluster_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_i_ps(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of IP addresses for which nodes in the cluster will also accept traffic for this service.

        These IPs are not managed by Kubernetes. The user
        is responsible for ensuring that traffic arrives at a node with this IP. A
        common example is external load-balancers that are not part of the
        Kubernetes system.

        :default: - No external IPs.

        :stability: experimental
        '''
        result = self._values.get("external_i_ps")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def external_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The externalName to be used when ServiceType.EXTERNAL_NAME is set.

        :default: - No external name.

        :stability: experimental
        '''
        result = self._values.get("external_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancer_source_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of CIDR IP addresses, if specified and supported by the platform, will restrict traffic through the cloud-provider load-balancer to the specified client IPs.

        More info: https://kubernetes.io/docs/tasks/access-application-cluster/configure-cloud-provider-firewall/

        :stability: experimental
        '''
        result = self._values.get("load_balancer_source_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List["ServicePort"]]:
        '''(experimental) The port exposed by this service.

        More info: https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies

        :stability: experimental
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List["ServicePort"]], result)

    @builtins.property
    def type(self) -> typing.Optional["ServiceType"]:
        '''(experimental) Determines how the Service is exposed.

        More info: https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types

        :default: ServiceType.ClusterIP

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["ServiceType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s-plus-17.ServiceType")
class ServiceType(enum.Enum):
    '''(experimental) For some parts of your application (for example, frontends) you may want to expose a Service onto an external IP address, that's outside of your cluster.

    Kubernetes ServiceTypes allow you to specify what kind of Service you want.
    The default is ClusterIP.

    :stability: experimental
    '''

    CLUSTER_IP = "CLUSTER_IP"
    '''(experimental) Exposes the Service on a cluster-internal IP.

    Choosing this value makes the Service only reachable from within the cluster.
    This is the default ServiceType

    :stability: experimental
    '''
    NODE_PORT = "NODE_PORT"
    '''(experimental) Exposes the Service on each Node's IP at a static port (the NodePort).

    A ClusterIP Service, to which the NodePort Service routes, is automatically created.
    You'll be able to contact the NodePort Service, from outside the cluster,
    by requesting :.

    :stability: experimental
    '''
    LOAD_BALANCER = "LOAD_BALANCER"
    '''(experimental) Exposes the Service externally using a cloud provider's load balancer.

    NodePort and ClusterIP Services, to which the external load balancer routes,
    are automatically created.

    :stability: experimental
    '''
    EXTERNAL_NAME = "EXTERNAL_NAME"
    '''(experimental) Maps the Service to the contents of the externalName field (e.g. foo.bar.example.com), by returning a CNAME record with its value. No proxying of any kind is set up.

    .. epigraph::

       Note: You need either kube-dns version 1.7 or CoreDNS version 0.0.8 or higher to use the ExternalName type.

    :stability: experimental
    '''


@jsii.implements(IPodTemplate)
class StatefulSet(
    Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-plus-17.StatefulSet",
):
    '''(experimental) StatefulSet is the workload API object used to manage stateful applications.

    Manages the deployment and scaling of a set of Pods, and provides guarantees
    about the ordering and uniqueness of these Pods.

    Like a Deployment, a StatefulSet manages Pods that are based on an identical
    container spec. Unlike a Deployment, a StatefulSet maintains a sticky identity
    for each of their Pods. These pods are created from the same spec, but are not
    interchangeable: each has a persistent identifier that it maintains across any
    rescheduling.

    If you want to use storage volumes to provide persistence for your workload, you
    can use a StatefulSet as part of the solution. Although individual Pods in a StatefulSet
    are susceptible to failure, the persistent Pod identifiers make it easier to match existing
    volumes to the new Pods that replace any that have failed.


    Using StatefulSets

    StatefulSets are valuable for applications that require one or more of the following.

    - Stable, unique network identifiers.
    - Stable, persistent storage.
    - Ordered, graceful deployment and scaling.
    - Ordered, automated rolling updates.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        service: Service,
        default_selector: typing.Optional[builtins.bool] = None,
        pod_management_policy: typing.Optional[PodManagementPolicy] = None,
        replicas: typing.Optional[jsii.Number] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List["Volume"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param service: (experimental) Service to associate with the statefulset.
        :param default_selector: (experimental) Automatically allocates a pod selector for this statefulset. If this is set to ``false`` you must define your selector through ``statefulset.podMetadata.addLabel()`` and ``statefulset.selectByLabel()``. Default: true
        :param pod_management_policy: (experimental) Pod management policy to use for this statefulset. Default: PodManagementPolicy.ORDERED_READY
        :param replicas: (experimental) Number of desired pods. Default: 1
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param pod_metadata: (experimental) The pod metadata.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        props = StatefulSetProps(
            service=service,
            default_selector=default_selector,
            pod_management_policy=pod_management_policy,
            replicas=replicas,
            metadata=metadata,
            pod_metadata=pod_metadata,
            containers=containers,
            restart_policy=restart_policy,
            service_account=service_account,
            volumes=volumes,
        )

        jsii.create(StatefulSet, self, [scope, id, props])

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional[ImagePullPolicy] = None,
        liveness: typing.Optional[Probe] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional[Probe] = None,
        startup: typing.Optional[Probe] = None,
        volume_mounts: typing.Optional[typing.List["VolumeMount"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        container = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        return typing.cast(Container, jsii.invoke(self, "addContainer", [container]))

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: "Volume") -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVolume", [volume]))

    @jsii.member(jsii_name="selectByLabel")
    def select_by_label(self, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Configure a label selector to this deployment.

        Pods that have the label will be selected by deployments configured with this spec.

        :param key: - The label key.
        :param value: - The label value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "selectByLabel", [key, value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        return typing.cast(typing.List[Container], jsii.get(self, "containers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelSelector")
    def label_selector(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The labels this statefulset will match against in order to select pods.

        Returns a a copy. Use ``selectByLabel()`` to add labels.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labelSelector"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podManagementPolicy")
    def pod_management_policy(self) -> PodManagementPolicy:
        '''(experimental) Management policy to use for the set.

        :stability: experimental
        '''
        return typing.cast(PodManagementPolicy, jsii.get(self, "podManagementPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podMetadata")
    def pod_metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''(experimental) Provides read/write access to the underlying pod metadata of the resource.

        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObjectMetadataDefinition, jsii.get(self, "podMetadata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicas")
    def replicas(self) -> jsii.Number:
        '''(experimental) Number of desired pods.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "replicas"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List["Volume"]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        return typing.cast(typing.List["Volume"], jsii.get(self, "volumes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[RestartPolicy], jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IServiceAccount], jsii.get(self, "serviceAccount"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.StatefulSetProps",
    jsii_struct_bases=[ResourceProps, PodTemplateProps],
    name_mapping={
        "metadata": "metadata",
        "containers": "containers",
        "restart_policy": "restartPolicy",
        "service_account": "serviceAccount",
        "volumes": "volumes",
        "pod_metadata": "podMetadata",
        "service": "service",
        "default_selector": "defaultSelector",
        "pod_management_policy": "podManagementPolicy",
        "replicas": "replicas",
    },
)
class StatefulSetProps(ResourceProps, PodTemplateProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List["Volume"]] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        service: Service,
        default_selector: typing.Optional[builtins.bool] = None,
        pod_management_policy: typing.Optional[PodManagementPolicy] = None,
        replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``StatefulSet``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.
        :param pod_metadata: (experimental) The pod metadata.
        :param service: (experimental) Service to associate with the statefulset.
        :param default_selector: (experimental) Automatically allocates a pod selector for this statefulset. If this is set to ``false`` you must define your selector through ``statefulset.podMetadata.addLabel()`` and ``statefulset.selectByLabel()``. Default: true
        :param pod_management_policy: (experimental) Pod management policy to use for this statefulset. Default: PodManagementPolicy.ORDERED_READY
        :param replicas: (experimental) Number of desired pods. Default: 1

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        if isinstance(pod_metadata, dict):
            pod_metadata = cdk8s.ApiObjectMetadata(**pod_metadata)
        self._values: typing.Dict[str, typing.Any] = {
            "service": service,
        }
        if metadata is not None:
            self._values["metadata"] = metadata
        if containers is not None:
            self._values["containers"] = containers
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if volumes is not None:
            self._values["volumes"] = volumes
        if pod_metadata is not None:
            self._values["pod_metadata"] = pod_metadata
        if default_selector is not None:
            self._values["default_selector"] = default_selector
        if pod_management_policy is not None:
            self._values["pod_management_policy"] = pod_management_policy
        if replicas is not None:
            self._values["replicas"] = replicas

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def containers(self) -> typing.Optional[typing.List[ContainerProps]]:
        '''(experimental) List of containers belonging to the pod.

        Containers cannot currently be
        added or removed. There must be at least one container in a Pod.

        You can add additionnal containers using ``podSpec.addContainer()``

        :default: - No containers. Note that a pod spec must include at least one container.

        :stability: experimental
        '''
        result = self._values.get("containers")
        return typing.cast(typing.Optional[typing.List[ContainerProps]], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :default: RestartPolicy.ALWAYS

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy
        :stability: experimental
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional[RestartPolicy], result)

    @builtins.property
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) A service account provides an identity for processes that run in a Pod.

        When you (a human) access the cluster (for example, using kubectl), you are
        authenticated by the apiserver as a particular User Account (currently this
        is usually admin, unless your cluster administrator has customized your
        cluster). Processes in containers inside pods can also contact the
        apiserver. When they do, they are authenticated as a particular Service
        Account (for example, default).

        :default: - No service account.

        :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[IServiceAccount], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List["Volume"]]:
        '''(experimental) List of volumes that can be mounted by containers belonging to the pod.

        You can also add volumes later using ``podSpec.addVolume()``

        :default: - No volumes.

        :see: https://kubernetes.io/docs/concepts/storage/volumes
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List["Volume"]], result)

    @builtins.property
    def pod_metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) The pod metadata.

        :stability: experimental
        '''
        result = self._values.get("pod_metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def service(self) -> Service:
        '''(experimental) Service to associate with the statefulset.

        :stability: experimental
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(Service, result)

    @builtins.property
    def default_selector(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically allocates a pod selector for this statefulset.

        If this is set to ``false`` you must define your selector through
        ``statefulset.podMetadata.addLabel()`` and ``statefulset.selectByLabel()``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("default_selector")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pod_management_policy(self) -> typing.Optional[PodManagementPolicy]:
        '''(experimental) Pod management policy to use for this statefulset.

        :default: PodManagementPolicy.ORDERED_READY

        :stability: experimental
        '''
        result = self._values.get("pod_management_policy")
        return typing.cast(typing.Optional[PodManagementPolicy], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of desired pods.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatefulSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Volume(metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.Volume"):
    '''(experimental) Volume represents a named volume in a pod that may be accessed by any container in the pod.

    Docker also has a concept of volumes, though it is somewhat looser and less
    managed. In Docker, a volume is simply a directory on disk or in another
    Container. Lifetimes are not managed and until very recently there were only
    local-disk-backed volumes. Docker now provides volume drivers, but the
    functionality is very limited for now (e.g. as of Docker 1.7 only one volume
    driver is allowed per Container and there is no way to pass parameters to
    volumes).

    A Kubernetes volume, on the other hand, has an explicit lifetime - the same
    as the Pod that encloses it. Consequently, a volume outlives any Containers
    that run within the Pod, and data is preserved across Container restarts. Of
    course, when a Pod ceases to exist, the volume will cease to exist, too.
    Perhaps more importantly than this, Kubernetes supports many types of
    volumes, and a Pod can use any number of them simultaneously.

    At its core, a volume is just a directory, possibly with some data in it,
    which is accessible to the Containers in a Pod. How that directory comes to
    be, the medium that backs it, and the contents of it are determined by the
    particular volume type used.

    To use a volume, a Pod specifies what volumes to provide for the Pod (the
    .spec.volumes field) and where to mount those into Containers (the
    .spec.containers[*].volumeMounts field).

    A process in a container sees a filesystem view composed from their Docker
    image and volumes. The Docker image is at the root of the filesystem
    hierarchy, and any volumes are mounted at the specified paths within the
    image. Volumes can not mount onto other volumes

    :stability: experimental
    '''

    def __init__(self, name: builtins.str, config: typing.Any) -> None:
        '''
        :param name: -
        :param config: -

        :stability: experimental
        '''
        jsii.create(Volume, self, [name, config])

    @jsii.member(jsii_name="fromConfigMap") # type: ignore[misc]
    @builtins.classmethod
    def from_config_map(
        cls,
        config_map: "IConfigMap",
        *,
        default_mode: typing.Optional[jsii.Number] = None,
        items: typing.Optional[typing.Mapping[builtins.str, PathMapping]] = None,
        name: typing.Optional[builtins.str] = None,
        optional: typing.Optional[builtins.bool] = None,
    ) -> "Volume":
        '''(experimental) Populate the volume from a ConfigMap.

        The configMap resource provides a way to inject configuration data into
        Pods. The data stored in a ConfigMap object can be referenced in a volume
        of type configMap and then consumed by containerized applications running
        in a Pod.

        When referencing a configMap object, you can simply provide its name in the
        volume to reference it. You can also customize the path to use for a
        specific entry in the ConfigMap.

        :param config_map: The config map to use to populate the volume.
        :param default_mode: (experimental) Mode bits to use on created files by default. Must be a value between 0 and 0777. Defaults to 0644. Directories within the path are not affected by this setting. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set. Default: 644. Directories within the path are not affected by this setting. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set.
        :param items: (experimental) If unspecified, each key-value pair in the Data field of the referenced ConfigMap will be projected into the volume as a file whose name is the key and content is the value. If specified, the listed keys will be projected into the specified paths, and unlisted keys will not be present. If a key is specified which is not present in the ConfigMap, the volume setup will error unless it is marked optional. Paths must be relative and may not contain the '..' path or start with '..'. Default: - no mapping
        :param name: (experimental) The volume name. Default: - auto-generated
        :param optional: (experimental) Specify whether the ConfigMap or its keys must be defined. Default: - undocumented

        :stability: experimental
        '''
        options = ConfigMapVolumeOptions(
            default_mode=default_mode, items=items, name=name, optional=optional
        )

        return typing.cast("Volume", jsii.sinvoke(cls, "fromConfigMap", [config_map, options]))

    @jsii.member(jsii_name="fromEmptyDir") # type: ignore[misc]
    @builtins.classmethod
    def from_empty_dir(
        cls,
        name: builtins.str,
        *,
        medium: typing.Optional[EmptyDirMedium] = None,
        size_limit: typing.Optional[cdk8s.Size] = None,
    ) -> "Volume":
        '''(experimental) An emptyDir volume is first created when a Pod is assigned to a Node, and exists as long as that Pod is running on that node.

        As the name says, it is
        initially empty. Containers in the Pod can all read and write the same
        files in the emptyDir volume, though that volume can be mounted at the same
        or different paths in each Container. When a Pod is removed from a node for
        any reason, the data in the emptyDir is deleted forever.

        :param name: -
        :param medium: (experimental) By default, emptyDir volumes are stored on whatever medium is backing the node - that might be disk or SSD or network storage, depending on your environment. However, you can set the emptyDir.medium field to ``EmptyDirMedium.MEMORY`` to tell Kubernetes to mount a tmpfs (RAM-backed filesystem) for you instead. While tmpfs is very fast, be aware that unlike disks, tmpfs is cleared on node reboot and any files you write will count against your Container's memory limit. Default: EmptyDirMedium.DEFAULT
        :param size_limit: (experimental) Total amount of local storage required for this EmptyDir volume. The size limit is also applicable for memory medium. The maximum usage on memory medium EmptyDir would be the minimum value between the SizeLimit specified here and the sum of memory limits of all containers in a pod. Default: - limit is undefined

        :see: http://kubernetes.io/docs/user-guide/volumes#emptydir
        :stability: experimental
        '''
        options = EmptyDirVolumeOptions(medium=medium, size_limit=size_limit)

        return typing.cast("Volume", jsii.sinvoke(cls, "fromEmptyDir", [name, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.VolumeMount",
    jsii_struct_bases=[MountOptions],
    name_mapping={
        "propagation": "propagation",
        "read_only": "readOnly",
        "sub_path": "subPath",
        "sub_path_expr": "subPathExpr",
        "path": "path",
        "volume": "volume",
    },
)
class VolumeMount(MountOptions):
    def __init__(
        self,
        *,
        propagation: typing.Optional[MountPropagation] = None,
        read_only: typing.Optional[builtins.bool] = None,
        sub_path: typing.Optional[builtins.str] = None,
        sub_path_expr: typing.Optional[builtins.str] = None,
        path: builtins.str,
        volume: Volume,
    ) -> None:
        '''(experimental) Mount a volume from the pod to the container.

        :param propagation: (experimental) Determines how mounts are propagated from the host to container and the other way around. When not set, MountPropagationNone is used. Mount propagation allows for sharing volumes mounted by a Container to other Containers in the same Pod, or even to other Pods on the same node. This field is beta in 1.10. Default: MountPropagation.NONE
        :param read_only: (experimental) Mounted read-only if true, read-write otherwise (false or unspecified). Defaults to false. Default: false
        :param sub_path: (experimental) Path within the volume from which the container's volume should be mounted.). Default: "" the volume's root
        :param sub_path_expr: (experimental) Expanded path within the volume from which the container's volume should be mounted. Behaves similarly to SubPath but environment variable references $(VAR_NAME) are expanded using the container's environment. Defaults to "" (volume's root). SubPathExpr and SubPath are mutually exclusive. This field is beta in 1.15. ``subPathExpr`` and ``subPath`` are mutually exclusive. This field is beta in 1.15. Default: "" volume's root.
        :param path: (experimental) Path within the container at which the volume should be mounted. Must not contain ':'.
        :param volume: (experimental) The volume to mount.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
            "volume": volume,
        }
        if propagation is not None:
            self._values["propagation"] = propagation
        if read_only is not None:
            self._values["read_only"] = read_only
        if sub_path is not None:
            self._values["sub_path"] = sub_path
        if sub_path_expr is not None:
            self._values["sub_path_expr"] = sub_path_expr

    @builtins.property
    def propagation(self) -> typing.Optional[MountPropagation]:
        '''(experimental) Determines how mounts are propagated from the host to container and the other way around.

        When not set, MountPropagationNone is used.

        Mount propagation allows for sharing volumes mounted by a Container to
        other Containers in the same Pod, or even to other Pods on the same node.

        This field is beta in 1.10.

        :default: MountPropagation.NONE

        :stability: experimental
        '''
        result = self._values.get("propagation")
        return typing.cast(typing.Optional[MountPropagation], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Mounted read-only if true, read-write otherwise (false or unspecified).

        Defaults to false.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sub_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path within the volume from which the container's volume should be mounted.).

        :default: "" the volume's root

        :stability: experimental
        '''
        result = self._values.get("sub_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sub_path_expr(self) -> typing.Optional[builtins.str]:
        '''(experimental) Expanded path within the volume from which the container's volume should be mounted.

        Behaves similarly to SubPath but environment variable references
        $(VAR_NAME) are expanded using the container's environment. Defaults to ""
        (volume's root). SubPathExpr and SubPath are mutually exclusive. This field
        is beta in 1.15.

        ``subPathExpr`` and ``subPath`` are mutually exclusive. This field is beta in
        1.15.

        :default: "" volume's root.

        :stability: experimental
        '''
        result = self._values.get("sub_path_expr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) Path within the container at which the volume should be mounted.

        Must not
        contain ':'.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def volume(self) -> Volume:
        '''(experimental) The volume to mount.

        :stability: experimental
        '''
        result = self._values.get("volume")
        assert result is not None, "Required property 'volume' is missing"
        return typing.cast(Volume, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VolumeMount(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.CommandProbeOptions",
    jsii_struct_bases=[ProbeOptions],
    name_mapping={
        "failure_threshold": "failureThreshold",
        "initial_delay_seconds": "initialDelaySeconds",
        "period_seconds": "periodSeconds",
        "success_threshold": "successThreshold",
        "timeout_seconds": "timeoutSeconds",
    },
)
class CommandProbeOptions(ProbeOptions):
    def __init__(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
        initial_delay_seconds: typing.Optional[cdk8s.Duration] = None,
        period_seconds: typing.Optional[cdk8s.Duration] = None,
        success_threshold: typing.Optional[jsii.Number] = None,
        timeout_seconds: typing.Optional[cdk8s.Duration] = None,
    ) -> None:
        '''(experimental) Options for ``Probe.fromCommand()``.

        :param failure_threshold: (experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded. Defaults to 3. Minimum value is 1. Default: 3
        :param initial_delay_seconds: (experimental) Number of seconds after the container has started before liveness probes are initiated. Default: - immediate
        :param period_seconds: (experimental) How often (in seconds) to perform the probe. Default to 10 seconds. Minimum value is 1. Default: Duration.seconds(10) Minimum value is 1.
        :param success_threshold: (experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1. Must be 1 for liveness and startup. Minimum value is 1. Default: 1 Must be 1 for liveness and startup. Minimum value is 1.
        :param timeout_seconds: (experimental) Number of seconds after which the probe times out. Defaults to 1 second. Minimum value is 1. Default: Duration.seconds(1)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if failure_threshold is not None:
            self._values["failure_threshold"] = failure_threshold
        if initial_delay_seconds is not None:
            self._values["initial_delay_seconds"] = initial_delay_seconds
        if period_seconds is not None:
            self._values["period_seconds"] = period_seconds
        if success_threshold is not None:
            self._values["success_threshold"] = success_threshold
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds

    @builtins.property
    def failure_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded.

        Defaults to 3. Minimum value is 1.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def initial_delay_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Number of seconds after the container has started before liveness probes are initiated.

        :default: - immediate

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#container-probes
        :stability: experimental
        '''
        result = self._values.get("initial_delay_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def period_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) How often (in seconds) to perform the probe.

        Default to 10 seconds. Minimum value is 1.

        :default: Duration.seconds(10) Minimum value is 1.

        :stability: experimental
        '''
        result = self._values.get("period_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def success_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1.

        Must be 1 for liveness and startup. Minimum value is 1.

        :default: 1 Must be 1 for liveness and startup. Minimum value is 1.

        :stability: experimental
        '''
        result = self._values.get("success_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Number of seconds after which the probe times out.

        Defaults to 1 second. Minimum value is 1.

        :default: Duration.seconds(1)

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#container-probes
        :stability: experimental
        '''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommandProbeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ConfigMapProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={"metadata": "metadata", "binary_data": "binaryData", "data": "data"},
)
class ConfigMapProps(ResourceProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        binary_data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``ConfigMap``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param binary_data: (experimental) BinaryData contains the binary data. Each key must consist of alphanumeric characters, '-', '_' or '.'. BinaryData can contain byte sequences that are not in the UTF-8 range. The keys stored in BinaryData must not overlap with the ones in the Data field, this is enforced during validation process. Using this field will require 1.10+ apiserver and kubelet. You can also add binary data using ``configMap.addBinaryData()``.
        :param data: (experimental) Data contains the configuration data. Each key must consist of alphanumeric characters, '-', '_' or '.'. Values with non-UTF-8 byte sequences must use the BinaryData field. The keys stored in Data must not overlap with the keys in the BinaryData field, this is enforced during validation process. You can also add data using ``configMap.addData()``.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if binary_data is not None:
            self._values["binary_data"] = binary_data
        if data is not None:
            self._values["data"] = data

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def binary_data(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) BinaryData contains the binary data.

        Each key must consist of alphanumeric characters, '-', '_' or '.'.
        BinaryData can contain byte sequences that are not in the UTF-8 range. The
        keys stored in BinaryData must not overlap with the ones in the Data field,
        this is enforced during validation process. Using this field will require
        1.10+ apiserver and kubelet.

        You can also add binary data using ``configMap.addBinaryData()``.

        :stability: experimental
        '''
        result = self._values.get("binary_data")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def data(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Data contains the configuration data.

        Each key must consist of alphanumeric characters, '-', '_' or '.'. Values
        with non-UTF-8 byte sequences must use the BinaryData field. The keys
        stored in Data must not overlap with the keys in the BinaryData field, this
        is enforced during validation process.

        You can also add data using ``configMap.addData()``.

        :stability: experimental
        '''
        result = self._values.get("data")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigMapProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPodTemplate)
class Deployment(
    Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-plus-17.Deployment",
):
    '''(experimental) A Deployment provides declarative updates for Pods and ReplicaSets.

    You describe a desired state in a Deployment, and the Deployment Controller changes the actual
    state to the desired state at a controlled rate. You can define Deployments to create new ReplicaSets, or to remove
    existing Deployments and adopt all their resources with new Deployments.
    .. epigraph::

       Note: Do not manage ReplicaSets owned by a Deployment. Consider opening an issue in the main Kubernetes repository if your use case is not covered below.


    Use Case

    The following are typical use cases for Deployments:

    - Create a Deployment to rollout a ReplicaSet. The ReplicaSet creates Pods in the background.
      Check the status of the rollout to see if it succeeds or not.
    - Declare the new state of the Pods by updating the PodTemplateSpec of the Deployment.
      A new ReplicaSet is created and the Deployment manages moving the Pods from the old ReplicaSet to the new one at a controlled rate.
      Each new ReplicaSet updates the revision of the Deployment.
    - Rollback to an earlier Deployment revision if the current state of the Deployment is not stable.
      Each rollback updates the revision of the Deployment.
    - Scale up the Deployment to facilitate more load.
    - Pause the Deployment to apply multiple fixes to its PodTemplateSpec and then resume it to start a new rollout.
    - Use the status of the Deployment as an indicator that a rollout has stuck.
    - Clean up older ReplicaSets that you don't need anymore.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_selector: typing.Optional[builtins.bool] = None,
        replicas: typing.Optional[jsii.Number] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List[Volume]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param default_selector: (experimental) Automatically allocates a pod selector for this deployment. If this is set to ``false`` you must define your selector through ``deployment.podMetadata.addLabel()`` and ``deployment.selectByLabel()``. Default: true
        :param replicas: (experimental) Number of desired pods. Default: 1
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param pod_metadata: (experimental) The pod metadata.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        props = DeploymentProps(
            default_selector=default_selector,
            replicas=replicas,
            metadata=metadata,
            pod_metadata=pod_metadata,
            containers=containers,
            restart_policy=restart_policy,
            service_account=service_account,
            volumes=volumes,
        )

        jsii.create(Deployment, self, [scope, id, props])

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional[ImagePullPolicy] = None,
        liveness: typing.Optional[Probe] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional[Probe] = None,
        startup: typing.Optional[Probe] = None,
        volume_mounts: typing.Optional[typing.List[VolumeMount]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        container = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        return typing.cast(Container, jsii.invoke(self, "addContainer", [container]))

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: Volume) -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVolume", [volume]))

    @jsii.member(jsii_name="expose")
    def expose(
        self,
        port: jsii.Number,
        *,
        name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[Protocol] = None,
        service_type: typing.Optional[ServiceType] = None,
        target_port: typing.Optional[jsii.Number] = None,
    ) -> Service:
        '''(experimental) Expose a deployment via a service.

        This is equivalent to running ``kubectl expose deployment <deployment-name>``.

        :param port: The port number the service will bind to.
        :param name: (experimental) The name of the service to expose. This will be set on the Service.metadata and must be a DNS_LABEL Default: undefined Uses the system generated name.
        :param protocol: (experimental) The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP. Default: Protocol.TCP
        :param service_type: (experimental) The type of the exposed service. Default: - ClusterIP.
        :param target_port: (experimental) The port number the service will redirect to. Default: - The port of the first container in the deployment (ie. containers[0].port)

        :stability: experimental
        '''
        options = ExposeOptions(
            name=name,
            protocol=protocol,
            service_type=service_type,
            target_port=target_port,
        )

        return typing.cast(Service, jsii.invoke(self, "expose", [port, options]))

    @jsii.member(jsii_name="selectByLabel")
    def select_by_label(self, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Configure a label selector to this deployment.

        Pods that have the label will be selected by deployments configured with this spec.

        :param key: - The label key.
        :param value: - The label value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "selectByLabel", [key, value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        return typing.cast(typing.List[Container], jsii.get(self, "containers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelSelector")
    def label_selector(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The labels this deployment will match against in order to select pods.

        Returns a a copy. Use ``selectByLabel()`` to add labels.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labelSelector"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podMetadata")
    def pod_metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''(experimental) Provides read/write access to the underlying pod metadata of the resource.

        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObjectMetadataDefinition, jsii.get(self, "podMetadata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicas")
    def replicas(self) -> jsii.Number:
        '''(experimental) Number of desired pods.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "replicas"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List[Volume]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        return typing.cast(typing.List[Volume], jsii.get(self, "volumes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[RestartPolicy], jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IServiceAccount], jsii.get(self, "serviceAccount"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.DeploymentProps",
    jsii_struct_bases=[ResourceProps, PodTemplateProps],
    name_mapping={
        "metadata": "metadata",
        "containers": "containers",
        "restart_policy": "restartPolicy",
        "service_account": "serviceAccount",
        "volumes": "volumes",
        "pod_metadata": "podMetadata",
        "default_selector": "defaultSelector",
        "replicas": "replicas",
    },
)
class DeploymentProps(ResourceProps, PodTemplateProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List[Volume]] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        default_selector: typing.Optional[builtins.bool] = None,
        replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``Deployment``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.
        :param pod_metadata: (experimental) The pod metadata.
        :param default_selector: (experimental) Automatically allocates a pod selector for this deployment. If this is set to ``false`` you must define your selector through ``deployment.podMetadata.addLabel()`` and ``deployment.selectByLabel()``. Default: true
        :param replicas: (experimental) Number of desired pods. Default: 1

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        if isinstance(pod_metadata, dict):
            pod_metadata = cdk8s.ApiObjectMetadata(**pod_metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if containers is not None:
            self._values["containers"] = containers
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if volumes is not None:
            self._values["volumes"] = volumes
        if pod_metadata is not None:
            self._values["pod_metadata"] = pod_metadata
        if default_selector is not None:
            self._values["default_selector"] = default_selector
        if replicas is not None:
            self._values["replicas"] = replicas

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def containers(self) -> typing.Optional[typing.List[ContainerProps]]:
        '''(experimental) List of containers belonging to the pod.

        Containers cannot currently be
        added or removed. There must be at least one container in a Pod.

        You can add additionnal containers using ``podSpec.addContainer()``

        :default: - No containers. Note that a pod spec must include at least one container.

        :stability: experimental
        '''
        result = self._values.get("containers")
        return typing.cast(typing.Optional[typing.List[ContainerProps]], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :default: RestartPolicy.ALWAYS

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy
        :stability: experimental
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional[RestartPolicy], result)

    @builtins.property
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) A service account provides an identity for processes that run in a Pod.

        When you (a human) access the cluster (for example, using kubectl), you are
        authenticated by the apiserver as a particular User Account (currently this
        is usually admin, unless your cluster administrator has customized your
        cluster). Processes in containers inside pods can also contact the
        apiserver. When they do, they are authenticated as a particular Service
        Account (for example, default).

        :default: - No service account.

        :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[IServiceAccount], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[Volume]]:
        '''(experimental) List of volumes that can be mounted by containers belonging to the pod.

        You can also add volumes later using ``podSpec.addVolume()``

        :default: - No volumes.

        :see: https://kubernetes.io/docs/concepts/storage/volumes
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[Volume]], result)

    @builtins.property
    def pod_metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) The pod metadata.

        :stability: experimental
        '''
        result = self._values.get("pod_metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def default_selector(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically allocates a pod selector for this deployment.

        If this is set to ``false`` you must define your selector through
        ``deployment.podMetadata.addLabel()`` and ``deployment.selectByLabel()``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("default_selector")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of desired pods.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.HttpGetProbeOptions",
    jsii_struct_bases=[ProbeOptions],
    name_mapping={
        "failure_threshold": "failureThreshold",
        "initial_delay_seconds": "initialDelaySeconds",
        "period_seconds": "periodSeconds",
        "success_threshold": "successThreshold",
        "timeout_seconds": "timeoutSeconds",
        "port": "port",
    },
)
class HttpGetProbeOptions(ProbeOptions):
    def __init__(
        self,
        *,
        failure_threshold: typing.Optional[jsii.Number] = None,
        initial_delay_seconds: typing.Optional[cdk8s.Duration] = None,
        period_seconds: typing.Optional[cdk8s.Duration] = None,
        success_threshold: typing.Optional[jsii.Number] = None,
        timeout_seconds: typing.Optional[cdk8s.Duration] = None,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Options for ``Probe.fromHttpGet()``.

        :param failure_threshold: (experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded. Defaults to 3. Minimum value is 1. Default: 3
        :param initial_delay_seconds: (experimental) Number of seconds after the container has started before liveness probes are initiated. Default: - immediate
        :param period_seconds: (experimental) How often (in seconds) to perform the probe. Default to 10 seconds. Minimum value is 1. Default: Duration.seconds(10) Minimum value is 1.
        :param success_threshold: (experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1. Must be 1 for liveness and startup. Minimum value is 1. Default: 1 Must be 1 for liveness and startup. Minimum value is 1.
        :param timeout_seconds: (experimental) Number of seconds after which the probe times out. Defaults to 1 second. Minimum value is 1. Default: Duration.seconds(1)
        :param port: (experimental) The TCP port to use when sending the GET request. Default: - defaults to ``container.port``.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if failure_threshold is not None:
            self._values["failure_threshold"] = failure_threshold
        if initial_delay_seconds is not None:
            self._values["initial_delay_seconds"] = initial_delay_seconds
        if period_seconds is not None:
            self._values["period_seconds"] = period_seconds
        if success_threshold is not None:
            self._values["success_threshold"] = success_threshold
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def failure_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum consecutive failures for the probe to be considered failed after having succeeded.

        Defaults to 3. Minimum value is 1.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("failure_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def initial_delay_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Number of seconds after the container has started before liveness probes are initiated.

        :default: - immediate

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#container-probes
        :stability: experimental
        '''
        result = self._values.get("initial_delay_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def period_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) How often (in seconds) to perform the probe.

        Default to 10 seconds. Minimum value is 1.

        :default: Duration.seconds(10) Minimum value is 1.

        :stability: experimental
        '''
        result = self._values.get("period_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def success_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Minimum consecutive successes for the probe to be considered successful after having failed. Defaults to 1.

        Must be 1 for liveness and startup. Minimum value is 1.

        :default: 1 Must be 1 for liveness and startup. Minimum value is 1.

        :stability: experimental
        '''
        result = self._values.get("success_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Number of seconds after which the probe times out.

        Defaults to 1 second. Minimum value is 1.

        :default: Duration.seconds(1)

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle#container-probes
        :stability: experimental
        '''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The TCP port to use when sending the GET request.

        :default: - defaults to ``container.port``.

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpGetProbeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk8s-plus-17.IConfigMap")
class IConfigMap(IResource, typing_extensions.Protocol):
    '''(experimental) Represents a config map.

    :stability: experimental
    '''

    @builtins.staticmethod
    def __jsii_proxy_class__() -> typing.Type["_IConfigMapProxy"]:
        return _IConfigMapProxy


class _IConfigMapProxy(
    jsii.proxy_for(IResource) # type: ignore[misc]
):
    '''(experimental) Represents a config map.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-plus-17.IConfigMap"
    pass


class IngressV1Beta1(
    Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-plus-17.IngressV1Beta1",
):
    '''(experimental) Ingress is a collection of rules that allow inbound connections to reach the endpoints defined by a backend.

    An Ingress can be configured to give services
    externally-reachable urls, load balance traffic, terminate SSL, offer name
    based virtual hosting etc.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_backend: typing.Optional[IngressV1Beta1Backend] = None,
        rules: typing.Optional[typing.List[IngressV1Beta1Rule]] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param default_backend: (experimental) The default backend services requests that do not match any rule. Using this option or the ``addDefaultBackend()`` method is equivalent to adding a rule with both ``path`` and ``host`` undefined.
        :param rules: (experimental) Routing rules for this ingress. Each rule must define an ``IngressBackend`` that will receive the requests that match this rule. If both ``host`` and ``path`` are not specifiec, this backend will be used as the default backend of the ingress. You can also add rules later using ``addRule()``, ``addHostRule()``, ``addDefaultBackend()`` and ``addHostDefaultBackend()``.
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        props = IngressV1Beta1Props(
            default_backend=default_backend, rules=rules, metadata=metadata
        )

        jsii.create(IngressV1Beta1, self, [scope, id, props])

    @jsii.member(jsii_name="addDefaultBackend")
    def add_default_backend(self, backend: IngressV1Beta1Backend) -> None:
        '''(experimental) Defines the default backend for this ingress.

        A default backend capable of
        servicing requests that don't match any rule.

        :param backend: The backend to use for requests that do not match any rule.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addDefaultBackend", [backend]))

    @jsii.member(jsii_name="addHostDefaultBackend")
    def add_host_default_backend(
        self,
        host: builtins.str,
        backend: IngressV1Beta1Backend,
    ) -> None:
        '''(experimental) Specify a default backend for a specific host name.

        This backend will be used as a catch-all for requests
        targeted to this host name (the ``Host`` header matches this value).

        :param host: The host name to match.
        :param backend: The backend to route to.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addHostDefaultBackend", [host, backend]))

    @jsii.member(jsii_name="addHostRule")
    def add_host_rule(
        self,
        host: builtins.str,
        path: builtins.str,
        backend: IngressV1Beta1Backend,
    ) -> None:
        '''(experimental) Adds an ingress rule applied to requests to a specific host and a specific HTTP path (the ``Host`` header matches this value).

        :param host: The host name.
        :param path: The HTTP path.
        :param backend: The backend to route requests to.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addHostRule", [host, path, backend]))

    @jsii.member(jsii_name="addRule")
    def add_rule(self, path: builtins.str, backend: IngressV1Beta1Backend) -> None:
        '''(experimental) Adds an ingress rule applied to requests sent to a specific HTTP path.

        :param path: The HTTP path.
        :param backend: The backend to route requests to.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addRule", [path, backend]))

    @jsii.member(jsii_name="addRules")
    def add_rules(self, *rules: IngressV1Beta1Rule) -> None:
        '''(experimental) Adds rules to this ingress.

        :param rules: The rules to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addRules", [*rules]))

    @jsii.member(jsii_name="onValidate")
    def _on_validate(self) -> typing.List[builtins.str]:
        '''(experimental) (deprecated) Validate the current construct.

        This method can be implemented by derived constructs in order to perform
        validation logic. It is called on all constructs before synthesis.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "onValidate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.IngressV1Beta1Props",
    jsii_struct_bases=[ResourceProps],
    name_mapping={
        "metadata": "metadata",
        "default_backend": "defaultBackend",
        "rules": "rules",
    },
)
class IngressV1Beta1Props(ResourceProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        default_backend: typing.Optional[IngressV1Beta1Backend] = None,
        rules: typing.Optional[typing.List[IngressV1Beta1Rule]] = None,
    ) -> None:
        '''(experimental) Properties for ``Ingress``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param default_backend: (experimental) The default backend services requests that do not match any rule. Using this option or the ``addDefaultBackend()`` method is equivalent to adding a rule with both ``path`` and ``host`` undefined.
        :param rules: (experimental) Routing rules for this ingress. Each rule must define an ``IngressBackend`` that will receive the requests that match this rule. If both ``host`` and ``path`` are not specifiec, this backend will be used as the default backend of the ingress. You can also add rules later using ``addRule()``, ``addHostRule()``, ``addDefaultBackend()`` and ``addHostDefaultBackend()``.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if default_backend is not None:
            self._values["default_backend"] = default_backend
        if rules is not None:
            self._values["rules"] = rules

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def default_backend(self) -> typing.Optional[IngressV1Beta1Backend]:
        '''(experimental) The default backend services requests that do not match any rule.

        Using this option or the ``addDefaultBackend()`` method is equivalent to
        adding a rule with both ``path`` and ``host`` undefined.

        :stability: experimental
        '''
        result = self._values.get("default_backend")
        return typing.cast(typing.Optional[IngressV1Beta1Backend], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List[IngressV1Beta1Rule]]:
        '''(experimental) Routing rules for this ingress.

        Each rule must define an ``IngressBackend`` that will receive the requests
        that match this rule. If both ``host`` and ``path`` are not specifiec, this
        backend will be used as the default backend of the ingress.

        You can also add rules later using ``addRule()``, ``addHostRule()``,
        ``addDefaultBackend()`` and ``addHostDefaultBackend()``.

        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List[IngressV1Beta1Rule]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IngressV1Beta1Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPodTemplate)
class Job(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.Job"):
    '''(experimental) A Job creates one or more Pods and ensures that a specified number of them successfully terminate.

    As pods successfully complete,
    the Job tracks the successful completions. When a specified number of successful completions is reached, the task (ie, Job) is complete.
    Deleting a Job will clean up the Pods it created. A simple case is to create one Job object in order to reliably run one Pod to completion.
    The Job object will start a new Pod if the first Pod fails or is deleted (for example due to a node hardware failure or a node reboot).
    You can also use a Job to run multiple Pods in parallel.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        active_deadline: typing.Optional[cdk8s.Duration] = None,
        backoff_limit: typing.Optional[jsii.Number] = None,
        ttl_after_finished: typing.Optional[cdk8s.Duration] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List[Volume]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param active_deadline: (experimental) Specifies the duration the job may be active before the system tries to terminate it. Default: - If unset, then there is no deadline.
        :param backoff_limit: (experimental) Specifies the number of retries before marking this job failed. Default: - If not set, system defaults to 6.
        :param ttl_after_finished: (experimental) Limits the lifetime of a Job that has finished execution (either Complete or Failed). If this field is set, after the Job finishes, it is eligible to be automatically deleted. When the Job is being deleted, its lifecycle guarantees (e.g. finalizers) will be honored. If this field is set to zero, the Job becomes eligible to be deleted immediately after it finishes. This field is alpha-level and is only honored by servers that enable the ``TTLAfterFinished`` feature. Default: - If this field is unset, the Job won't be automatically deleted.
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param pod_metadata: (experimental) The pod metadata.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        props = JobProps(
            active_deadline=active_deadline,
            backoff_limit=backoff_limit,
            ttl_after_finished=ttl_after_finished,
            metadata=metadata,
            pod_metadata=pod_metadata,
            containers=containers,
            restart_policy=restart_policy,
            service_account=service_account,
            volumes=volumes,
        )

        jsii.create(Job, self, [scope, id, props])

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional[ImagePullPolicy] = None,
        liveness: typing.Optional[Probe] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional[Probe] = None,
        startup: typing.Optional[Probe] = None,
        volume_mounts: typing.Optional[typing.List[VolumeMount]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        container = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        return typing.cast(Container, jsii.invoke(self, "addContainer", [container]))

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: Volume) -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVolume", [volume]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        return typing.cast(typing.List[Container], jsii.get(self, "containers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podMetadata")
    def pod_metadata(self) -> cdk8s.ApiObjectMetadataDefinition:
        '''(experimental) Provides read/write access to the underlying pod metadata of the resource.

        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObjectMetadataDefinition, jsii.get(self, "podMetadata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List[Volume]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        return typing.cast(typing.List[Volume], jsii.get(self, "volumes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="activeDeadline")
    def active_deadline(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Duration before job is terminated.

        If undefined, there is no deadline.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[cdk8s.Duration], jsii.get(self, "activeDeadline"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="backoffLimit")
    def backoff_limit(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of retries before marking failed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backoffLimit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[RestartPolicy], jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IServiceAccount], jsii.get(self, "serviceAccount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttlAfterFinished")
    def ttl_after_finished(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) TTL before the job is deleted after it is finished.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[cdk8s.Duration], jsii.get(self, "ttlAfterFinished"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.JobProps",
    jsii_struct_bases=[ResourceProps, PodTemplateProps],
    name_mapping={
        "metadata": "metadata",
        "containers": "containers",
        "restart_policy": "restartPolicy",
        "service_account": "serviceAccount",
        "volumes": "volumes",
        "pod_metadata": "podMetadata",
        "active_deadline": "activeDeadline",
        "backoff_limit": "backoffLimit",
        "ttl_after_finished": "ttlAfterFinished",
    },
)
class JobProps(ResourceProps, PodTemplateProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List[Volume]] = None,
        pod_metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        active_deadline: typing.Optional[cdk8s.Duration] = None,
        backoff_limit: typing.Optional[jsii.Number] = None,
        ttl_after_finished: typing.Optional[cdk8s.Duration] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``Job``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.
        :param pod_metadata: (experimental) The pod metadata.
        :param active_deadline: (experimental) Specifies the duration the job may be active before the system tries to terminate it. Default: - If unset, then there is no deadline.
        :param backoff_limit: (experimental) Specifies the number of retries before marking this job failed. Default: - If not set, system defaults to 6.
        :param ttl_after_finished: (experimental) Limits the lifetime of a Job that has finished execution (either Complete or Failed). If this field is set, after the Job finishes, it is eligible to be automatically deleted. When the Job is being deleted, its lifecycle guarantees (e.g. finalizers) will be honored. If this field is set to zero, the Job becomes eligible to be deleted immediately after it finishes. This field is alpha-level and is only honored by servers that enable the ``TTLAfterFinished`` feature. Default: - If this field is unset, the Job won't be automatically deleted.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        if isinstance(pod_metadata, dict):
            pod_metadata = cdk8s.ApiObjectMetadata(**pod_metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if containers is not None:
            self._values["containers"] = containers
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if volumes is not None:
            self._values["volumes"] = volumes
        if pod_metadata is not None:
            self._values["pod_metadata"] = pod_metadata
        if active_deadline is not None:
            self._values["active_deadline"] = active_deadline
        if backoff_limit is not None:
            self._values["backoff_limit"] = backoff_limit
        if ttl_after_finished is not None:
            self._values["ttl_after_finished"] = ttl_after_finished

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def containers(self) -> typing.Optional[typing.List[ContainerProps]]:
        '''(experimental) List of containers belonging to the pod.

        Containers cannot currently be
        added or removed. There must be at least one container in a Pod.

        You can add additionnal containers using ``podSpec.addContainer()``

        :default: - No containers. Note that a pod spec must include at least one container.

        :stability: experimental
        '''
        result = self._values.get("containers")
        return typing.cast(typing.Optional[typing.List[ContainerProps]], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :default: RestartPolicy.ALWAYS

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy
        :stability: experimental
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional[RestartPolicy], result)

    @builtins.property
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) A service account provides an identity for processes that run in a Pod.

        When you (a human) access the cluster (for example, using kubectl), you are
        authenticated by the apiserver as a particular User Account (currently this
        is usually admin, unless your cluster administrator has customized your
        cluster). Processes in containers inside pods can also contact the
        apiserver. When they do, they are authenticated as a particular Service
        Account (for example, default).

        :default: - No service account.

        :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[IServiceAccount], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[Volume]]:
        '''(experimental) List of volumes that can be mounted by containers belonging to the pod.

        You can also add volumes later using ``podSpec.addVolume()``

        :default: - No volumes.

        :see: https://kubernetes.io/docs/concepts/storage/volumes
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[Volume]], result)

    @builtins.property
    def pod_metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) The pod metadata.

        :stability: experimental
        '''
        result = self._values.get("pod_metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def active_deadline(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Specifies the duration the job may be active before the system tries to terminate it.

        :default: - If unset, then there is no deadline.

        :stability: experimental
        '''
        result = self._values.get("active_deadline")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    @builtins.property
    def backoff_limit(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Specifies the number of retries before marking this job failed.

        :default: - If not set, system defaults to 6.

        :stability: experimental
        '''
        result = self._values.get("backoff_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ttl_after_finished(self) -> typing.Optional[cdk8s.Duration]:
        '''(experimental) Limits the lifetime of a Job that has finished execution (either Complete or Failed).

        If this field is set, after the Job finishes, it is eligible to
        be automatically deleted. When the Job is being deleted, its lifecycle
        guarantees (e.g. finalizers) will be honored. If this field is set to zero,
        the Job becomes eligible to be deleted immediately after it finishes. This
        field is alpha-level and is only honored by servers that enable the
        ``TTLAfterFinished`` feature.

        :default: - If this field is unset, the Job won't be automatically deleted.

        :stability: experimental
        '''
        result = self._values.get("ttl_after_finished")
        return typing.cast(typing.Optional[cdk8s.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPodSpec)
class Pod(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.Pod"):
    '''(experimental) Pod is a collection of containers that can run on a host.

    This resource is
    created by clients and scheduled onto hosts.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List[Volume]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        props = PodProps(
            metadata=metadata,
            containers=containers,
            restart_policy=restart_policy,
            service_account=service_account,
            volumes=volumes,
        )

        jsii.create(Pod, self, [scope, id, props])

    @jsii.member(jsii_name="addContainer")
    def add_container(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        command: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, EnvValue]] = None,
        image_pull_policy: typing.Optional[ImagePullPolicy] = None,
        liveness: typing.Optional[Probe] = None,
        name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        readiness: typing.Optional[Probe] = None,
        startup: typing.Optional[Probe] = None,
        volume_mounts: typing.Optional[typing.List[VolumeMount]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> Container:
        '''(experimental) Add a container to the pod.

        :param image: (experimental) Docker image name.
        :param args: (experimental) Arguments to the entrypoint. The docker image's CMD is used if ``command`` is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. Default: []
        :param command: (experimental) Entrypoint array. Not executed within a shell. The docker image's ENTRYPOINT is used if this is not provided. Variable references $(VAR_NAME) are expanded using the container's environment. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Cannot be updated. More info: https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#running-a-command-in-a-shell Default: - The docker image's ENTRYPOINT.
        :param env: (experimental) List of environment variables to set in the container. Cannot be updated. Default: - No environment variables.
        :param image_pull_policy: (experimental) Image pull policy for this container. Default: ImagePullPolicy.ALWAYS
        :param liveness: (experimental) Periodic probe of container liveness. Container will be restarted if the probe fails. Default: - no liveness probe is defined
        :param name: (experimental) Name of the container specified as a DNS_LABEL. Each container in a pod must have a unique name (DNS_LABEL). Cannot be updated. Default: 'main'
        :param port: (experimental) Number of port to expose on the pod's IP address. This must be a valid port number, 0 < x < 65536. Default: - No port is exposed.
        :param readiness: (experimental) Determines when the container is ready to serve traffic. Default: - no readiness probe is defined
        :param startup: (experimental) StartupProbe indicates that the Pod has successfully initialized. If specified, no other probes are executed until this completes successfully Default: - no startup probe is defined.
        :param volume_mounts: (experimental) Pod volumes to mount into the container's filesystem. Cannot be updated.
        :param working_dir: (experimental) Container's working directory. If not specified, the container runtime's default will be used, which might be configured in the container image. Cannot be updated. Default: - The container runtime's default.

        :stability: experimental
        '''
        container = ContainerProps(
            image=image,
            args=args,
            command=command,
            env=env,
            image_pull_policy=image_pull_policy,
            liveness=liveness,
            name=name,
            port=port,
            readiness=readiness,
            startup=startup,
            volume_mounts=volume_mounts,
            working_dir=working_dir,
        )

        return typing.cast(Container, jsii.invoke(self, "addContainer", [container]))

    @jsii.member(jsii_name="addVolume")
    def add_volume(self, volume: Volume) -> None:
        '''(experimental) Add a volume to the pod.

        :param volume: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addVolume", [volume]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containers")
    def containers(self) -> typing.List[Container]:
        '''(experimental) The containers belonging to the pod.

        Use ``addContainer`` to add containers.

        :stability: experimental
        '''
        return typing.cast(typing.List[Container], jsii.get(self, "containers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List[Volume]:
        '''(experimental) The volumes associated with this pod.

        Use ``addVolume`` to add volumes.

        :stability: experimental
        '''
        return typing.cast(typing.List[Volume], jsii.get(self, "volumes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[RestartPolicy], jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccount")
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) The service account used to run this pod.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IServiceAccount], jsii.get(self, "serviceAccount"))


@jsii.data_type(
    jsii_type="cdk8s-plus-17.PodProps",
    jsii_struct_bases=[ResourceProps, PodSpecProps],
    name_mapping={
        "metadata": "metadata",
        "containers": "containers",
        "restart_policy": "restartPolicy",
        "service_account": "serviceAccount",
        "volumes": "volumes",
    },
)
class PodProps(ResourceProps, PodSpecProps):
    def __init__(
        self,
        *,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
        containers: typing.Optional[typing.List[ContainerProps]] = None,
        restart_policy: typing.Optional[RestartPolicy] = None,
        service_account: typing.Optional[IServiceAccount] = None,
        volumes: typing.Optional[typing.List[Volume]] = None,
    ) -> None:
        '''(experimental) Properties for initialization of ``Pod``.

        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.
        :param containers: (experimental) List of containers belonging to the pod. Containers cannot currently be added or removed. There must be at least one container in a Pod. You can add additionnal containers using ``podSpec.addContainer()`` Default: - No containers. Note that a pod spec must include at least one container.
        :param restart_policy: (experimental) Restart policy for all containers within the pod. Default: RestartPolicy.ALWAYS
        :param service_account: (experimental) A service account provides an identity for processes that run in a Pod. When you (a human) access the cluster (for example, using kubectl), you are authenticated by the apiserver as a particular User Account (currently this is usually admin, unless your cluster administrator has customized your cluster). Processes in containers inside pods can also contact the apiserver. When they do, they are authenticated as a particular Service Account (for example, default). Default: - No service account.
        :param volumes: (experimental) List of volumes that can be mounted by containers belonging to the pod. You can also add volumes later using ``podSpec.addVolume()`` Default: - No volumes.

        :stability: experimental
        '''
        if isinstance(metadata, dict):
            metadata = cdk8s.ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {}
        if metadata is not None:
            self._values["metadata"] = metadata
        if containers is not None:
            self._values["containers"] = containers
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if service_account is not None:
            self._values["service_account"] = service_account
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def metadata(self) -> typing.Optional[cdk8s.ApiObjectMetadata]:
        '''(experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[cdk8s.ApiObjectMetadata], result)

    @builtins.property
    def containers(self) -> typing.Optional[typing.List[ContainerProps]]:
        '''(experimental) List of containers belonging to the pod.

        Containers cannot currently be
        added or removed. There must be at least one container in a Pod.

        You can add additionnal containers using ``podSpec.addContainer()``

        :default: - No containers. Note that a pod spec must include at least one container.

        :stability: experimental
        '''
        result = self._values.get("containers")
        return typing.cast(typing.Optional[typing.List[ContainerProps]], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional[RestartPolicy]:
        '''(experimental) Restart policy for all containers within the pod.

        :default: RestartPolicy.ALWAYS

        :see: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#restart-policy
        :stability: experimental
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional[RestartPolicy], result)

    @builtins.property
    def service_account(self) -> typing.Optional[IServiceAccount]:
        '''(experimental) A service account provides an identity for processes that run in a Pod.

        When you (a human) access the cluster (for example, using kubectl), you are
        authenticated by the apiserver as a particular User Account (currently this
        is usually admin, unless your cluster administrator has customized your
        cluster). Processes in containers inside pods can also contact the
        apiserver. When they do, they are authenticated as a particular Service
        Account (for example, default).

        :default: - No service account.

        :see: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
        :stability: experimental
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[IServiceAccount], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[Volume]]:
        '''(experimental) List of volumes that can be mounted by containers belonging to the pod.

        You can also add volumes later using ``podSpec.addVolume()``

        :default: - No volumes.

        :see: https://kubernetes.io/docs/concepts/storage/volumes
        :stability: experimental
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[Volume]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PodProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-plus-17.ServicePort",
    jsii_struct_bases=[ServicePortOptions],
    name_mapping={
        "name": "name",
        "node_port": "nodePort",
        "protocol": "protocol",
        "target_port": "targetPort",
        "port": "port",
    },
)
class ServicePort(ServicePortOptions):
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        node_port: typing.Optional[jsii.Number] = None,
        protocol: typing.Optional[Protocol] = None,
        target_port: typing.Optional[jsii.Number] = None,
        port: jsii.Number,
    ) -> None:
        '''(experimental) Definition of a service port.

        :param name: (experimental) The name of this port within the service. This must be a DNS_LABEL. All ports within a ServiceSpec must have unique names. This maps to the 'Name' field in EndpointPort objects. Optional if only one ServicePort is defined on this service.
        :param node_port: (experimental) The port on each node on which this service is exposed when type=NodePort or LoadBalancer. Usually assigned by the system. If specified, it will be allocated to the service if unused or else creation of the service will fail. Default is to auto-allocate a port if the ServiceType of this Service requires one. Default: to auto-allocate a port if the ServiceType of this Service requires one.
        :param protocol: (experimental) The IP protocol for this port. Supports "TCP", "UDP", and "SCTP". Default is TCP. Default: Protocol.TCP
        :param target_port: (experimental) The port number the service will redirect to. Default: - The value of ``port`` will be used.
        :param port: (experimental) The port number the service will bind to.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "port": port,
        }
        if name is not None:
            self._values["name"] = name
        if node_port is not None:
            self._values["node_port"] = node_port
        if protocol is not None:
            self._values["protocol"] = protocol
        if target_port is not None:
            self._values["target_port"] = target_port

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of this port within the service.

        This must be a DNS_LABEL. All
        ports within a ServiceSpec must have unique names. This maps to the 'Name'
        field in EndpointPort objects. Optional if only one ServicePort is defined
        on this service.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port on each node on which this service is exposed when type=NodePort or LoadBalancer.

        Usually assigned by the system. If specified, it will be
        allocated to the service if unused or else creation of the service will
        fail. Default is to auto-allocate a port if the ServiceType of this Service
        requires one.

        :default:

        to auto-allocate a port if the ServiceType of this Service
        requires one.

        :see: https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport
        :stability: experimental
        '''
        result = self._values.get("node_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol(self) -> typing.Optional[Protocol]:
        '''(experimental) The IP protocol for this port.

        Supports "TCP", "UDP", and "SCTP". Default is TCP.

        :default: Protocol.TCP

        :stability: experimental
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[Protocol], result)

    @builtins.property
    def target_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port number the service will redirect to.

        :default: - The value of ``port`` will be used.

        :stability: experimental
        '''
        result = self._values.get("target_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''(experimental) The port number the service will bind to.

        :stability: experimental
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServicePort(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IConfigMap)
class ConfigMap(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdk8s-plus-17.ConfigMap"):
    '''(experimental) ConfigMap holds configuration data for pods to consume.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        binary_data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        metadata: typing.Optional[cdk8s.ApiObjectMetadata] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param binary_data: (experimental) BinaryData contains the binary data. Each key must consist of alphanumeric characters, '-', '_' or '.'. BinaryData can contain byte sequences that are not in the UTF-8 range. The keys stored in BinaryData must not overlap with the ones in the Data field, this is enforced during validation process. Using this field will require 1.10+ apiserver and kubelet. You can also add binary data using ``configMap.addBinaryData()``.
        :param data: (experimental) Data contains the configuration data. Each key must consist of alphanumeric characters, '-', '_' or '.'. Values with non-UTF-8 byte sequences must use the BinaryData field. The keys stored in Data must not overlap with the keys in the BinaryData field, this is enforced during validation process. You can also add data using ``configMap.addData()``.
        :param metadata: (experimental) Metadata that all persisted resources must have, which includes all objects users must create.

        :stability: experimental
        '''
        props = ConfigMapProps(binary_data=binary_data, data=data, metadata=metadata)

        jsii.create(ConfigMap, self, [scope, id, props])

    @jsii.member(jsii_name="fromConfigMapName") # type: ignore[misc]
    @builtins.classmethod
    def from_config_map_name(cls, name: builtins.str) -> IConfigMap:
        '''(experimental) Represents a ConfigMap created elsewhere.

        :param name: The name of the config map to import.

        :stability: experimental
        '''
        return typing.cast(IConfigMap, jsii.sinvoke(cls, "fromConfigMapName", [name]))

    @jsii.member(jsii_name="addBinaryData")
    def add_binary_data(self, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Adds a binary data entry to the config map.

        BinaryData can contain byte
        sequences that are not in the UTF-8 range.

        :param key: The key.
        :param value: The value.

        :stability: experimental
        :throws: if there is either a ``data`` or ``binaryData`` entry with the same key
        '''
        return typing.cast(None, jsii.invoke(self, "addBinaryData", [key, value]))

    @jsii.member(jsii_name="addData")
    def add_data(self, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Adds a data entry to the config map.

        :param key: The key.
        :param value: The value.

        :stability: experimental
        :throws: if there is either a ``data`` or ``binaryData`` entry with the same key
        '''
        return typing.cast(None, jsii.invoke(self, "addData", [key, value]))

    @jsii.member(jsii_name="addDirectory")
    def add_directory(
        self,
        local_dir: builtins.str,
        *,
        exclude: typing.Optional[typing.List[builtins.str]] = None,
        key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a directory to the ConfigMap.

        :param local_dir: A path to a local directory.
        :param exclude: (experimental) Glob patterns to exclude when adding files. Default: - include all files
        :param key_prefix: (experimental) A prefix to add to all keys in the config map. Default: ""

        :stability: experimental
        '''
        options = AddDirectoryOptions(exclude=exclude, key_prefix=key_prefix)

        return typing.cast(None, jsii.invoke(self, "addDirectory", [local_dir, options]))

    @jsii.member(jsii_name="addFile")
    def add_file(
        self,
        local_file: builtins.str,
        key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a file to the ConfigMap.

        :param local_file: The path to the local file.
        :param key: The ConfigMap key (default to the file name).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addFile", [local_file, key]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObject")
    def _api_object(self) -> cdk8s.ApiObject:
        '''(experimental) The underlying cdk8s API object.

        :see: base.Resource.apiObject
        :stability: experimental
        '''
        return typing.cast(cdk8s.ApiObject, jsii.get(self, "apiObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="binaryData")
    def binary_data(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The binary data associated with this config map.

        Returns a copy. To add data records, use ``addBinaryData()`` or ``addData()``.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "binaryData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The data associated with this config map.

        Returns an copy. To add data records, use ``addData()`` or ``addBinaryData()``.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "data"))


__all__ = [
    "AddDirectoryOptions",
    "CommandProbeOptions",
    "ConfigMap",
    "ConfigMapProps",
    "ConfigMapVolumeOptions",
    "Container",
    "ContainerProps",
    "Deployment",
    "DeploymentProps",
    "EmptyDirMedium",
    "EmptyDirVolumeOptions",
    "EnvValue",
    "EnvValueFromConfigMapOptions",
    "EnvValueFromProcessOptions",
    "EnvValueFromSecretOptions",
    "ExposeOptions",
    "HttpGetProbeOptions",
    "IConfigMap",
    "IPodSpec",
    "IPodTemplate",
    "IResource",
    "ISecret",
    "IServiceAccount",
    "ImagePullPolicy",
    "IngressV1Beta1",
    "IngressV1Beta1Backend",
    "IngressV1Beta1Props",
    "IngressV1Beta1Rule",
    "Job",
    "JobProps",
    "MountOptions",
    "MountPropagation",
    "PathMapping",
    "Pod",
    "PodManagementPolicy",
    "PodProps",
    "PodSpec",
    "PodSpecProps",
    "PodTemplate",
    "PodTemplateProps",
    "Probe",
    "ProbeOptions",
    "Protocol",
    "Resource",
    "ResourceProps",
    "RestartPolicy",
    "Secret",
    "SecretProps",
    "SecretValue",
    "Service",
    "ServiceAccount",
    "ServiceAccountProps",
    "ServiceIngressV1BetaBackendOptions",
    "ServicePort",
    "ServicePortOptions",
    "ServiceProps",
    "ServiceType",
    "StatefulSet",
    "StatefulSetProps",
    "Volume",
    "VolumeMount",
]

publication.publish()
