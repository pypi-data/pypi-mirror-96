# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union
from . import _utilities, _tables

__all__ = ['Droplet']


class Droplet(pulumi.CustomResource):
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 backups: Optional[pulumi.Input[bool]] = None,
                 image: Optional[pulumi.Input[str]] = None,
                 ipv6: Optional[pulumi.Input[bool]] = None,
                 monitoring: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 private_networking: Optional[pulumi.Input[bool]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 resize_disk: Optional[pulumi.Input[bool]] = None,
                 size: Optional[pulumi.Input[str]] = None,
                 ssh_keys: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 user_data: Optional[pulumi.Input[str]] = None,
                 volume_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 vpc_uuid: Optional[pulumi.Input[str]] = None,
                 __props__=None,
                 __name__=None,
                 __opts__=None):
        """
        Provides a DigitalOcean Droplet resource. This can be used to create,
        modify, and delete Droplets.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_digitalocean as digitalocean

        # Create a new Web Droplet in the nyc2 region
        web = digitalocean.Droplet("web",
            image="ubuntu-18-04-x64",
            region="nyc2",
            size="s-1vcpu-1gb")
        ```

        ## Import

        Droplets can be imported using the Droplet `id`, e.g.

        ```sh
         $ pulumi import digitalocean:index/droplet:Droplet mydroplet 100823
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] backups: Boolean controlling if backups are made. Defaults to
               false.
        :param pulumi.Input[str] image: The Droplet image ID or slug.
        :param pulumi.Input[bool] ipv6: Boolean controlling if IPv6 is enabled. Defaults to false.
        :param pulumi.Input[bool] monitoring: Boolean controlling whether monitoring agent is installed.
               Defaults to false.
        :param pulumi.Input[str] name: The Droplet name.
        :param pulumi.Input[bool] private_networking: Boolean controlling if private networking
               is enabled. When VPC is enabled on an account, this will provision the
               Droplet inside of your account's default VPC for the region. Use the
               `vpc_uuid` attribute to specify a different VPC.
        :param pulumi.Input[str] region: The region to start in.
        :param pulumi.Input[bool] resize_disk: Boolean controlling whether to increase the disk
               size when resizing a Droplet. It defaults to `true`. When set to `false`,
               only the Droplet's RAM and CPU will be resized. **Increasing a Droplet's disk
               size is a permanent change**. Increasing only RAM and CPU is reversible.
        :param pulumi.Input[str] size: The unique slug that indentifies the type of Droplet. You can find a list of available slugs on [DigitalOcean API documentation](https://developers.digitalocean.com/documentation/v2/#list-all-sizes).
        :param pulumi.Input[Sequence[pulumi.Input[str]]] ssh_keys: A list of SSH IDs or fingerprints to enable in
               the format `[12345, 123456]`. To retrieve this info, use a tool such
               as `curl` with the [DigitalOcean API](https://developers.digitalocean.com/documentation/v2/#ssh-keys),
               to retrieve them.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of the tags to be applied to this Droplet.
        :param pulumi.Input[str] user_data: A string of the desired User Data for the Droplet.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] volume_ids: A list of the IDs of each block storage volume to be attached to the Droplet.
        :param pulumi.Input[str] vpc_uuid: The ID of the VPC where the Droplet will be located.
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

            __props__['backups'] = backups
            if image is None and not opts.urn:
                raise TypeError("Missing required property 'image'")
            __props__['image'] = image
            __props__['ipv6'] = ipv6
            __props__['monitoring'] = monitoring
            __props__['name'] = name
            __props__['private_networking'] = private_networking
            if region is None and not opts.urn:
                raise TypeError("Missing required property 'region'")
            __props__['region'] = region
            __props__['resize_disk'] = resize_disk
            if size is None and not opts.urn:
                raise TypeError("Missing required property 'size'")
            __props__['size'] = size
            __props__['ssh_keys'] = ssh_keys
            __props__['tags'] = tags
            __props__['user_data'] = user_data
            __props__['volume_ids'] = volume_ids
            __props__['vpc_uuid'] = vpc_uuid
            __props__['created_at'] = None
            __props__['disk'] = None
            __props__['droplet_urn'] = None
            __props__['ipv4_address'] = None
            __props__['ipv4_address_private'] = None
            __props__['ipv6_address'] = None
            __props__['locked'] = None
            __props__['memory'] = None
            __props__['price_hourly'] = None
            __props__['price_monthly'] = None
            __props__['status'] = None
            __props__['vcpus'] = None
        super(Droplet, __self__).__init__(
            'digitalocean:index/droplet:Droplet',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            backups: Optional[pulumi.Input[bool]] = None,
            created_at: Optional[pulumi.Input[str]] = None,
            disk: Optional[pulumi.Input[int]] = None,
            droplet_urn: Optional[pulumi.Input[str]] = None,
            image: Optional[pulumi.Input[str]] = None,
            ipv4_address: Optional[pulumi.Input[str]] = None,
            ipv4_address_private: Optional[pulumi.Input[str]] = None,
            ipv6: Optional[pulumi.Input[bool]] = None,
            ipv6_address: Optional[pulumi.Input[str]] = None,
            locked: Optional[pulumi.Input[bool]] = None,
            memory: Optional[pulumi.Input[int]] = None,
            monitoring: Optional[pulumi.Input[bool]] = None,
            name: Optional[pulumi.Input[str]] = None,
            price_hourly: Optional[pulumi.Input[float]] = None,
            price_monthly: Optional[pulumi.Input[float]] = None,
            private_networking: Optional[pulumi.Input[bool]] = None,
            region: Optional[pulumi.Input[str]] = None,
            resize_disk: Optional[pulumi.Input[bool]] = None,
            size: Optional[pulumi.Input[str]] = None,
            ssh_keys: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            status: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            user_data: Optional[pulumi.Input[str]] = None,
            vcpus: Optional[pulumi.Input[int]] = None,
            volume_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            vpc_uuid: Optional[pulumi.Input[str]] = None) -> 'Droplet':
        """
        Get an existing Droplet resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] backups: Boolean controlling if backups are made. Defaults to
               false.
        :param pulumi.Input[int] disk: The size of the instance's disk in GB
        :param pulumi.Input[str] droplet_urn: The uniform resource name of the Droplet
               * `name`- The name of the Droplet
        :param pulumi.Input[str] image: The Droplet image ID or slug.
        :param pulumi.Input[str] ipv4_address: The IPv4 address
        :param pulumi.Input[str] ipv4_address_private: The private networking IPv4 address
        :param pulumi.Input[bool] ipv6: Boolean controlling if IPv6 is enabled. Defaults to false.
        :param pulumi.Input[str] ipv6_address: The IPv6 address
        :param pulumi.Input[bool] locked: Is the Droplet locked
        :param pulumi.Input[bool] monitoring: Boolean controlling whether monitoring agent is installed.
               Defaults to false.
        :param pulumi.Input[str] name: The Droplet name.
        :param pulumi.Input[float] price_hourly: Droplet hourly price
        :param pulumi.Input[float] price_monthly: Droplet monthly price
        :param pulumi.Input[bool] private_networking: Boolean controlling if private networking
               is enabled. When VPC is enabled on an account, this will provision the
               Droplet inside of your account's default VPC for the region. Use the
               `vpc_uuid` attribute to specify a different VPC.
        :param pulumi.Input[str] region: The region to start in.
        :param pulumi.Input[bool] resize_disk: Boolean controlling whether to increase the disk
               size when resizing a Droplet. It defaults to `true`. When set to `false`,
               only the Droplet's RAM and CPU will be resized. **Increasing a Droplet's disk
               size is a permanent change**. Increasing only RAM and CPU is reversible.
        :param pulumi.Input[str] size: The unique slug that indentifies the type of Droplet. You can find a list of available slugs on [DigitalOcean API documentation](https://developers.digitalocean.com/documentation/v2/#list-all-sizes).
        :param pulumi.Input[Sequence[pulumi.Input[str]]] ssh_keys: A list of SSH IDs or fingerprints to enable in
               the format `[12345, 123456]`. To retrieve this info, use a tool such
               as `curl` with the [DigitalOcean API](https://developers.digitalocean.com/documentation/v2/#ssh-keys),
               to retrieve them.
        :param pulumi.Input[str] status: The status of the Droplet
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of the tags to be applied to this Droplet.
        :param pulumi.Input[str] user_data: A string of the desired User Data for the Droplet.
        :param pulumi.Input[int] vcpus: The number of the instance's virtual CPUs
        :param pulumi.Input[Sequence[pulumi.Input[str]]] volume_ids: A list of the IDs of each block storage volume to be attached to the Droplet.
        :param pulumi.Input[str] vpc_uuid: The ID of the VPC where the Droplet will be located.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = dict()

        __props__["backups"] = backups
        __props__["created_at"] = created_at
        __props__["disk"] = disk
        __props__["droplet_urn"] = droplet_urn
        __props__["image"] = image
        __props__["ipv4_address"] = ipv4_address
        __props__["ipv4_address_private"] = ipv4_address_private
        __props__["ipv6"] = ipv6
        __props__["ipv6_address"] = ipv6_address
        __props__["locked"] = locked
        __props__["memory"] = memory
        __props__["monitoring"] = monitoring
        __props__["name"] = name
        __props__["price_hourly"] = price_hourly
        __props__["price_monthly"] = price_monthly
        __props__["private_networking"] = private_networking
        __props__["region"] = region
        __props__["resize_disk"] = resize_disk
        __props__["size"] = size
        __props__["ssh_keys"] = ssh_keys
        __props__["status"] = status
        __props__["tags"] = tags
        __props__["user_data"] = user_data
        __props__["vcpus"] = vcpus
        __props__["volume_ids"] = volume_ids
        __props__["vpc_uuid"] = vpc_uuid
        return Droplet(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def backups(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean controlling if backups are made. Defaults to
        false.
        """
        return pulumi.get(self, "backups")

    @property
    @pulumi.getter(name="createdAt")
    def created_at(self) -> pulumi.Output[str]:
        return pulumi.get(self, "created_at")

    @property
    @pulumi.getter
    def disk(self) -> pulumi.Output[int]:
        """
        The size of the instance's disk in GB
        """
        return pulumi.get(self, "disk")

    @property
    @pulumi.getter(name="dropletUrn")
    def droplet_urn(self) -> pulumi.Output[str]:
        """
        The uniform resource name of the Droplet
        * `name`- The name of the Droplet
        """
        return pulumi.get(self, "droplet_urn")

    @property
    @pulumi.getter
    def image(self) -> pulumi.Output[str]:
        """
        The Droplet image ID or slug.
        """
        return pulumi.get(self, "image")

    @property
    @pulumi.getter(name="ipv4Address")
    def ipv4_address(self) -> pulumi.Output[str]:
        """
        The IPv4 address
        """
        return pulumi.get(self, "ipv4_address")

    @property
    @pulumi.getter(name="ipv4AddressPrivate")
    def ipv4_address_private(self) -> pulumi.Output[str]:
        """
        The private networking IPv4 address
        """
        return pulumi.get(self, "ipv4_address_private")

    @property
    @pulumi.getter
    def ipv6(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean controlling if IPv6 is enabled. Defaults to false.
        """
        return pulumi.get(self, "ipv6")

    @property
    @pulumi.getter(name="ipv6Address")
    def ipv6_address(self) -> pulumi.Output[str]:
        """
        The IPv6 address
        """
        return pulumi.get(self, "ipv6_address")

    @property
    @pulumi.getter
    def locked(self) -> pulumi.Output[bool]:
        """
        Is the Droplet locked
        """
        return pulumi.get(self, "locked")

    @property
    @pulumi.getter
    def memory(self) -> pulumi.Output[int]:
        return pulumi.get(self, "memory")

    @property
    @pulumi.getter
    def monitoring(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean controlling whether monitoring agent is installed.
        Defaults to false.
        """
        return pulumi.get(self, "monitoring")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The Droplet name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="priceHourly")
    def price_hourly(self) -> pulumi.Output[float]:
        """
        Droplet hourly price
        """
        return pulumi.get(self, "price_hourly")

    @property
    @pulumi.getter(name="priceMonthly")
    def price_monthly(self) -> pulumi.Output[float]:
        """
        Droplet monthly price
        """
        return pulumi.get(self, "price_monthly")

    @property
    @pulumi.getter(name="privateNetworking")
    def private_networking(self) -> pulumi.Output[bool]:
        """
        Boolean controlling if private networking
        is enabled. When VPC is enabled on an account, this will provision the
        Droplet inside of your account's default VPC for the region. Use the
        `vpc_uuid` attribute to specify a different VPC.
        """
        return pulumi.get(self, "private_networking")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region to start in.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="resizeDisk")
    def resize_disk(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean controlling whether to increase the disk
        size when resizing a Droplet. It defaults to `true`. When set to `false`,
        only the Droplet's RAM and CPU will be resized. **Increasing a Droplet's disk
        size is a permanent change**. Increasing only RAM and CPU is reversible.
        """
        return pulumi.get(self, "resize_disk")

    @property
    @pulumi.getter
    def size(self) -> pulumi.Output[str]:
        """
        The unique slug that indentifies the type of Droplet. You can find a list of available slugs on [DigitalOcean API documentation](https://developers.digitalocean.com/documentation/v2/#list-all-sizes).
        """
        return pulumi.get(self, "size")

    @property
    @pulumi.getter(name="sshKeys")
    def ssh_keys(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A list of SSH IDs or fingerprints to enable in
        the format `[12345, 123456]`. To retrieve this info, use a tool such
        as `curl` with the [DigitalOcean API](https://developers.digitalocean.com/documentation/v2/#ssh-keys),
        to retrieve them.
        """
        return pulumi.get(self, "ssh_keys")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        The status of the Droplet
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A list of the tags to be applied to this Droplet.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="userData")
    def user_data(self) -> pulumi.Output[Optional[str]]:
        """
        A string of the desired User Data for the Droplet.
        """
        return pulumi.get(self, "user_data")

    @property
    @pulumi.getter
    def vcpus(self) -> pulumi.Output[int]:
        """
        The number of the instance's virtual CPUs
        """
        return pulumi.get(self, "vcpus")

    @property
    @pulumi.getter(name="volumeIds")
    def volume_ids(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of the IDs of each block storage volume to be attached to the Droplet.
        """
        return pulumi.get(self, "volume_ids")

    @property
    @pulumi.getter(name="vpcUuid")
    def vpc_uuid(self) -> pulumi.Output[str]:
        """
        The ID of the VPC where the Droplet will be located.
        """
        return pulumi.get(self, "vpc_uuid")

    def translate_output_property(self, prop):
        return _tables.CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return _tables.SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

