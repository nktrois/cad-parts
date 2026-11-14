# CPU cooler bracket

*English · [Français](README.fr.md)*

A bar that runs through the 14 mm channel of the cooler and hooks onto the two retention lugs of the motherboard, pressing the heatsink onto the CPU.

Made for an **ASRock FM2A88M Extreme4+ R2.0** motherboard (AMD socket FM2+). Other boards using the same AMD retention lugs should work after adjusting the dimensions below.

## Printing

- PETG, 0.2 mm layers, 5 perimeters, 100 % infill
- The STL is already oriented on its edge, with supports under the bar

## Settings

Everything is at the top of the `.scad`:

- `ecart`: distance between the inner faces of the two loops
- `appui`: height between the underside of the lugs and the bearing surface on the cooler; this sets the clamping force
- `fenetre_l`, `fenetre_h`: openings for the lugs
- `a_plat = true` to view the part in its mounted position

Fix dimensions in the source rather than scaling in the slicer.

## Status

Works on my setup. PETG can relax over time next to a hot heatsink: check the clamping now and then. A spring-steel clip remains more reliable in the long run.
