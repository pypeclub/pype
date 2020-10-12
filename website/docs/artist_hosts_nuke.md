---
id: artist_hosts_nuke
title: Nuke
sidebar_label: Nuke
---

:::important
After Nuke starts it will automatically **Apply All Settings** for you. If you are sure the settings are wrong just contact your supervisor and he will set them correctly for you in project database.
:::

:::tip Used elements terminology
For mode details about the element click on its name.

[asset](artist_concepts.md#asset) - In our context we usually mean **shot** and that is how we will call it bellow in the text (`shot01`).

[subset](artist_concepts.md#subset) - a clip on timeline which is part of a particular shot for example _foreground_, _main_, _background_, _reference_ (`shot01_main`)

[version](artist_concepts.md#version) - version of shot's subset (`shot01_main_v001`)

[representation](artist_concepts.md#representation) - file type of version (`shot01_main_v001.mov`)

[family](artist_concepts.md#family) - Publisher plugin filtering keyword, (if `ftrack` in family, publishing to Ftrack will be performed)

:::

## Pype global tools

-   [Set Context](artist_tools.md#set-context)
-   [Work Files](artist_tools.md#workfiles)
-   [Create](artist_tools.md#creator)
-   [Load](artist_tools.md#loader)
-   [Manage (Inventory)](artist_tools.md#inventory)
-   [Publish](artist_tools.md#publisher)
-   [Library Loader](artist_tools.md#library-loader)

## Nuke specific tools

### Set Frame Ranges

<div class="ImagePanel" data-image-align='right'>
<div class="ImagePanel.content">

Use this feature in case you are not sure the frame range is correct.

##### Result

-   setting Frame Range in script settings
-   setting Frame Range in viewers (timeline)

</div>
<div class="ImagePanel.image Screenshot">

![Set Frame Ranges](assets/nuke_setFrameRanges.png)

</div>
</div>

<div class="ImagePanel.image Screenshot">

<figure>

![Set Frame Ranges Timeline](assets/nuke_setFrameRanges_timeline.png)

<figcaption>

1.  limiting to Frame Range without handles
2.  **Input** handle on start
3.  **Output** handle on end

</figcaption>
</figure>

</div>

### Set Resolution

<div class="ImagePanel" data-image-align='right'>
<div class="ImagePanel.content">

This menu item will set correct resolution format for you defined by your production.

##### Result

-   creates new item in formats with project name
-   sets the new format as used

</div>
<div class="ImagePanel.image Screenshot">

![Set Resolution](assets/nuke_setResolution.png)

</div>
</div>

### Set Colorspace

<div class="ImagePanel" data-image-align='right'>
<div class="ImagePanel.content">

This menu item will set correct Colorspace definitions for you. All has to be configured by your production (Project coordinator).

##### Result

-   set Colorspace in your script settings
-   set preview LUT to your viewers

</div>
<div class="ImagePanel.image Screenshot">

![Set Colorspace](assets/nuke_setColorspace.png)

</div>
</div>

### Apply All Settings

<div class="ImagePanel" data-image-align='right'>
<div class="ImagePanel.content">

It is usually enough if you once per while use this option just to make yourself sure the workfile is having set correct properties.

##### Result

-   set Frame Ranges
-   set Colorspace
-   set Resolution

</div>
<div class="ImagePanel.image Screenshot">

![Apply All Settings](assets/nuke_applyAllSettings.png)

</div>
</div>

### Build First Work File

<div class="ImagePanel" data-image-align='right'>
<div class="ImagePanel.content">

This tool will create your first version of workfile and save it to correct folder with correct file name convention. It will look into database and get all last [versions](artist_concepts.md#version) of available [subsets](artist_concepts.md#subset).

</div>
<div class="ImagePanel.image Screenshot">

![Build First Work File](assets/nuke_buildFirstWorkfile.png)

</div>
</div>

##### Result

<div class="ImagePanel" data-image-align='left'>
<div class="ImagePanel.content">

-   adds all last versions of subsets (rendered image sequences) as read nodes
-   adds available color transformations under Read nodes
-   adds publishable write node as `renderMain` subset

</div>
<div class="ImagePanel.image Screenshot">

<figure>

![Set Frame Ranges Timeline](assets/nuke_autoBuild.png)

<figcaption>

Orange arrow is pointing at `Lut` groups.

</figcaption>
</figure>
</div>
</div>
