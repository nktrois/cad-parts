"""Write bilingual per-part folders and indexes without modifying CAD geometry."""
from pathlib import Path
import json,os
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
TITLES="""R01|18-position rack for Ø12 tubes
R02|18-position rack for Ø16 tubes
R03|12-position rack for Ø20 tubes
R04|10-position rack for 15 mL conical tubes
R05|8-position rack for 50 mL conical tubes
R06|24-position microtube rack
R07|12-position rack for Ø20 vials
R08|8-position rack for Ø28 vials
B01|Tray for four Ø32 bottles
B02|Tray for three Ø45 bottles
B03|Stand for a Ø65 bottle
B04|Stand for Ø90 glassware
F01|Light funnel stand base
F02|145 mm funnel stand column
F03|Ø35 funnel support arm
F04|Ø55 funnel support arm
P01|Pipette stand base
P02|190 mm pipette stand column
P03|Five-pipette support comb
D01|Drying rack for eight slides or plates
D02|Drying rack for six lids
D03|Rest for six glass rods
C01|Rack for twelve square cuvettes
C02|Ø90 open probe support plate
C03|Ø120 open probe support plate
T01|Organizer for six Ø6.6 hoses
T02|Organizer for six Ø8.6 hoses
T03|90-degree bend guide for Ø6.8 hose
T04|90-degree bend guide for Ø10.8 hose
O01|Rest for six spatulas
O02|Rest for three thermometers
O03|Three-compartment organizer
O04|Long storage tray
S01|Small Ø25 demonstration scoop
S02|Small Ø40 demonstration scoop
V01|Ø40 × 50 prototype cup
V02|Ø60 × 75 prototype cup
V03|Ø80 × 100 prototype cup
E01|Ø60 demonstration funnel
E02|Ø90 demonstration funnel
L01|Ø24 bottle-neck label
L02|Ø32 bottle-neck label
L03|Ø45 bottle-neck label
G01|4–20 mm diameter gauge
G02|Stand fit-test coupon
QB100|PP pouring beaker — nominal 100 mL
QB250|PP pouring beaker — nominal 250 mL
QB500|PP pouring beaker — nominal 500 mL
QB1000|PP pouring beaker — nominal 1000 mL
QC090|PP crystallizing dish — 90 mm inside diameter
QC140|PP crystallizing dish — 140 mm inside diameter
QF060|Ø60 PP liquid funnel
QF090|Ø90 PP liquid funnel
QP080|Ø80 PP powder funnel
QP110|Ø110 PP powder funnel
WB01|Open immersion bath
WB02|Perforated immersion basket
WB03|Immersible specimen holder
WF01|Removable gravity filter holder
WF02|Removable filter support grid
WP01|Pouring weigh boat
WP02|Perforated manual stirring paddle
WP03|Three-stage rinse block
FL01|Flanged lower filter collector
FL02|Upper filtration chamber
FL03|Ø55 filter-paper support disc
FL04|TPU flat filter gasket
FL05|TPU tapered stem-to-receiver seal
FL06|Removable cylindrical receiver
FL07|Receiver lid with open vent
FL08|Two-port lid for a trap prototype
FL09|TPU receiver lid gasket
FL10|Filtration station base
FL11|Foot for a Ø12 metal support rod
FL12|Filter flange support arm
FL13|Receiver cradle
FL14|External hose guide
FL15|Support-disc lifting hook
FL16|TPU stem fit-test coupon
FL17|Alternative open filter support disc"""
EN=dict(line.split("|",1) for line in TITLES.splitlines())
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text("\n".join(line.rstrip() for line in text.strip().splitlines())+"\n",encoding="utf-8",newline="\n")
def rel(folder,target):return Path(os.path.relpath(target,folder)).as_posix()
def bilingual(text,english):
    lines=text.strip().splitlines()
    if len(lines)>2 and ("[English]" in lines[2] or "[Français]" in lines[2]):lines=lines[:1]+lines[3:]
    return lines[0]+"\n\n"+("*English · [Français](README.fr.md)*" if english else "*[English](README.md) · Français*")+"\n"+"\n".join(lines[1:])
def french_existing(folder):
    path=folder/"README.fr.md"
    current=(folder/"README.md").read_text(encoding="utf-8")
    return path.read_text(encoding="utf-8") if path.exists() and "*English · [Français](README.fr.md)*" in current else current

def main():
    parts=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"))["parts"]
    assert len(parts)==len(EN)==80
    filcat=json.loads((ROOT/"filtration/catalogue.json").read_text(encoding="utf-8"))
    sources={"atelier":("scripts/build_freecad.py","catalogue-base.json"),
             "recipients":("recipients-chimiques/scripts/build_recipients_freecad.py",None),
             "humides":("outils-humides/scripts/build_freecad.py",None),
             "filtration":("filtration/scripts/build_system_freecad.py",None)}
    for p in parts:
        ident=p["id"];folder=ROOT/p["path"];back=rel(folder,ROOT)
        fr=french_existing(folder)
        fr=fr.replace(f"![Aperçu du STL]({back}/apercus/{ident}.png)","![Aperçu du STL](preview.jpg)")
        script,settings=sources[p["series"]]
        source=rel(folder,ROOT/script);setting=rel(folder,ROOT/settings) if settings else None
        if "## Sources et réglages" not in fr:
            fr+="\n\n## Sources et réglages\n\n"
            fr+=f"[Générateur FreeCAD]({source}) · [Paramètres de référence](source.json). "
            fr+=(f"Modifier la ligne de cette pièce dans [{settings}]({setting}), puis régénérer." if setting else "Modifier les dimensions dans le générateur (`P` pour la filtration, `SPECS` pour les autres séries), puis régénérer.")
            fr+=" Le fichier `source.json` est un relevé des paramètres ; le générateur utilise les sources indiquées. Les FCStd contiennent un solide et ses métadonnées, sans historique de fonctions esquissées."
        write(folder/"README.fr.md",bilingual(fr,False))
        candidate=p.get("material_candidate",p.get("material","PP")).split()[0]
        dims=" × ".join(f"{v:g}" for v in p["dimensions_mm"])
        text=f"""# {ident} — {EN[ident]}

![STL preview](preview.jpg)

## Files

- [{ident}.stl]({ident}.stl): printable mesh in millimetres.
- [{ident}.step]({ident}.step): CAD exchange solid.
- [{ident}.FCStd]({ident}.FCStd): native FreeCAD solid and metadata.
- [source.json](source.json): dimensions and source references.

Envelope: **{dims} mm**. Detailed interface notes are available in the [French notice](README.fr.md).

## Printing

Material candidate: **{candidate}**, selected for the actual use. See the [printing guide]({back}/IMPRESSION.md) for orientation and fit checks. No slicer profile or G-code is included.

## Settings

[FreeCAD generator]({source}). """
        text+=(f"Edit this part's entry in [{settings}]({setting}) and regenerate." if setting else "Edit the generator dimensions (`P` for filtration, `SPECS` for the other series) and regenerate.")
        text+=f""" The `source.json` file is a parameter reference; edit the listed generator inputs. FCStd files contain solids and metadata, without a sketch-based feature history.

## Status

Original digital prototype by **nktrois**, under [CC BY 4.0]({back}/LICENSE). Numerically checked geometry; not physically printed or qualified for leak tightness, chemical exposure, heating or vacuum service. Check the exact material grade and intended conditions before use.

[Collection]({back}/README.md) · [Illustrated catalogue]({back}/CATALOGUE.md)
"""
        if p["series"]=="filtration":text+=f" · [Filtration assembly]({back}/filtration/README.md)\n"
        write(folder/"README.md",bilingual(text,True))
        parameters=p.get("parameters",filcat["interfaces"] if p["series"]=="filtration" else {})
        write(folder/"source.json",json.dumps(dict(id=ident,title=EN[ident],generator=source,settings=setting,parameters_reference=parameters,dimensions_mm=p["dimensions_mm"],material_candidate=candidate,author="nktrois",license="CC-BY-4.0"),ensure_ascii=False,indent=2))
        image=Image.open(ROOT/"apercus"/(ident+".png")).convert("RGB");image.thumbnail((640,480));image.save(folder/"preview.jpg",quality=88)

    fr=french_existing(ROOT)
    fr=fr.replace(" Le conditionnement et les scripts restent locaux ; aucune publication GitHub n'est autorisée par la seule génération de ces fichiers.","")
    write(ROOT/"README.fr.md",bilingual(fr,False))
    overview="""# Chemistry and workshop — 80 original CAD models

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

## Files and settings

Each model folder contains its STL in millimetres, STEP, FCStd, `source.json`, `preview.jpg`, `README.md` and `README.fr.md`. Common generators remain under the relevant `scripts/` folder, linked from every notice. Parametric regeneration uses Python/JSON with FreeCAD. Native documents contain solids and metadata, without sketch-based feature histories.

See the [printing and regeneration guide](IMPRESSION.md) and the [material guide](recipients-chimiques/MATERIAUX.md). Technical documentation is in French.

## Verification and limits

All 80 meshes have closed, consistently oriented topology, one component and positive volume. STEP and FreeCAD readback confirms one valid solid per model. Each printable part fits within 240 mm on every axis; the largest dimension is 235 mm. [Mesh report](verification/mesh-report.json) · [CAD readback](verification/cad-readback.json).

These are digital prototypes. No physical printing, leak, chemical, thermal or vacuum tests have been performed. PP is a candidate for compatible wetted parts, PETG for dry supports, and TPU for compatible seals. Select the grade for the actual reagent, concentration, temperature and exposure time. No vacuum rating is assigned to the printed receiver or lids; initial filtration trials are gravity-fed with the vent open.

Original designs by **nktrois**, under [CC BY 4.0](LICENSE).
"""
    write(ROOT/"README.md",bilingual(overview,True))
    folder=ROOT/"filtration";fr=french_existing(folder)
    write(folder/"README.fr.md",bilingual(fr,False))
    english="""# Original filtration station — 17 parts

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
"""
    write(folder/"README.md",bilingual(english,True))

    # Folder indexes preserve the model-per-directory layout and existing paths.
    groups={ROOT/"originaux":[p for p in parts if p["series"]=="atelier"],ROOT/"recipients-chimiques":[p for p in parts if p["series"]=="recipients"],ROOT/"outils-humides":[p for p in parts if p["series"]=="humides"]}
    for p in parts:
        if p["series"]=="atelier":groups.setdefault((ROOT/p["path"]).parent,[]).append(p)
    for series in ("recipients-chimiques","outils-humides","filtration"):
        groups[ROOT/series/"modeles"]=[p for p in parts if p["path"].startswith(series+"/")]
    labels={"originaux":("Workshop and storage","Atelier et rangement"),"recipients-chimiques":("Open vessels","Récipients ouverts"),"outils-humides":("Immersion and preparation","Immersion et préparation"),"modeles":("Individual models","Modèles individuels")}
    for folder,rows in groups.items():
        title_en,title_fr=labels.get(folder.name,("Workshop parts — "+folder.name,"Pièces d'atelier — "+folder.name))
        for english,title,filename in [(True,title_en,"README.md"),(False,title_fr,"README.fr.md")]:
            text="# "+title+"\n\n"+("One directory per model, with STL, STEP, FreeCAD, source references and preview." if english else "Un dossier par modèle, avec STL, STEP, FreeCAD, références des sources et aperçu.")+"\n\n| ID | "+("Model" if english else "Modèle")+" |\n|---|---|\n"
            for p in rows:text+=f"| {p['id']} | [{EN[p['id']] if english else p['title']}]({rel(folder,ROOT/p['path'])}/{'README.md' if english else 'README.fr.md'}) |\n"
            text+=f"\n[{'Collection' if english else 'Bibliothèque'}]({rel(folder,ROOT)}/{'README.md' if english else 'README.fr.md'})\n"
            write(folder/filename,bilingual(text,english))
    html=ROOT/"catalogue.html"
    if html.exists():write(html,html.read_text(encoding="utf-8").replace(" Aucun push effectué.",""))
    print("ORGANIZED",len(parts),"part folders with STL/STEP/FCStd, EN/FR notices, preview and source references")
if __name__=="__main__":main()
