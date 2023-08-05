# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union
from . import _utilities, _tables
from . import outputs
from ._inputs import *

__all__ = ['DatabaseFirewall']


class DatabaseFirewall(pulumi.CustomResource):
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 rules: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatabaseFirewallRuleArgs']]]]] = None,
                 __props__=None,
                 __name__=None,
                 __opts__=None):
        """
        Provides a DigitalOcean database firewall resource allowing you to restrict
        connections to your database to trusted sources. You may limit connections to
        specific Droplets, Kubernetes clusters, or IP addresses.

        ## Example Usage
        ### Create a new database firewall allowing multiple IP addresses

        ```python
        import pulumi
        import pulumi_digitalocean as digitalocean

        postgres_example = digitalocean.DatabaseCluster("postgres-example",
            engine="pg",
            version="11",
            size="db-s-1vcpu-1gb",
            region="nyc1",
            node_count=1)
        example_fw = digitalocean.DatabaseFirewall("example-fw",
            cluster_id=postgres_example.id,
            rules=[
                digitalocean.DatabaseFirewallRuleArgs(
                    type="ip_addr",
                    value="192.168.1.1",
                ),
                digitalocean.DatabaseFirewallRuleArgs(
                    type="ip_addr",
                    value="192.0.2.0",
                ),
            ])
        ```
        ### Create a new database firewall allowing a Droplet

        ```python
        import pulumi
        import pulumi_digitalocean as digitalocean

        web = digitalocean.Droplet("web",
            size="s-1vcpu-1gb",
            image="centos-7-x64",
            region="nyc3")
        postgres_example = digitalocean.DatabaseCluster("postgres-example",
            engine="pg",
            version="11",
            size="db-s-1vcpu-1gb",
            region="nyc1",
            node_count=1)
        example_fw = digitalocean.DatabaseFirewall("example-fw",
            cluster_id=postgres_example.id,
            rules=[digitalocean.DatabaseFirewallRuleArgs(
                type="droplet",
                value=web.id,
            )])
        ```

        ## Import

        Database firewalls can be imported using the `id` of the target database cluster For example

        ```sh
         $ pulumi import digitalocean:index:DatabaseFirewall example-fw 5f55c6cd-863b-4907-99b8-7e09b0275d54
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cluster_id: The ID of the target database cluster.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatabaseFirewallRuleArgs']]]] rules: A rule specifying a resource allowed to access the database cluster. The following arguments must be specified:
        """
        if __name__ is not None:
            warnings.warn("explicit use of __name__ is deprecated", DeprecationWarning)
            resource_name = __name__
        if __opts__ is not None:
            warnings.warn("explicit use of __opts__ is deprecated, use 'opts' instead", DeprecationWarning)
            opts = __opts__
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = dict()

            if cluster_id is None and not opts.urn:
                raise TypeError("Missing required property 'cluster_id'")
            __props__['cluster_id'] = cluster_id
            if rules is None and not opts.urn:
                raise TypeError("Missing required property 'rules'")
            __props__['rules'] = rules
        super(DatabaseFirewall, __self__).__init__(
            'digitalocean:index:DatabaseFirewall',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            cluster_id: Optional[pulumi.Input[str]] = None,
            rules: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatabaseFirewallRuleArgs']]]]] = None) -> 'DatabaseFirewall':
        """
        Get an existing DatabaseFirewall resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cluster_id: The ID of the target database cluster.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DatabaseFirewallRuleArgs']]]] rules: A rule specifying a resource allowed to access the database cluster. The following arguments must be specified:
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = dict()

        __props__["cluster_id"] = cluster_id
        __props__["rules"] = rules
        return DatabaseFirewall(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Output[str]:
        """
        The ID of the target database cluster.
        """
        return pulumi.get(self, "cluster_id")

    @property
    @pulumi.getter
    def rules(self) -> pulumi.Output[Sequence['outputs.DatabaseFirewallRule']]:
        """
        A rule specifying a resource allowed to access the database cluster. The following arguments must be specified:
        """
        return pulumi.get(self, "rules")

    def translate_output_property(self, prop):
        return _tables.CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return _tables.SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

