# -*- coding: utf-8 -*-
"""Submitting render job to Deadline."""
import os

import attr
import pyblish.api

import pype.lib.abstract_submit_deadline


@attr.s
class PluginInfo:
    """Plugin info structure for Harmony Deadline plugin."""

    SceneFile = attr.ib()
    # Harmony version
    Version = attr.ib()

    Camera = attr.ib(default="")
    FieldOfView = attr.ib(default=41.11)
    IsDatabase = attr.ib(default=False)
    ResolutionX = attr.ib(default=1920)
    ResolutionY = attr.ib(default=1080)

    # Resolution name preset, default
    UsingResPreset = attr.ib(default=False)
    ResolutionName = attr.ib(default="HDTV_1080p24")

    # --------------------------------------------------
    _outputNode = attr.ib(factory=list)

    @property
    def OutputNode(self):  # noqa: N802
        """Return all output nodes formatted for Deadline.

        Returns:
            dict: as `{'Output0Node', 'Top/renderFarmDefault'}`

        """
        out = {}
        for index, v in enumerate(self._outputNode):
            out["Output{}Node".format(index)] = v
        return out

    @OutputNode.setter
    def OutputNode(self, val):  # noqa: N802
        self._outputNode.append(val)

    # --------------------------------------------------
    _outputType = attr.ib(factory=list)

    @property
    def OutputType(self):  # noqa: N802
        """Return output nodes type formatted for Deadline.

        Returns:
            dict: as `{'Output0Type', 'Image'}`

        """
        out = {}
        for index, v in enumerate(self._outputType):
            out["Output{}Type".format(index)] = v
        return out

    @OutputType.setter
    def OutputType(self, val):  # noqa: N802
        self._outputType.append(val)

    # --------------------------------------------------
    _outputLeadingZero = attr.ib(factory=list)

    @property
    def OutputLeadingZero(self):  # noqa: N802
        """Return output nodes type formatted for Deadline.

        Returns:
            dict: as `{'Output0LeadingZero', '3'}`

        """
        out = {}
        for index, v in enumerate(self._outputLeadingZero):
            out["Output{}LeadingZero".format(index)] = v
        return out

    @OutputLeadingZero.setter
    def OutputLeadingZero(self, val):  # noqa: N802
        self._outputLeadingZero.append(val)

    # --------------------------------------------------
    _outputFormat = attr.ib(factory=list)

    @property
    def OutputFormat(self):  # noqa: N802
        """Return output nodes format formatted for Deadline.

        Returns:
            dict: as `{'Output0Type', 'PNG4'}`

        """
        out = {}
        for index, v in enumerate(self._outputFormat):
            out["Output{}Format".format(index)] = v
        return out

    @OutputFormat.setter
    def OutputFormat(self, val):  # noqa: N802
        self._outputFormat.append(val)

    # --------------------------------------------------
    _outputStartFrame = attr.ib(factory=list)

    @property
    def OutputStartFrame(self):  # noqa: N802
        """Return start frame for output nodes formatted for Deadline.

        Returns:
            dict: as `{'Output0StartFrame', '1'}`

        """
        out = {}
        for index, v in enumerate(self._outputStartFrame):
            out["Output{}StartFrame".format(index)] = v
        return out

    @OutputStartFrame.setter
    def OutputStartFrame(self, val):  # noqa: N802
        self._outputStartFrame.append(val)

    # --------------------------------------------------
    _outputPath = attr.ib(factory=list)

    @property
    def OutputPath(self):  # noqa: N802
        """Return output paths for nodes formatted for Deadline.

        Returns:
            dict: as `{'Output0Path', '/output/path'}`

        """
        out = {}
        for index, v in enumerate(self._outputPath):
            out["Output{}Path".format(index)] = v
        return out

    @OutputPath.setter
    def OutputPath(self, val):  # noqa: N802
        self._outputPath.append(val)

    def set_output(self, node, image_format, output,
                   output_type="Image", zeros=3, start_frame=1):
        """Helper to set output.

        This should be used instead of setting properties individually
        as so index remain consistent.

        Args:
            node (str): harmony write node name
            image_format (str): format of output (PNG4, TIF, ...)
            output (str): output path
            output_type (str, optional): "Image" or "Movie" (not supported).
            zeros (int, optional): Leading zeros (for 0001 = 3)
            start_frame (int, optional): Sequence offset.

        """

        self.OutputNode = node
        self.OutputFormat = image_format
        self.OutputPath = output
        self.OutputType = output_type
        self.OutputLeadingZero = zeros
        self.OutputStartFrame = start_frame


class HarmonySubmitDeadline(
        pype.lib.abstract_submit_deadline.AbstractSubmitDeadline):
    """Submit render write of Harmony scene to Deadline.

    Renders are submitted to a Deadline Web Service as
    supplied via the environment variable ``DEADLINE_REST_URL``.

    Note:
        If Deadline configuration is not detected, this plugin will
        be disabled.

    Attributes:
        use_published (bool): Use published scene to render instead of the
            one in work area.

    """

    label = "Submit to Deadline"
    order = pyblish.api.IntegratorOrder + 0.1
    hosts = ["harmony"]
    families = ["renderlayer"]
    if not os.environ.get("DEADLINE_REST_URL"):
        optional = False
        active = False
    else:
        optional = True

    use_published = True

    def get_job_info(self):
        pass

    def get_plugin_info(self):
        harmony_plugin_info = PluginInfo(
            SceneFile=self._instance.data["source"],
            Version=(
                self._instance.context.data["harmonyVersion"].split(".")[0]),
            FieldOfView=self._instance.context.data["FOV"],
            ResolutionX=self._instance.data["resolutionWidth"],
            ResolutionY=self._instance.data["resolutionHeight"]
        )
        """
        harmony_plugin_info.set_output(
            self._instance.context.data["setMembers"][0],
            self._instance.data["outputFormat"]
        )
        """
        return attr.asdict(harmony_plugin_info)
