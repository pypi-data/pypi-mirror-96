# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union
from . import _utilities, _tables

__all__ = ['VolumeSnapshot']


class VolumeSnapshot(pulumi.CustomResource):
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 volume_id: Optional[pulumi.Input[str]] = None,
                 __props__=None,
                 __name__=None,
                 __opts__=None):
        """
        Provides a DigitalOcean Volume Snapshot which can be used to create a snapshot from an existing volume.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_digitalocean as digitalocean

        foobar_volume = digitalocean.Volume("foobarVolume",
            region="nyc1",
            size=100,
            description="an example volume")
        foobar_volume_snapshot = digitalocean.VolumeSnapshot("foobarVolumeSnapshot", volume_id=foobar_volume.id)
        ```

        ## Import

        Volume Snapshots can be imported using the `snapshot id`, e.g.

        ```sh
         $ pulumi import digitalocean:index/volumeSnapshot:VolumeSnapshot snapshot 506f78a4-e098-11e5-ad9f-000f53306ae1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] name: A name for the volume snapshot.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of the tags to be applied to this volume snapshot.
        :param pulumi.Input[str] volume_id: The ID of the volume from which the volume snapshot originated.
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

            __props__['name'] = name
            __props__['tags'] = tags
            if volume_id is None and not opts.urn:
                raise TypeError("Missing required property 'volume_id'")
            __props__['volume_id'] = volume_id
            __props__['created_at'] = None
            __props__['min_disk_size'] = None
            __props__['regions'] = None
            __props__['size'] = None
        super(VolumeSnapshot, __self__).__init__(
            'digitalocean:index/volumeSnapshot:VolumeSnapshot',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            created_at: Optional[pulumi.Input[str]] = None,
            min_disk_size: Optional[pulumi.Input[int]] = None,
            name: Optional[pulumi.Input[str]] = None,
            regions: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            size: Optional[pulumi.Input[float]] = None,
            tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            volume_id: Optional[pulumi.Input[str]] = None) -> 'VolumeSnapshot':
        """
        Get an existing VolumeSnapshot resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] created_at: The date and time the volume snapshot was created.
        :param pulumi.Input[int] min_disk_size: The minimum size in gigabytes required for a volume to be created based on this volume snapshot.
        :param pulumi.Input[str] name: A name for the volume snapshot.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] regions: A list of DigitalOcean region "slugs" indicating where the volume snapshot is available.
        :param pulumi.Input[float] size: The billable size of the volume snapshot in gigabytes.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of the tags to be applied to this volume snapshot.
        :param pulumi.Input[str] volume_id: The ID of the volume from which the volume snapshot originated.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = dict()

        __props__["created_at"] = created_at
        __props__["min_disk_size"] = min_disk_size
        __props__["name"] = name
        __props__["regions"] = regions
        __props__["size"] = size
        __props__["tags"] = tags
        __props__["volume_id"] = volume_id
        return VolumeSnapshot(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="createdAt")
    def created_at(self) -> pulumi.Output[str]:
        """
        The date and time the volume snapshot was created.
        """
        return pulumi.get(self, "created_at")

    @property
    @pulumi.getter(name="minDiskSize")
    def min_disk_size(self) -> pulumi.Output[int]:
        """
        The minimum size in gigabytes required for a volume to be created based on this volume snapshot.
        """
        return pulumi.get(self, "min_disk_size")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A name for the volume snapshot.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def regions(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of DigitalOcean region "slugs" indicating where the volume snapshot is available.
        """
        return pulumi.get(self, "regions")

    @property
    @pulumi.getter
    def size(self) -> pulumi.Output[float]:
        """
        The billable size of the volume snapshot in gigabytes.
        """
        return pulumi.get(self, "size")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A list of the tags to be applied to this volume snapshot.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="volumeId")
    def volume_id(self) -> pulumi.Output[str]:
        """
        The ID of the volume from which the volume snapshot originated.
        """
        return pulumi.get(self, "volume_id")

    def translate_output_property(self, prop):
        return _tables.CAMEL_TO_SNAKE_CASE_TABLE.get(prop) or prop

    def translate_input_property(self, prop):
        return _tables.SNAKE_TO_CAMEL_CASE_TABLE.get(prop) or prop

