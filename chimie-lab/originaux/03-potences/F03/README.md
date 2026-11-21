# F03 — Ø35 funnel support arm

*English · [Français](README.fr.md)*

![STL preview](preview.jpg)

## Files

- [F03.stl](F03.stl): printable mesh in millimetres.
- [F03.step](F03.step): CAD exchange solid.
- [F03.FCStd](F03.FCStd): native FreeCAD solid and metadata.
- [source.json](source.json): dimensions and source references.

Envelope: **129.5 × 48.979 × 8 mm**. Detailed interface notes are available in the [French notice](README.fr.md).

## Printing

Material candidate: **PETG**, selected for the actual use. See the [printing guide](../../../IMPRESSION.md) for orientation and fit checks. No slicer profile or G-code is included.

## Settings

[FreeCAD generator](../../../scripts/build_freecad.py). Edit this part's entry in [catalogue-base.json](../../../catalogue-base.json) and regenerate. The `source.json` file is a parameter reference; edit the listed generator inputs. FCStd files contain solids and metadata, without a sketch-based feature history.

## Status

Original digital prototype by **nktrois**, under [CC BY 4.0](../../../LICENSE). Numerically checked geometry; not physically printed or qualified for leak tightness, chemical exposure, heating or vacuum service. Check the exact material grade and intended conditions before use.

[Collection](../../../README.md) · [Illustrated catalogue](../../../CATALOGUE.md)
