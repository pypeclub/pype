# -*- coding: utf-8 -*-
"""Collect data to render from scene."""
import json

import pyblish.api
from avalon import harmony

from pype.lib.abstract_collect_render import (
    RenderInstance, AbstractCollectRender)


class CollectRender(AbstractCollectRender):
    """Gather all publishable renders."""

    def get_instances(self, context):

        version = None
        if self.sync_workfile_version:
            version = context.data["version"]

        instances = []
        for instance in context:
            nodes = harmony.send(
                {"function": "node.subNodes", "args": ["Top"]}
            )["result"]

            for node in nodes:
                data = harmony.read(node)

                # Skip non-tagged nodes.
                if not data:
                    continue

                # Skip containers.
                if "container" in data["id"]:
                    continue

                render_instance = RenderInstance(
                    version=version,
                    time=None,
                    source=None,
                    label=None,
                    subset=None,
                    asset=attr.ib(init=False)
                    attachTo=attr.ib(init=False)
                    setMembers=attr.ib()
                    publish=attr.ib()
                    review=attr.ib(default=False)
                    renderer=attr.ib()
                    priority=attr.ib(default=50)
                    name=attr.ib()

                    family=attr.ib(default="renderlayer")
                    families=attr.ib(default=["renderlayer"])

                    # format settings
                    resolutionWidth=attr.ib()
                    resolutionHeight=attr.ib()
                    pixelAspect=attr.ib()
                    multipartExr=attr.ib(default=False)
                    tileRendering=attr.ib()
                    tilesX=attr.ib()
                    tilesY=attr.ib()
                    convertToScanline=attr.ib(default=False)

                    # time settings
                    frameStart=attr.ib()
                    frameEnd=attr.ib()
                    frameStep=attr.ib()
                )
