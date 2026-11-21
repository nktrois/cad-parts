# QB250 — PP pouring beaker — nominal 250 mL

*English · [Français](README.fr.md)*

![STL preview](preview.jpg)

## Files

- [QB250.stl](QB250.stl): printable mesh in millimetres.
- [QB250.step](QB250.step): CAD exchange solid.
- [QB250.FCStd](QB250.FCStd): native FreeCAD solid and metadata.
- [source.json](source.json): dimensions and source references.

Envelope: **84.2 × 77.2 × 95 mm**. Detailed interface notes are available in the [French notice](README.fr.md).

## Printing

Material candidate: **PP**, selected for the actual use. See the [printing guide](../../../IMPRESSION.md) for orientation and fit checks. No slicer profile or G-code is included.

## Settings

[FreeCAD generator](../../scripts/build_recipients_freecad.py). Edit the generator dimensions (`P` for filtration, `SPECS` for the other series) and regenerate. The `source.json` file is a parameter reference; edit the listed generator inputs. FCStd files contain solids and metadata, without a sketch-based feature history.

## Status

Original digital prototype by **nktrois**, under [CC BY 4.0](../../../LICENSE). Initial release (21 November 2026): models checked digitally, before the first prints. Print feedback and test results will guide updates to dimensions, fits and printing settings. See the material and printing notes for the intended use.

[Collection](../../../README.md) · [Illustrated catalogue](../../../CATALOGUE.md)
