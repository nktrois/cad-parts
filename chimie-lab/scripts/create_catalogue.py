"""Create the explicit, editable specifications for the original lab parts."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PARTS = []


def add(ident, title, family, kind, params, usage, fit="", material="PETG", assembly=None):
    PARTS.append(dict(id=ident, title=title, family=family, kind=kind,
                      parameters=params, usage=usage, fit=fit, material=material,
                      assembly=assembly, license="CC-BY-4.0", author="nktrois",
                      support_status="A verifier au tranchage", physically_tested=False))


def rack(ident, title, diameter, nx, ny, pitch, height, usage):
    add(ident, title, "01-portoirs", "rack",
        dict(diameter=diameter, nx=nx, ny=ny, pitch=pitch, height=height,
             edge=7, bottom=4, drain=3.2), usage,
        f"Puits Ø {diameter} mm ; mesurer le diamètre extérieur du récipient.")


rack("R01", "Portoir 18 tubes Ø12", 12.6, 6, 3, 20, 34, "Ranger verticalement 18 tubes secs de diamètre extérieur voisin de 12 mm.")
rack("R02", "Portoir 18 tubes Ø16", 16.6, 6, 3, 24, 42, "Ranger 18 tubes secs de diamètre extérieur voisin de 16 mm.")
rack("R03", "Portoir 12 tubes Ø20", 20.7, 4, 3, 29, 44, "Ranger 12 tubes secs de diamètre extérieur voisin de 20 mm.")
rack("R04", "Portoir 10 tubes coniques 15 mL", 17.8, 5, 2, 26, 42, "Maintenir 10 tubes commerciaux de 15 mL au repos, hors centrifugeuse.")
rack("R05", "Portoir 8 tubes coniques 50 mL", 30.8, 4, 2, 39, 56, "Maintenir 8 tubes commerciaux de 50 mL au repos, hors centrifugeuse.")
rack("R06", "Portoir 24 microtubes", 11.6, 6, 4, 17, 23, "Ranger 24 microtubes commerciaux ; vérifier la géométrie de leur collerette.")
rack("R07", "Portoir 12 flacons Ø20", 20.8, 4, 3, 28, 27, "Organiser 12 flacons secs de petit diamètre.")
rack("R08", "Portoir 8 flacons Ø28", 28.8, 4, 2, 37, 32, "Organiser 8 flacons secs de diamètre extérieur voisin de 28 mm.")

for ident, title, dia, nx, ny, pitch in [
    ("B01", "Plateau 4 flacons Ø32", 33, 2, 2, 46),
    ("B02", "Plateau 3 flacons Ø45", 46, 3, 1, 60)]:
    add(ident, title, "02-flacons", "rack", dict(diameter=dia,nx=nx,ny=ny,pitch=pitch,height=20,edge=10,bottom=4,drain=3.2),
        "Positionner des flacons commerciaux fermés sur la paillasse ; ce plateau n'est pas un bac de rétention.", f"Logements Ø {dia} mm.")
for ident, title, dia in [("B03", "Socle flacon Ø65", 66), ("B04", "Socle verrerie Ø90", 91)]:
    add(ident, title, "02-flacons", "bottle_base", dict(diameter=dia,wall=4,bottom=5,ring_height=15,margin=18),
        "Positionner un récipient commercial à température ambiante ; aucune garantie contre le renversement.", f"Diamètre intérieur du collier : {dia} mm.")

add("F01", "Socle de potence légère", "03-potences", "stand_base", dict(length=160,width=110,height=11,socket=20.4,depth=8),
    "Socle pour le support léger d'entonnoir F02/F03/F04 ; pas une potence de laboratoire porteuse.", "Emboîtement carré 20,4 mm ; assemblage F01 + F02 + F03 ou F04.", assembly="potence-entonnoir")
add("F02", "Colonne de potence 145 mm", "03-potences", "stand_post", dict(side=20,height=145,bottom_tenon=19.9,top_tenon=15.9,tenon_height=8),
    "Colonne pour un petit entonnoir vide ou un accessoire léger, sans chauffe.", "Tenons 19,9 mm en bas et 15,9 mm en haut.", assembly="potence-entonnoir")
for ident, diameter in [("F03",35),("F04",55)]:
    add(ident, f"Bras porte-entonnoir Ø{diameter}", "03-potences", "funnel_arm", dict(diameter=diameter,wall=7,thickness=8,socket=16.4),
        "Maintenir un petit entonnoir commercial vide ; vérifier la stabilité avec le récipient récepteur avant tout usage.",
        f"Passage central Ø {diameter} mm ; montage sur le tenon supérieur de F02.", assembly="potence-entonnoir")

add("P01", "Socle porte-pipettes", "04-pipettes", "stand_base", dict(length=170,width=125,height=11,socket=20.4,depth=8,socket_x=85),
    "Base du porte-pipettes P01/P02/P03 ; rangement à sec uniquement.", "Assemblage P01 + P02 + P03.", assembly="porte-pipettes")
add("P02", "Colonne porte-pipettes 190 mm", "04-pipettes", "stand_post", dict(side=20,height=190,bottom_tenon=19.9,top_tenon=15.9,tenon_height=8),
    "Colonne du porte-pipettes, sans charge instrumentale lourde.", "Même interface que F02 ; hauteur totale 206 mm.", assembly="porte-pipettes")
add("P03", "Peigne 5 pipettes", "04-pipettes", "pipette_comb", dict(length=160,width=65,thickness=8,slot=10.5,slots=5,socket=16.4),
    "Suspendre 5 pipettes possédant un épaulement plus large que les encoches ; vérifier chaque pipette.",
    "Encoches ouvertes de 10,5 mm ; ne convient pas à toutes les marques.", assembly="porte-pipettes")

add("D01", "Égouttoir 8 lames ou plaques", "05-sechage", "drying_rack", dict(slots=8,gap=5,fin=3,length=90,height=24,base=4),
    "Sécher des lames, petites plaques ou accessoires déjà rincés à l'eau ; hors verrerie chaude.", "8 intervalles de 5 mm ; aucun contact avec des déchets chimiques dangereux.")
add("D02", "Égouttoir 6 couvercles", "05-sechage", "drying_rack", dict(slots=6,gap=15,fin=3,length=100,height=32,base=5),
    "Ranger ou égoutter 6 couvercles et verres de montre déjà rincés à l'eau.", "6 intervalles de 15 mm.")
add("D03", "Support 6 tiges de verre", "05-sechage", "rod_rest", dict(count=6,diameter=8.6,pitch=20,length=140,width=70,height=18),
    "Poser horizontalement des tiges de verre propres et froides.", "Gorges Ø 8,6 mm, entraxe 20 mm.")
add("C01", "Portoir 12 cuvettes carrées", "06-mesure", "square_rack", dict(nx=4,ny=3,side=13.6,pitch=22,height=22,bottom=4,edge=7,drain=3.2),
    "Ranger des cuvettes commerciales carrées ; éviter les faces optiques dans les manipulations.", "Logements carrés 13,6 mm, à ajuster à tes cuvettes.")
for ident, dia in [("C02",90),("C03",120)]:
    add(ident, f"Plaque ouverte porte-sondes Ø{dia}", "06-mesure", "probe_plate", dict(diameter=dia,thickness=5,holes=[6.5,8.5,12.5,4.5]),
        "Positionner des sondes sur un récipient à froid après vérification des dimensions et de la compatibilité ; plaque ouverte non étanche.",
        "Passages Ø 6,5 / 8,5 / 12,5 / 4,5 mm et évent central. Ne sert pas de fermeture sous pression.")

for ident, dia in [("T01",6.6),("T02",8.6)]:
    add(ident, f"Organiseur 6 tuyaux Ø{dia:g}", "07-tuyaux", "tube_comb", dict(count=6,diameter=dia,pitch=dia+7,width=40,height=14),
        "Guider six tuyaux par leur extérieur, sans les pincer ni obturer leur lumière.", f"Encoches ouvertes de {dia} mm ; aucun contact direct avec le fluide.")
for ident, dia, radius in [("T03",6.8,30),("T04",10.8,40)]:
    add(ident, f"Guide courbe 90° tuyau Ø{dia:g}", "07-tuyaux", "tube_bend", dict(diameter=dia,radius=radius,height=10,wall=4),
        "Accompagner un tuyau souple dans un virage à 90°, sans fonction de raccord ni d'étanchéité.",
        f"Rayon de ligne médiane {radius} mm ; vérifier le rayon de courbure minimal du tuyau.")

add("O01", "Repose 6 spatules", "08-rangement", "rod_rest", dict(count=6,diameter=12,pitch=22,length=154,width=75,height=16),
    "Poser des spatules propres et froides ; support de rangement, pas zone de pesée analytique.", "Six gorges ouvertes de 12 mm.")
add("O02", "Repose 3 thermomètres", "08-rangement", "rod_rest", dict(count=3,diameter=7,pitch=25,length=96,width=80,height=16),
    "Ranger trois thermomètres ou sondes propres et froids.", "Trois gorges ouvertes de 7 mm.")
add("O03", "Organiseur 3 compartiments", "08-rangement", "tray", dict(length=180,width=120,height=22,wall=3,bottom=3,dividers=2),
    "Ranger bouchons, pinces et petites pièces secs. Ce plateau n'est pas une rétention de sécurité.")
add("O04", "Bac de rangement long", "08-rangement", "tray", dict(length=225,width=85,height=26,wall=3,bottom=3,dividers=0),
    "Ranger spatules et petites pièces secs, sans chauffage ni produits dangereux.")

for ident, dia in [("S01",25),("S02",40)]:
    add(ident, f"Petite pelle Ø{dia} pour démonstration", "09-contact-conditionnel", "scoop", dict(diameter=dia,height=12 if dia==25 else 17,wall=2.4,handle=90),
        "Manipulation de poudres bénignes pour démonstration, uniquement après vérification de compatibilité et de propreté ; ne mesure pas un volume étalonné.",
        "Pas de poudre toxique, réactive, pharmaceutique ni analyse de traces.", material="PP compatible avec le produit, à qualifier")
for ident, dia, height in [("V01",40,50),("V02",60,75),("V03",80,100)]:
    add(ident, f"Gobelet prototype Ø{dia} × {height}", "09-contact-conditionnel", "cup", dict(diameter=dia,height=height,wall=2.4,bottom=3),
        "Prototype de récipient pour eau ou solution bénigne à température ambiante, après validation de l'étanchéité. Ne remplace pas un bécher de laboratoire.",
        "Sans graduation ni capacité certifiée ; aucune chauffe, pression, stérilisation ou substance dangereuse.", material="PP compatible avec le liquide, à qualifier")
for ident, dia in [("E01",60),("E02",90)]:
    add(ident, f"Entonnoir de démonstration Ø{dia}", "09-contact-conditionnel", "funnel", dict(diameter=dia,stem_od=16,stem_id=11,height=45 if dia==60 else 60,stem_height=16,wall=2.4),
        "Transvaser de l'eau ou un liquide bénin à froid, après vérification de compatibilité et d'étanchéité ; pour les réactifs, utiliser un entonnoir de laboratoire adapté.",
        "Tige Ø extérieur 16 mm, passage 11 mm ; imprimer debout avec une bordure d'adhérence.", material="PP compatible avec le liquide, à qualifier")

for ident, dia in [("L01",24),("L02",32),("L03",45)]:
    add(ident, f"Étiquette de col Ø{dia}", "10-etiquetage", "bottle_tag", dict(diameter=dia,wall=4,thickness=3,tab_length=42,tab_width=22),
        "Ajouter une étiquette de rangement autour du col d'un flacon ; garder les mentions réglementaires et l'étiquette du fabricant visibles.",
        f"Anneau fermé Ø intérieur {dia} mm ; passer le col avant de refermer le bouchon, sans interférer avec sa fermeture.")
add("G01", "Jauge de diamètres 4 à 20 mm", "11-calibration", "gauge", dict(diameters=[4,6,8,10,12,14,16,18,20],thickness=4),
    "Évaluer le jeu réel de ton impression avant de fabriquer un portoir complet.", "Trous nominaux ; la pièce n'est pas un instrument de métrologie certifié.")
add("G02", "Coupon emboîtements des potences", "11-calibration", "fit_coupon", dict(sockets=[20.2,20.4,20.6],peg=19.9,thickness=10),
    "Tester les trois jeux d'emboîtement avant d'imprimer les grandes potences.", "Trois logements carrés et un pion solidaire du coupon ; tester avec une colonne séparée ou mesurer au pied à coulisse.")

ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "catalogue-base.json").write_text(json.dumps({"units":"mm", "printer_envelope_mm":[256,256,256], "parts":PARTS},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Catalogue: {len(PARTS)} pièces originales, {len(set(p['kind'] for p in PARTS))} familles géométriques.")
