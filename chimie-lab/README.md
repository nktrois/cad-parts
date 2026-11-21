# Chemistry and workshop — 80 original CAD models

*English · [Français](README.fr.md)*

80 original parts with STL, STEP, native FreeCAD files and Python/JSON sources. Each part has its own folder, preview and English/French notices.

![Filtration station and section view](apercus/filtration-detail.jpg)

| Collection | Parts | Contents |
|---|---:|---|
| [Workshop and storage](originaux/) | 45 | Tube and bottle racks, stands, drying racks, hose guides, trays, scoops, labels and gauges |
| [Open vessels](recipients-chimiques/) | 10 | Pouring beakers, crystallizing dishes, liquid and powder funnels |
| [Immersion and preparation](outils-humides/) | 8 | Bath and basket, specimen holder, gravity filter, weigh boat, paddle and rinse block |
| [Filtration station](filtration/) | 17 | Collector, chamber, support discs, receiver, lids, three TPU seals and dry support parts |

[Illustrated catalogue](CATALOGUE.md) · [Offline searchable catalogue](catalogue.html) · [JSON](catalogue.json) · [CSV](catalogue.csv)

GitHub displays the Markdown catalogue. Download the collection and open `catalogue.html` locally to use its search and material filters.

## Materials

| Part type | Suggested material |
|---|---|
| Vessels and wetted filtration parts | PP |
| Dry stands, racks and organizers | PETG |
| Flexible seals | TPU |

Select the exact grade for the intended use; see the [material guide](recipients-chimiques/MATERIAUX.md) and each model's notes.

## Files and settings

Each model folder contains its STL in millimetres, STEP, FCStd, `source.json`, `preview.jpg`, `README.md` and `README.fr.md`. Common generators remain under the relevant `scripts/` folder, linked from every notice. Parametric regeneration uses Python/JSON with FreeCAD. Native documents contain solids and metadata, without sketch-based feature histories.

See the [printing and regeneration guide](IMPRESSION.md) and the [material guide](recipients-chimiques/MATERIAUX.md). Technical documentation is in French.

## Verification and limits

All 80 meshes have closed, consistently oriented topology, one component and positive volume. STEP and FreeCAD readback confirms one valid solid per model. Each printable part fits within 240 mm on every axis; the largest dimension is 235 mm. [Mesh report](verification/mesh-report.json) · [CAD readback](verification/cad-readback.json).

Initial release (21 November 2026): models checked digitally, before the first prints. Print feedback and test results will guide updates to dimensions, fits and printing settings. See the [filtration notes](filtration/README.md) for assembly and operating limits.

Original designs by **nktrois**, under [CC BY 4.0](LICENSE).
