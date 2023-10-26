from appclasses import Manifest, ManifestArgs, ServicePortConfigArgs

application_args = ManifestArgs(image="harbor-mage",
                                namespace='test2',
                                replicas=2,
                                service_enabled=True,
                                service_ports=[
                                    ServicePortConfigArgs(port=20, protocol='TCP', target_port=20, name='grdfaefqwpc'),
                                    ServicePortConfigArgs(port=10, protocol='UDP', target_port=30, name='htqddwsdqtp')]
                                )

app = Manifest('example', application_args)
