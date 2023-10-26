import typing

import pulumi_kubernetes as kubernetes

from dataclasses import dataclass, field
from pulumi import ResourceOptions
from pulumi_kubernetes import Provider
from pulumi import ComponentResource
from typing import List, Sequence, Any


render_provider = Provider('k8s-yaml-renderer',
                           render_yaml_to_directory='yaml')


@dataclass
class ServicePortConfigArgs:
    name: str = 'http'
    port: int = 80
    target_port: int = 80
    protocol: str = 'TCP'

# @dataclass
# class ContainerPortConfigArgs:
#     name: str = 'http'
#     port: int = 80


@dataclass
class ManifestArgs:
    image: str = "core.harbor.k8s.devim.team/library/app-master"
    replicas: int = 1
    namespace: str = "apps"
    service_enabled: bool = True
    service_ports: Sequence[ServicePortConfigArgs] = field(default_factory=lambda: [ServicePortConfigArgs()])


class Manifest(ComponentResource):
    def __init__(self, name, args: ManifestArgs, opts: ResourceOptions = None):
        super().__init__("pulumi:modules:Deployments", name, None, opts)
        self.preparefields(args, name)
        self.createmanifest(name, args)

    def preparefields(self, args, name):
        self.deployment_metadata = kubernetes.meta.v1.ObjectMetaArgs(
            name=name,
            labels={"app": name},
            namespace=args.namespace
        )
        self.deployment_spec = kubernetes.apps.v1.DeploymentSpecArgs(
            replicas=args.replicas,
            selector=kubernetes.meta.v1.LabelSelectorArgs(
                match_labels={"app": name}),
            template=kubernetes.core.v1.PodTemplateSpecArgs(
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    labels={"app": name}),
                spec=kubernetes.core.v1.PodSpecArgs(
                    containers=[kubernetes.core.v1.ContainerArgs(
                        name=name,
                        image=args.image
                    )]
                )
            ))
        if args.service_enabled:
            self.service_metadata = kubernetes.meta.v1.ObjectMetaArgs(
                name=name,
                labels={"app": name},
                namespace=args.namespace)
            self.service_spec = kubernetes.core.v1.ServiceSpecArgs(
                ports=[kubernetes.core.v1.ServicePortArgs(name=port.name,
                                                          port=port.port,
                                                          target_port=port.target_port,
                                                          protocol=port.protocol)
                       for port in args.service_ports])

    def createmanifest(self, name, args):
        self.deployment = kubernetes.apps.v1.Deployment(resource_name=name, metadata=self.deployment_metadata,
                                                        spec=self.deployment_spec,
                                                        opts=ResourceOptions(provider=render_provider))
        if args.service_enabled:
            self.service = kubernetes.core.v1.Service(resource_name=name, metadata=self.service_metadata,
                                                      spec=self.service_spec,
                                                      opts=ResourceOptions(provider=render_provider))

