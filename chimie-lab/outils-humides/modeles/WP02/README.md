# WP02 — Perforated manual stirring paddle

*English · [Français](README.fr.md)*

![STL preview](preview.jpg)

## Files

- [WP02.stl](WP02.stl): printable mesh in millimetres.
- [WP02.step](WP02.step): CAD exchange solid.
- [WP02.FCStd](WP02.FCStd): native FreeCAD solid and metadata.
- [source.json](source.json): dimensions and source references.

Envelope: **175 × 40 × 4 mm**. Detailed interface notes are available in the [French notice](README.fr.md).

## Printing

Material candidate: **PP**, selected for the actual use. See the [printing guide](../../../IMPRESSION.md) for orientation and fit checks. No slicer profile or G-code is included.

## Settings

[FreeCAD generator](../../scripts/build_freecad.py). Edit the generator dimensions (`P` for filtration, `SPECS` for the other series) and regenerate. The `source.json` file is a parameter reference; edit the listed generator inputs. FCStd files contain solids and metadata, without a sketch-based feature history.

## Status

Original digital prototype by **nktrois**, under [CC BY 4.0](../../../LICENSE). Numerically checked geometry; not physically printed or qualified for leak tightness, chemical exposure, heating or vacuum service. Check the exact material grade and intended conditions before use.

[Collection](../../../README.md) · [Illustrated catalogue](../../../CATALOGUE.md)
