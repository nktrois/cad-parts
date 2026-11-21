"""Generate catalogue, per-part instructions and contact sheets from the selection."""
from pathlib import Path
import csv,html,json,math,os,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
PARTS=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"))["parts"]
LABELS={"atelier":"Atelier et rangement · 45 pièces","recipients":"Récipients ouverts · 10 pièces","humides":"Immersion, rinçage, préparation · 8 pièces","filtration":"Station de filtration · 17 pièces"}
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+"\n",encoding="utf-8")
def mat(p):return p.get("material_candidate",p.get("material","À sélectionner"))
def dims(p):return " × ".join(f"{d:g}" for d in p["dimensions_mm"])
def relative(source,target):return Path(os.path.relpath(target,source)).as_posix()

readme="""# Chimie et atelier — 80 CAO originales

Une bibliothèque entièrement originale en STL, STEP et FreeCAD : **45 pièces d'atelier**, **10 récipients ouverts**, **8 outils d'immersion, de filtration et de préparation**, et **17 éléments de station de filtration**. Les Erlenmeyer et les modèles récupérés ne font pas partie de cette sélection.

![Station de filtration et coupe](apercus/filtration-detail.jpg)

Le système de filtration réunit le collecteur, une chambre démontable, deux grilles alternatives, un récepteur cylindrique conçu ici, ses couvercles, son berceau, un bras sur tige métallique et **trois joints TPU**. Un coupon permet de tester l'ajustement du TPU. [Montage, dimensions et liste d'achats](filtration/README.md).

**Ouvrir [catalogue.html](catalogue.html)** pour parcourir les 80 modèles, filtrer par série ou matière et accéder aux fichiers. [Catalogue Markdown](CATALOGUE.md), [données JSON](catalogue.json), [table CSV](catalogue.csv).

| Série | Contenu |
|---|---|
| Atelier | Portoirs tubes/flacons, potences pour entonnoirs, porte-pipettes, égouttoirs, supports de sondes, guides de tuyaux, plateaux, spatules, coupelles, étiquettes, jauges |
| Récipients ouverts | Béchers à bec de 100, 250, 500 et 1 000 mL nominaux ; cristallisoirs Ø90/140 ; entonnoirs liquides Ø60/90 et poudres Ø80/110 |
| Outils humides | Bain, panier perforé, porte-éprouvettes d'immersion, ancien filtre gravitaire et sa grille, coupelle de pesée, palette, bloc de rinçage à trois étapes |
| Filtration intégrée | FL01–FL17 : pièces en contact candidates au PP, joints TPU et bâti sec en PETG |

## Ce qui est vérifié

Les 80 STL ont une topologie fermée, un seul composant, des orientations cohérentes et un volume positif. Les STEP et FCStd ont été relus indépendamment : un solide valide par pièce. Chaque modèle tient individuellement dans 240 mm sur les trois axes ; le plus grand atteint 235 mm. Les contrôles d'assemblage de filtration ne détectent aucune collision rigide inattendue ; les deux interférences TPU prévues sont identifiées.

Ces contrôles numériques ne sont pas des essais d'étanchéité, de résistance chimique, de chauffe ou de vide. **Aucune pièce n'a encore été imprimée ou physiquement qualifiée.** La configuration initiale du filtre est gravitaire, évent ouvert. Le récepteur et le couvercle à deux ports restent sans tenue au vide assignée. La matière et le grade doivent convenir au produit, à sa concentration, à la température et à la durée réelles ; le TPU n'est pas un joint universel pour les acides et bases.

## Imprimer et modifier

[Plan d'impression et régénération](IMPRESSION.md) · [Matériaux et limites machine](recipients-chimiques/MATERIAUX.md) · [Rapport STL](verification/mesh-report.json) · [Relecture STEP/FreeCAD](verification/cad-readback.json) · [Interfaces et collisions de filtration](filtration/verification/assemblages.json).

Les STL sont en millimètres. Les FCStd contiennent les solides CAO et des métadonnées ; la modification paramétrique se fait dans les sources Python/JSON FreeCAD, sans historique de fonctions esquissées. Aucun profil trancheur ni G-code n'est fourni. Les coupes PLY sont des illustrations non imprimables.

Toutes les créations sont attribuées à **nktrois**, sous [CC BY 4.0](LICENSE). Aucun modèle tiers n'est embarqué. Le conditionnement et les scripts restent locaux ; aucune publication GitHub n'est autorisée par la seule génération de ces fichiers.
"""
write(ROOT/"README.md",readme)
lines=["# Catalogue des 80 pièces originales","", "STL en mm · STEP · FreeCAD · CC BY 4.0. Les matières sont des candidates à qualifier. [Montage de filtration](filtration/README.md) · [Plan d'impression](IMPRESSION.md)",""]
cards=[]
for series,label in LABELS.items():
    rows=[p for p in PARTS if p["series"]==series]
    lines += ["## "+label,"",f"![{label}](apercus/planche-{series}.jpg)","","| ID | Modèle | Encombrement mm | Matière candidate | Fichiers |","|---|---|---|---|---|"]
    for p in rows:
        ident=p["id"];folder=ROOT/p["path"];links=" · ".join(f"[{ext}]({p['path']}/{ident}.{ext})" for ext in ("stl","step","FCStd"))
        lines.append(f"| [{ident}]({p['path']}/README.md) | {p['title']} | {dims(p)} | {mat(p)} | {links} |")
        usage=p.get("usage",p.get("intended_use",p.get("fit","Voir la notice de série.")))
        back=relative(folder,ROOT)
        text=f"# {ident} — {p['title']}\n\n![Aperçu du STL]({back}/apercus/{ident}.png)\n\n{usage}\n\n- Encombrement STL : **{dims(p)} mm**.\n- Matière candidate : **{mat(p)}**.\n- Interface : {p.get('fit','Consulter les dimensions et paramètres du catalogue.')}\n- Fichiers : [{ident}.stl]({ident}.stl), [{ident}.step]({ident}.step), [{ident}.FCStd]({ident}.FCStd).\n\nModèle original nktrois · [CC BY 4.0]({back}/LICENSE). Contrôles numériques seulement ; aucune impression, étanchéité, tenue chimique, thermique ou au vide qualifiée.\n\n[Plan d'impression]({back}/IMPRESSION.md) · [Catalogue]({back}/CATALOGUE.md)"
        if series=="filtration":text+=f" · [Montage de la station]({back}/filtration/README.md)"
        if "capacity_to_rim_calculated_ml" in p:text+=f"\n\nCapacité géométrique calculée au bord : {p['capacity_to_rim_calculated_ml']} mL. Ce n'est pas un étalonnage volumétrique."
        write(folder/"README.md",text)
        esc=html.escape
        tags=esc(" ".join([ident,p["title"],mat(p),series]),quote=True)
        buttons="".join(f'<a href="{p["path"]}/{ident}.{ext}">{ext.upper()}</a>' for ext in ("stl","step","FCStd"))
        cards.append(f'<article data-series="{series}" data-search="{tags}" data-material="{esc(mat(p).split()[0])}"><a class="picture" href="apercus/{ident}.png"><img loading="lazy" src="apercus/{ident}.png" alt="{esc(p["title"])}"></a><div class="body"><small>{ident} · {esc(mat(p))}</small><h2>{esc(p["title"])}</h2><p>{dims(p)} mm</p><nav>{buttons}<a href="{p["path"]}/README.md">Notice</a></nav></div></article>')
    lines.append("")
write(ROOT/"CATALOGUE.md","\n".join(lines))
with (ROOT/"catalogue.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f,delimiter=";");w.writerow(["ID","Titre","Serie","Matiere candidate","X mm","Y mm","Z mm","Volume CAO mm3","STL","STEP","FreeCAD","Qualification chimique"])
    for p in PARTS:w.writerow([p["id"],p["title"],p["series"],mat(p),*p["dimensions_mm"],p["volume_material_mm3"],*[p["path"]+"/"+p["id"]+"."+e for e in ["stl","step","FCStd"]],"Non"])
template='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chimie & atelier · 80 CAO originales</title><style>
*{box-sizing:border-box}body{margin:0;background:#edf2f6;color:#153142;font:16px/1.5 system-ui,sans-serif}header{padding:48px max(5vw,24px);background:#123344;color:white}h1{font-size:clamp(30px,4vw,56px);line-height:1.05;margin:12px 0}header p{max-width:850px;color:#c9e0e9}header a{color:#a5edf1}.hero{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:28px auto;max-width:1280px;padding:0 24px}.hero img{width:100%;border-radius:15px}.hero a{color:#153142}.controls{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;gap:12px;padding:16px max(4vw,20px);background:#f9fcffed;backdrop-filter:blur(10px);border-bottom:1px solid #d2dfe7}input,select{padding:12px;border:1px solid #bcced9;border-radius:8px;font:inherit;background:white}input{flex:1;min-width:220px}main{max-width:1500px;margin:auto;padding:28px;display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:20px}article{background:white;border:1px solid #dce5eb;border-radius:12px;overflow:hidden}article[hidden]{display:none}.picture{display:block;background:#e5e9ed}.picture img{display:block;width:100%;aspect-ratio:4/3;object-fit:contain}.body{padding:18px}small{color:#527083}h2{font-size:18px;margin:7px 0;line-height:1.3}.body p{color:#527083;font-size:14px}nav{display:flex;flex-wrap:wrap;gap:7px}nav a{font-size:12px;background:#e7f2f6;border-radius:5px;color:#075c6e;padding:7px 9px;text-decoration:none}footer{padding:30px;text-align:center;color:#527083}#count{align-self:center;min-width:70px}@media(max-width:650px){.hero{grid-template-columns:1fr}header{padding:30px 24px}.controls{position:relative}main{padding:16px}}
</style><header><small style="color:#81d6dd">COLLECTION ORIGINALE · nktrois · CC BY 4.0</small><h1>Chimie & atelier</h1><p>80 modèles à parcourir, imprimer et adapter. Filtration complète, immersion, préparation, récipients ouverts et rangement. Fichiers STL, STEP et FreeCAD pour chaque pièce.</p><p><strong>Prototypes numériques.</strong> Aucun essai physique, chimique, thermique ou de vide réalisé. Le filtre est prévu d'abord pour des essais gravitaires, évent ouvert. La compatibilité du PP et des joints TPU dépend du grade et des produits.</p><a href="filtration/README.md">Montage & quincaillerie</a> · <a href="IMPRESSION.md">Impression</a> · <a href="CATALOGUE.md">Catalogue texte</a></header><section class="hero"><a href="apercus/station-gravitaire.png"><img src="apercus/station-gravitaire.png" alt="Station montée"><strong>Station de filtration démontable</strong></a><a href="apercus/coupe-filtration.png"><img src="apercus/coupe-filtration.png" alt="Coupe des interfaces et des joints"><strong>Coupe : les trois joints TPU en orange</strong></a></section><div class="controls"><input id="query" type="search" aria-label="Rechercher" placeholder="Rechercher : joint, bécher, portoir…"><select id="series" aria-label="Série"><option value="">Toutes les séries</option>__OPTIONS__</select><select id="material" aria-label="Matière candidate"><option value="">Toutes les matières candidates</option><option>PP</option><option>TPU</option><option>PETG</option></select><span id="count">80 / 80</span></div><main>__CARDS__</main><footer>Rendus issus des géométries réelles. Les coupes sont des illustrations non imprimables. Tige métallique et quincaillerie à acheter séparément. Aucun push effectué.</footer><script>
const query=document.querySelector('#query'),series=document.querySelector('#series'),material=document.querySelector('#material'),cards=[...document.querySelectorAll('article')];const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();function update(){let n=0;const terms=norm(query.value).split(/\\s+/).filter(Boolean);for(const c of cards){const show=(!series.value||c.dataset.series===series.value)&&(!material.value||c.dataset.material===material.value)&&terms.every(t=>norm(c.dataset.search).includes(t));c.hidden=!show;if(show)n++;}document.querySelector('#count').textContent=n+' / '+cards.length;}[query,series,material].forEach(el=>el.addEventListener('input',update));
</script></html>'''
options="".join(f'<option value="{s}">{html.escape(l)}</option>' for s,l in LABELS.items())
write(ROOT/"catalogue.html",template.replace("__OPTIONS__",options).replace("__CARDS__","\n".join(cards)))

def font(size,bold=False):
    root=Path("C:/Windows/Fonts");path=root/("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(path),size) if path.exists() else ImageFont.load_default()
def sheet(rows,title,target,columns=4):
    cw,ch=360,332;top=110;cols=columns;nr=math.ceil(len(rows)/cols)
    im=Image.new("RGB",(cw*cols,top+nr*ch+65),(239,245,249));d=ImageDraw.Draw(im)
    d.text((22,18),title,font=font(30,True),fill=(18,51,68));d.text((22,62),"CAO originales · STL / STEP / FreeCAD · prototypes à qualifier",font=font(18),fill=(64,96,112))
    for i,p in enumerate(rows):
        x=(i%cols)*cw;y=top+(i//cols)*ch
        pic=Image.open(ROOT/"apercus"/(p["id"]+".png")).convert("RGB");pic.thumbnail((cw-16,238))
        im.paste(pic,(x+(cw-pic.width)//2,y));titlelines=textwrap.wrap(p["id"]+" — "+p["title"],32)
        for n,line in enumerate(titlelines[:2]):d.text((x+12,y+241+n*22),line,font=font(17,True),fill=(18,51,68))
        d.text((x+12,y+288),dims(p)+" mm",font=font(15),fill=(64,96,112))
    d.text((20,im.height-43),"nktrois · CC BY 4.0 · contrôles numériques seulement",font=font(17),fill=(64,96,112));im.save(target,quality=88)
for series,label in LABELS.items():sheet([p for p in PARTS if p["series"]==series],label,ROOT/"apercus"/("planche-"+series+".jpg"))
sheet(PARTS,"80 pièces originales · vue d'ensemble",ROOT/"apercus/vue-ensemble.jpg",columns=8)
im=Image.new("RGB",(1800,900),(239,245,249));d=ImageDraw.Draw(im)
d.text((34,20),"Filtration : pièces conçues ensemble",font=font(38,True),fill=(18,51,68))
d.text((34,75),"Récepteur original · chambre démontable · grilles interchangeables · trois joints TPU",font=font(24),fill=(64,96,112))
for x,name in [(0,"station-gravitaire"),(900,"coupe-filtration")]:
    pic=Image.open(ROOT/"apercus"/(name+".png")).convert("RGB");pic=pic.resize((900,675),Image.Resampling.LANCZOS);im.paste(pic,(x,125))
d.text((34,817),"Bleu : PP candidat    Orange : TPU candidat    Turquoise : supports secs PETG",font=font(24,True),fill=(18,51,68))
d.text((34,857),"Prototype numérique · essais gravitaires à réaliser · aucune tenue au vide assignée",font=font(22),fill=(64,96,112))
im.save(ROOT/"apercus/filtration-detail.jpg",quality=92)
print("DOCUMENTATION_OK",len(PARTS),"notices; catalogue HTML/MD/CSV; 6 planches")
from organize_documentation import main as organize_documentation
organize_documentation()
