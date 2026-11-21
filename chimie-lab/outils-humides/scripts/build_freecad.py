"""FreeCADCmd: functional concepts for opaque wet-contact lab tools.

PP grade, chemical compatibility, leak resistance and mechanical performance
remain to be qualified. No pressure/vacuum or calibrated dispensing features.
"""
from pathlib import Path
import json,math,traceback
import FreeCAD as App
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1]
V=App.Vector
E=.12

def box(x,y,z,at=(0,0,0)):return Part.makeBox(x,y,z,V(*at))
def cyl(r,h,at=(0,0,0)):return Part.makeCylinder(r,h,V(*at))
def union(parts):
    result=parts[0]
    for p in parts[1:]:result=result.fuse(p)
    return result.removeSplitter()
def rounded(x,y,z,r=4,at=(0,0,0)):
    out=union([box(x-2*r,y,z,(r,0,0)),box(x,y-2*r,z,(0,r,0))]+[cyl(r,z,(a,b,0)) for a in (r,x-r) for b in (r,y-r)])
    out.translate(V(*at));return out
def cut(s,tools):return s.cut(Part.makeCompound(tools)).removeSplitter() if tools else s

def bath(p):
    l,w,h,t,b=(p[k] for k in ("length","width","height","wall","bottom"))
    return rounded(l,w,h,8).cut(rounded(l-2*t,w-2*t,h-b+E,4,(t,t,b))).removeSplitter()

def basket(p):
    l,w,h,t,b=(p[k] for k in ("length","width","height","wall","bottom"))
    outer=rounded(l,w,h,5,(0,0,4))
    inside=rounded(l-2*t,w-2*t,h-b+E,2,(t,t,4+b))
    shape=outer.cut(inside)
    feet=[cyl(4,4.2,(x,y,0)) for x in (8,l-8) for y in (8,w-8)]
    ears=[box(6,20,24,(x,w/2-10,h+2)) for x in (-3,l-3)]
    shape=union([shape]+feet+ears)
    tools=[]
    for x in range(12,int(l)-10,10):
        for y in range(12,int(w)-10,10):tools.append(cyl(1.8,4+b+2*E,(x,y,-E)))
        for y in (-E,w-t-E):tools.append(box(4,t+2*E,30,(x-2,y,13)))
    for y in range(14,int(w)-10,10):
        for x in (-E,l-t-E):tools.append(box(t+2*E,4,30,(x,y-2,13)))
    for x in (-4,l-4):
        z=h+15;cy=w/2
        points=[V(x,cy-6,z),V(x,cy,z+7),V(x,cy+6,z),V(x,cy,z-7),V(x,cy-6,z)]
        tools.append(Part.Face(Part.makePolygon(points)).extrude(V(9,0,0)))
    return cut(shape,tools)

def coupon_holder(p):
    n,gap,t,l,w=(p[k] for k in ("count","gap","fin","length","width"))
    base=rounded(l,w,4,4)
    # Rails constrain coupon edges; open ends allow flow and manual removal.
    pitch=gap+t;start=(l-(n*gap+(n+1)*t))/2
    fins=[box(t,w-12,15,(start+i*pitch,6,4-E)) for i in range(n+1)]
    shape=union([base]+fins)
    tools=[]
    for i in range(n):
        x=start+t+gap/2+i*pitch
        for y in (14,w/2,w-14):tools.append(cyl(.9,5,(x,y,-E)))
    return cut(shape,tools)

def filter_body(p):
    # Upper open cup; removable disc sits at z=60 on an annular ledge.
    sh=p["stem_height"];ch=p["collector_height"];d=p["cup_inner_diameter"];w=p["wall"]
    z=sh+ch;r=d/2
    outer=union([cyl(4+w,sh+E),Part.makeCone(4+w,r+w,ch,V(0,0,sh)),cyl(r+w,22+E,(0,0,z-E))])
    tools=[cyl(4,sh+2*E,(0,0,-E)),Part.makeCone(4,r-2.5,ch+E,V(0,0,sh-E)),cyl(r,22+2*E,(0,0,z))]
    return cut(outer,tools)

def filter_disc(p):
    r=p["diameter"]/2;h=p["thickness"]
    shape=cyl(r,h);tools=[]
    for x in range(-24,25,6):
        for y in range(-24,25,6):
            if math.hypot(x,y)<=24:tools.append(cyl(1.25,h+2*E,(x,y,-E)))
    return cut(shape,tools)

def weigh_boat(p):
    l,w,h,t,b=(p[k] for k in ("length","width","height","wall","bottom"))
    shape=rounded(l,w,h,8).cut(rounded(l-2*t,w-2*t,h-b+E,5,(t,t,b)))
    # Open V in one short rim: a visible pour guide, not a liquid-tight cap.
    cy=w/2
    points=[V(l-t-1,cy-8,h+E),V(l-t-1,cy+8,h+E),V(l-t-1,cy,h-7),V(l-t-1,cy-8,h+E)]
    shape=shape.cut(Part.Face(Part.makePolygon(points)).extrude(V(t+2,0,0)))
    return shape.removeSplitter()

def paddle(p):
    handle=p["handle_length"];th=p["thickness"]
    grip=rounded(handle+5,12,th,4,(0,14,0))
    blade=rounded(50,40,th,6,(handle,0,0))
    shape=union([grip,blade])
    holes=[cyl(3,th+2*E,(handle+x,y,-E)) for x in (14,26,38) for y in (11,20,29)]
    holes.append(cyl(2.5,th+2*E,(8,20,-E)))
    return cut(shape,holes)

def rinse_block(p):
    l,w,h,d=(p[k] for k in ("length","width","height","well_diameter"))
    shape=rounded(l,w,h,6)
    return cut(shape,[cyl(d/2,h-6+E,(18+i*34,w/2,6)) for i in range(3)])

SPECS=[
    ("WB01","Bain ouvert pour immersion","bath",dict(length=190,width=125,height=70,wall=4,bottom=5),"Contenir un bain compatible ; ouverture supérieure permettant l'observation et la reprise des échantillons.","Bain + panier WB02 ; pas une rétention de sécurité."),
    ("WB02","Panier d'immersion perforé","basket",dict(length=164,width=100,height=52,wall=3,bottom=3.2),"Introduire et retirer des échantillons assez grands pour rester dans le panier ; circulation du bain par le fond et les côtés.","Pieds de 4 mm ; oreilles ajourées ; ajustement prévu dans WB01. La flottabilité et la charge doivent être testées."),
    ("WB03","Porte-éprouvettes immergeable","coupon_holder",dict(count=6,gap=3.2,fin=3,length=100,width=65),"Maintenir six plaquettes ou éprouvettes dans un bain compatible, sans besoin de transparence de l'outil.","Six fentes de 3,2 mm ; dimensions des éprouvettes à mesurer ; aucune conformité à une norme de corrosion revendiquée."),
    ("WF01","Porte-filtre gravitaire démontable","filter_body",dict(stem_height=25,collector_height=35,cup_inner_diameter=62,wall=3.6),"Soutenir un médium filtrant commercial avec la grille WF02 et collecter un écoulement gravitaire.","Portée de grille à z=60 mm ; passage de sortie Ø8 mm. Papier, absence de contournement et filtration à valider. Pas d'aspiration ni de pression."),
    ("WF02","Grille amovible de filtration","filter_disc",dict(diameter=61.2,thickness=3),"Supporter un papier ou médium filtrant commercial dans WF01 ; la grille imprimée n'est pas elle-même le filtre fin.","Ø61,2 mm dans un logement Ø62 mm ; trous Ø2,5 mm. La zone perforée doit être entièrement couverte par le médium."),
    ("WP01","Nacelle de pesée à bec","weigh_boat",dict(length=85,width=55,height=18,wall=2.8,bottom=3.2),"Peser et transférer un produit compatible avec une balance commerciale, après tare de la nacelle.","Lecture de masse sur la balance ; pas de dosage volumétrique ni de propreté analytique certifiés."),
    ("WP02","Palette d'agitation manuelle perforée","paddle",dict(handle_length=125,thickness=4),"Mélanger manuellement de petits volumes compatibles ; géométrie plate permettant nettoyage et inspection.","Longueur 175 mm ; pas d'entraînement motorisé, charge ou tenue thermique qualifiés."),
    ("WP03","Bloc de rinçage à trois postes","rinse_block",dict(length=104,width=44,height=42,well_diameter=26),"Réaliser des rinçages successifs d'une sonde ou d'un petit outil avec trois liquides compatibles dans des puits indépendants.","Trois puits Ø26 mm, profondeur 36 mm ; repérer les postes et vérifier les contaminations croisées.")
]
BUILDERS=dict(bath=bath,basket=basket,coupon_holder=coupon_holder,filter_body=filter_body,filter_disc=filter_disc,weigh_boat=weigh_boat,paddle=paddle,rinse_block=rinse_block)
records=[];report=[]
for ident,title,kind,params,usage,fit in SPECS:
    doc=None
    try:
        shape=BUILDERS[kind](params)
        assert shape.isValid() and len(shape.Solids)==1 and shape.Volume>0,ident
        bb=shape.BoundBox;shape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
        out=ROOT/"modeles"/ident;out.mkdir(parents=True,exist_ok=True)
        doc=App.newDocument(ident);obj=doc.addObject("PartDesign::Feature","Outil");obj.Label=title;obj.Shape=shape
        doc.recompute();doc.saveAs(str(out/(ident+".FCStd")));shape.exportStep(str(out/(ident+".step")))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.12,Relative=False)
        assert mesh.isSolid(),ident
        mesh.write(str(out/(ident+".stl")));mb=mesh.BoundBox;ds=[mb.XLength,mb.YLength,mb.ZLength]
        assert max(ds)<240
        record=dict(id=ident,title=title,kind=kind,parameters=params,usage=usage,fit=fit,path=out.relative_to(ROOT).as_posix(),
                    dimensions_mm=[round(v,3) for v in ds],volume_material_mm3=round(shape.Volume,3),
                    material_candidate="PP non chargé, référence et conditions à qualifier",chemical_qualified=False,physically_printed=False,
                    opacity_limits_use=False,author="nktrois",license="CC-BY-4.0")
        records.append(record);report.append(dict(id=ident,solid_valid=True,solids=1,mesh_solid=True))
        App.closeDocument(doc.Name);doc=None
        step=Part.Shape();step.read(str(out/(ident+".step")));native=App.openDocument(str(out/(ident+".FCStd")))
        shapes=[o.Shape for o in native.Objects if hasattr(o,"Shape") and not o.Shape.isNull()]
        assert step.isValid() and len(step.Solids)==1 and len(shapes)==1 and shapes[0].isValid()
        assert abs(step.Volume-shapes[0].Volume)<max(.1,shape.Volume*1e-5)
        report[-1].update(step_readback=True,fcstd_readback=True)
        App.closeDocument(native.Name)
        print("WET_TOOL_OK",ident,record["dimensions_mm"],flush=True)
    except Exception as exc:
        report.append(dict(id=ident,error=str(exc)));traceback.print_exc();print("WET_TOOL_ERROR",ident,repr(exc),flush=True)
    finally:
        if doc:App.closeDocument(doc.Name)
ROOT.mkdir(exist_ok=True)
(ROOT/"catalogue.json").write_text(json.dumps(dict(units="mm",parts=records),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"verification").mkdir(exist_ok=True)
(ROOT/"verification"/"cad.json").write_text(json.dumps(dict(parts=report,printed_physical=0,chemical_qualification=False),indent=2)+"\n",encoding="utf-8")
assert len(records)==8 and not any("error" in r for r in report),"Wet tool build failed"
