# F04 — Ø55 funnel support arm

*English · [Français](README.fr.md)*

![STL preview](preview.jpg)

## Files

- [F04.stl](F04.stl): printable mesh in millimetres.
- [F04.step](F04.step): CAD exchange solid.
- [F04.FCStd](F04.FCStd): native FreeCAD solid and metadata.
- [source.json](source.json): dimensions and source references.

Envelope: **139.5 × 68.979 × 8 mm**. Detailed interface notes are available in the [French notice](README.fr.md).

## Printing

Material candidate: **PETG**, selected for the actual use. See the [printing guide](../../../IMPRESSION.md) for orientation and fit checks. No slicer profile or G-code is included.

## Settings

[FreeCAD generator](../../../scripts/build_freecad.py). Edit this part's entry in [catalogue-base.json](../../../catalogue-base.json) and regenerate. The `source.json` file is a parameter reference; edit the listed generator inputs. FCStd files contain solids and metadata, without a sketch-based feature history.

## Status

Original digital prototype by **nktrois**, under [CC BY 4.0](../../../LICENSE). Numerically checked geometry; not physically printed or qualified for leak tightness, chemical exposure, heating or vacuum service. Check the exact material grade and intended conditions before use.

[Collection](../../../README.md) · [Illustrated catalogue](../../../CATALOGUE.md)
