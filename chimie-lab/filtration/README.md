# Original filtration station — 17 parts

*English · [Français](README.fr.md)*

The filter, receiver and TPU seals were designed together. The cylindrical receiver is an original printed part, with a removable lid and cradle. The station uses a separate commercial Ø12 × 300 mm metal rod.

![Assembled station](../apercus/station-gravitaire.png)

The three seals are FL04 (flat filter gasket), FL05 (tapered stem-to-receiver seal) and FL09 (receiver lid gasket). FL16 is a TPU fit-test coupon. FL03 and FL17 are alternative paper-support discs; filter paper is a separate consumable.

[Assembly, interfaces and hardware list in French](README.fr.md) · [Printing guide](../IMPRESSION.md) · [All parts](../CATALOGUE.md)

## Status

Digital prototypes with numerical geometry and assembly checks only. Initial trials are gravity-fed, with an open vent. The receiver and two-port lid have no assigned vacuum rating: do not connect these unqualified printed bodies to a pump. Material compatibility, seal compression, leak tightness and stability need physical validation for the intended conditions.

![Non-printable explanatory section](../apercus/coupe-filtration.png)

## Sources

[Shared dimensions and generators](scripts/build_system_freecad.py) · [Assembly positions and checks](scripts/assemble_freecad.py) · [Interfaces and collision report](verification/assemblages.json).

The PLY files in `illustrations/` are non-printable sections for visualization. The printable parts are the catalogued STL files in `modeles/`.
