# QF090 — Ø90 PP liquid funnel

*English · [Français](README.fr.md)*

![STL preview](preview.jpg)

## Files

- [QF090.stl](QF090.stl): printable mesh in millimetres.
- [QF090.step](QF090.step): CAD exchange solid.
- [QF090.FCStd](QF090.FCStd): native FreeCAD solid and metadata.
- [source.json](source.json): dimensions and source references.

Envelope: **97.2 × 97.17 × 110 mm**. Detailed interface notes are available in the [French notice](README.fr.md).

## Printing

Material candidate: **PP**, selected for the actual use. See the [printing guide](../../../IMPRESSION.md) for orientation and fit checks. No slicer profile or G-code is included.

## Settings

[FreeCAD generator](../../scripts/build_recipients_freecad.py). Edit the generator dimensions (`P` for filtration, `SPECS` for the other series) and regenerate. The `source.json` file is a parameter reference; edit the listed generator inputs. FCStd files contain solids and metadata, without a sketch-based feature history.

## Status

Original digital prototype by **nktrois**, under [CC BY 4.0](../../../LICENSE). Initial release (21 November 2026): models checked digitally, before the first prints. Print feedback and test results will guide updates to dimensions, fits and printing settings. See the material and printing notes for the intended use.

[Collection](../../../README.md) · [Illustrated catalogue](../../../CATALOGUE.md)
