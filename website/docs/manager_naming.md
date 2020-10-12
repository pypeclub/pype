---
id: manager_naming
title: Naming Conventions
sidebar_label: Naming Conventions
---

:::note
This naming convention holds true for most of our pipeline. Please match it as close as possible even for projects and files that might be outside of pipeline scope at this point. Small errors count! The reason for given formatting is to allow people to understand the file at glance and that a script or a program can easily get meaningful information from your files without errors.
:::

## General rules

For more detailed rules and different file types, have a look at naming conventions for scenes and assets

-   Every file starts with file code based on a project it belongs to e.g. ‘tst_’, ‘drm_’
-   Optional subversion and comment always comes after the major version. v##.subversion_comment.
-   File names can only be composed of letters, numbers, underscores `_` and dots “.”
-   You can use snakeCase or CamelCase if you need more words in a section.  thisIsLongerSentenceInComment
-   No spaces in filenames. Ever!
-   Frame numbers are always separated by a period ”.”
-   If you're not sure use this template:

## Work files

**`{code}_{shot}_{task}_v001.ext`**

**`{code}_{asset}_{task}_v001.ext`**

**Examples:**

    prj_sh010_enviro_v001.ma
    prj_sh010_animation_v001.ma
    prj_sh010_comp_v001.nk

    prj_bob_modelling_v001.ma
    prj_bob_rigging_v001.ma
    prj_bob_lookdev_v001.ma

<div class="admonition info">
In all of the examples anything enclosed in curly brackets  { } is compulsory in the name.
Anything in square brackets [ ] is optional.
</div>

## Published Assets

**`{code}_{asset}_{family}_{variant}_{version}_[comment].ext`**

**Examples:**
  prj_bob_model_main_v01.ma
  prj_bob_model_hires_v01.ma
  prj_bob_model_main_v01_clothes.ma
  prj_bob_model_main_v01_body.ma
  prj_bob_rig_main_v01.ma
  Prj_bob_look_main_v01.ma
  Prj_bob_look_wet_v01.ma

## Published Textures

**`{code}_{asset}_{variant}_{part}_{map}_{version}.ext`**

**Examples:**
	prj_bob_main_body_diff.ma
	prj_bob_main_body_spec.ma
	prj_bob_main_body_opac.ma
	prj_bob_main_hair_density.ma
	prj_bob_main_hair_color.ma
	prj_bob_wet_body_spec.ma

### Key Reference

-   **code**:
    -   short code of the project. You can get this from Ftrack or ask the supervisor.
-   **entity**
    -   shot/asset name exactly as it is in Ftrack.
-   **task**
    -   task name exactly reflecting the task name from Ftrack.
-   **version**
    -   Version number. Always in the form of “v” and 2 or 3 digits.
-   **family**
    -   Type of the exported asset, such as: ‘geo’, ‘cache’, ‘rig’, ‘texture’.  Asset family doesn’t necessarily reflect the task that produced it, but rather what it actually contains.
-   **subset**
    -   specific variation of a give asset. This should be a descriptive name of the published asset. Most families have their default variants, but you can always specify your own. For example default variant for models is 'main', but you might need to use ‘hires’ or ‘proxy’ if these were created as well.
-   **part**
    -   If asset needs to be split to more parts during publishing, this is the name of each part.
-   **comment**
    -   Optional part of the name where artist can add any comments about the stage of work or whatever else might be needed. This part gets scrapped during publishing. e.g.: “retopo_finished”, “desing_test”
-   **map**
    -   What data is painted in the texture. Could be anything from standard ones like diffuse, specular, opacity to completely arbitrary data.
