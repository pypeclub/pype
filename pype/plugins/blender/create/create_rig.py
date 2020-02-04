"""Create a rig asset."""

import bpy

from avalon import api
from avalon.blender import Creator, lib


class CreateRig(Creator):
    """Artist-friendly rig with controls to direct motion"""

    name = "rigMain"
    label = "Rig"
    family = "rig"
    icon = "cube"

    def process(self):
        import pype.blender

        asset = self.data["asset"]
        subset = self.data["subset"]
        name = pype.blender.plugin.rig_name(asset, subset)
        collection = bpy.data.collections.new(name=name)
        bpy.context.scene.collection.children.link(collection)
        self.data['task'] = api.Session.get('AVALON_TASK')
        lib.imprint(collection, self.data)

        if (self.options or {}).get("useSelection"):
            for obj in lib.get_selection():
                collection.objects.link(obj)

        return collection
