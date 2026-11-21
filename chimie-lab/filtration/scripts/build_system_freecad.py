"""Integrated filtration station and TPU seals, authored from first principles.

Gravity configuration is the initial qualification path. Parts forming the
receiver or suction path are unqualified prototypes: no vacuum/pressure rating.
All mating dimensions below are defined together rather than inferred from an
unknown commercial flask. Threads/bolts, rod, tubing, filter media and pump are
separate hardware; no claimed chemical compatibility of generic PP or TPU.
"""
from pathlib import Path
import json,math,traceback
import FreeCAD as App
import Part,MeshPart

ROOT=Path(__file__).resolve().parents[1]
V=App.Vector
E=.12
P=dict(stem_od=16,stem_id=10,stem_length=55,collector_height=30,
       filter_flange_d=106,filter_bolt_circle=88,filter_bolts=6,filter_bolt_hole=4.5,
       filter_disc_d=55.2,filter_disc_t=4,filter_disc_pocket_d=56,filter_throat_d=51,
       filter_gasket_id=50,filter_gasket_od=72,filter_gasket_t=2.2,
       chamber_id=60,chamber_wall=4,chamber_height=50,
       receiver_id=106,receiver_od=126,receiver_height=120,receiver_bottom=10,
       receiver_flange_d=154,receiver_flange_t=10,receiver_bolt_circle=140,receiver_bolt_hole=6.6,
       receiver_gasket_id=106,receiver_gasket_od=130,receiver_gasket_t=3,
       lid_thickness=10,neck_od=44,neck_height=26,
       neck_cone_bottom_d=29.6,neck_cone_top_d=34,neck_cone_length=18,
       bung_bottom_d=29.8,bung_top_d=34.2,bung_hole_d=15.6,bung_lip_d=48,bung_lip_t=3,
       rod_d=12,rod_length=300,rod_clearance_d=12.4,
       station_l=235,station_w=195,station_t=12,
       hose_bore=4,hose_stem_od=8,hose_barb_od=9,hose_port_height=28)

def box(x,y,z,p=(0,0,0)):return Part.makeBox(x,y,z,V(*p))
def cyl(r,h,p=(0,0,0),axis=(0,0,1)):return Part.makeCylinder(r,h,V(*p),V(*axis))
def join(parts):
    result=parts[0]
    for s in parts[1:]:result=result.fuse(s)
    return result.removeSplitter()
def cut(s,tools):return s.cut(Part.makeCompound(tools)).removeSplitter() if tools else s
def rounded(x,y,z,r=4,p=(0,0,0)):
    shape=join([box(x-2*r,y,z,(r,0,0)),box(x,y-2*r,z,(0,r,0))]+
               [cyl(r,z,(a,b,0)) for a in (r,x-r) for b in (r,y-r)])
    shape.translate(V(*p));return shape
def ring(od,id,h,z=0):return cyl(od/2,h,(0,0,z)).cut(cyl(id/2,h+2*E,(0,0,z-E))).removeSplitter()
def bolt_holes(circle,count,diameter,z,h):
    return [cyl(diameter/2,h,(circle/2*math.cos(2*math.pi*i/count),circle/2*math.sin(2*math.pi*i/count),z)) for i in range(count)]
def hex_vertical(af,h,x,y,z):
    r=af/math.sqrt(3);points=[V(x+r*math.cos(math.pi/6+i*math.pi/3),y+r*math.sin(math.pi/6+i*math.pi/3),z) for i in range(6)]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,h))

def collector():
    sh=P["stem_length"];ch=P["collector_height"];f=sh+ch
    shape=join([cyl(P["stem_od"]/2,sh+E),Part.makeCone(P["stem_od"]/2,35,ch,V(0,0,sh)),cyl(P["filter_flange_d"]/2,8,(0,0,f))])
    tools=[cyl(P["stem_id"]/2,sh+2*E,(0,0,-E)),Part.makeCone(P["stem_id"]/2,P["filter_throat_d"]/2,ch+E,V(0,0,sh-E)),
           cyl(P["filter_throat_d"]/2,4+E,(0,0,f-E)),cyl(P["filter_disc_pocket_d"]/2,4+2*E,(0,0,f+4-E))]
    return cut(shape,tools+bolt_holes(P["filter_bolt_circle"],6,P["filter_bolt_hole"],f-E,8+2*E))

def upper_chamber():
    r=P["chamber_id"]/2;h=P["chamber_height"]
    shape=join([cyl(P["filter_flange_d"]/2,8),cyl(r+P["chamber_wall"],h+E,(0,0,8-E))])
    tools=[cyl(25,3+E,(0,0,-E)),Part.makeCone(25,r,5+E,V(0,0,3-E)),cyl(r,h+2*E,(0,0,8-E))]
    return cut(shape,tools+bolt_holes(P["filter_bolt_circle"],6,P["filter_bolt_hole"],-E,8+2*E))

def filter_disc(coarse=False):
    d=P["filter_disc_d"];t=P["filter_disc_t"]
    s=cyl(d/2,t);tools=[]
    step=7 if coarse else 5
    for x in range(-21,22,step):
        for y in range(-21,22,step):
            if math.hypot(x,y)<=22:
                tools.append(cyl(2 if coarse else 1.1,t+2*E,(x,y,-E)))
    return cut(s,tools)

def bung():
    h=P["neck_cone_length"]
    outer=join([Part.makeCone(P["bung_bottom_d"]/2,P["bung_top_d"]/2,h),cyl(P["bung_lip_d"]/2,P["bung_lip_t"],(0,0,h-E))])
    return outer.cut(cyl(P["bung_hole_d"]/2,h+P["bung_lip_t"]+2*E,(0,0,-E))).removeSplitter()

def receiver():
    h=P["receiver_height"];ft=P["receiver_flange_t"]
    shape=join([cyl(P["receiver_od"]/2,h-ft+E),cyl(P["receiver_flange_d"]/2,ft,(0,0,h-ft))])
    tools=[cyl(P["receiver_id"]/2,h-P["receiver_bottom"]+E,(0,0,P["receiver_bottom"]))]
    return cut(shape,tools+bolt_holes(P["receiver_bolt_circle"],6,P["receiver_bolt_hole"],h-ft-E,ft+2*E))

def hose_port(x):
    z=P["lid_thickness"];h=P["hose_port_height"]
    shapes=[cyl(P["hose_stem_od"]/2,h,(x,0,z-E))]
    for zz in (z+7,z+14,z+21):
        shapes.append(Part.makeCone(P["hose_stem_od"]/2,P["hose_barb_od"]/2,2,V(x,0,zz)))
        shapes.append(Part.makeCone(P["hose_barb_od"]/2,P["hose_stem_od"]/2,2,V(x,0,zz+2-E)))
    return join(shapes)

def receiver_lid(trap=False):
    t=P["lid_thickness"];nh=P["neck_height"]
    outer=join([cyl(P["receiver_flange_d"]/2,t),hose_port(42)]+([hose_port(-42)] if trap else [cyl(P["neck_od"]/2,nh,(0,0,t-E))]))
    tools=[cyl(P["hose_bore"]/2,t+P["hose_port_height"]+2*E,(42,0,-E))]
    if not trap:
        tools += [cyl(P["neck_cone_bottom_d"]/2,18+E,(0,0,-E)),Part.makeCone(P["neck_cone_bottom_d"]/2,P["neck_cone_top_d"]/2,P["neck_cone_length"]+E,V(0,0,18-E))]
    if trap:tools.append(cyl(P["hose_bore"]/2,t+P["hose_port_height"]+2*E,(-42,0,-E)))
    return cut(outer,tools+bolt_holes(P["receiver_bolt_circle"],6,P["receiver_bolt_hole"],-E,t+2*E))

def station_base():
    shape=rounded(P["station_l"],P["station_w"],P["station_t"],8)
    holes=[cyl(2.8,P["station_t"]+2*E,(x,y,-E)) for x in (16,44) for y in (77.5,117.5)]
    holes += [cyl(2.8,P["station_t"]+2*E,(x,y,-E)) for x,y in [(100,57.5),(180,57.5),(100,137.5),(180,137.5)]]
    nut_positions=[(x,y) for x in (16,44) for y in (77.5,117.5)]+[(100,57.5),(180,57.5),(100,137.5),(180,137.5)]
    return cut(shape,holes+[hex_vertical(8.4,5+E,x,y,-E) for x,y in nut_positions])

def rod_foot():
    shape=join([rounded(50,60,8,5),cyl(17,35,(20,30,8-E))])
    tools=[cyl(P["rod_clearance_d"]/2,35+E,(20,30,8)),cyl(2.75,13,(26,30,30),(1,0,0))]
    tools += [cyl(2.8,8+2*E,(x,y,-E)) for x in (8,36) for y in (10,50)]
    r=8.4/math.sqrt(3);pts=[V(33,30+r*math.cos(i*math.pi/3),30+r*math.sin(i*math.pi/3)) for i in range(6)]
    tools.append(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(5,0,0)))
    return cut(shape,tools)

def support_arm():
    outer=join([cyl(59,10,(132,59,0)),rounded(42,42,10,4,(0,38,0)),box(112,24,10,(20,47,0))])
    clearances=bolt_holes(P["filter_bolt_circle"],6,12,-E,10+2*E)
    for s in clearances:s.translate(V(132,59,0))
    return cut(outer,[cyl(37,10+2*E,(132,59,-E)),cyl(P["rod_clearance_d"]/2,10+2*E,(20,59,-E))]+clearances)

def cradle():
    base=cyl(78,3)
    hoop=ring(154,127.2,9,3-E)
    shape=join([base,hoop])
    positions=[(-40,-40),(40,-40),(-40,40),(40,40)]
    holes=[cyl(2.8,3+2*E,(x,y,-E)) for x,y in positions]
    # 90-degree countersinks keep M5 flat heads flush below the receiver floor.
    return cut(shape,holes+[Part.makeCone(2.8,5.8,3,V(x,y,0)) for x,y in positions])

def hose_guide():
    shape=join([rounded(65,35,5,4),box(65,16,14,(0,12,5-E))])
    tools=[]
    for x in (15,32.5,50):
        tools += [cyl(4.6,15,(x,20,5-E)),box(9.2,20,15,(x-4.6,0,5-E))]
    tools += [cyl(2.8,6,(7,29,-E)),cyl(2.8,6,(58,29,-E))]
    return cut(shape,tools)

def disc_lifter():
    # External hook for handling clean removable plates, no sharp scraping edge.
    handle=rounded(100,12,4,4)
    head=ring(22,12,4);head.translate(V(105,6,0))
    s=join([handle,head])
    return s.cut(box(12,10,5,(105,0,-E))).removeSplitter()

def tpu_coupon():
    shape=rounded(95,38,6,4)
    return cut(shape,[cyl(d/2,7,(18+i*29,19,-E)) for i,d in enumerate((15.6,15.8,16.0))])

SPECS=[
    ("FL01","Collecteur inférieur à bride",collector,"PP","wetted","Tige Ø16 mm ; passage Ø10 ; six perçages M4 sur cercle Ø88 ; poche de grille Ø56."),
    ("FL02","Chambre supérieure de filtration",upper_chamber,"PP","wetted","Chambre Ø60 mm, hauteur 50 mm ; bride commune avec FL01 ; ouvertures du filtre et du joint Ø50."),
    ("FL03","Grille de support papier Ø55",lambda:filter_disc(False),"PP","wetted","Ø55,2 × 4 mm ; trous Ø2,2 ; support de papier, pas un filtre fin imprimé."),
    ("FL04","Joint plat de filtration TPU",lambda:ring(P["filter_gasket_od"],P["filter_gasket_id"],P["filter_gasket_t"]),"TPU","seal","Ø72 / Ø50 × 2,2 mm ; pince la périphérie du papier entre les deux brides ; compression à qualifier."),
    ("FL05","Joint conique tige–récepteur TPU",bung,"TPU","seal","Tige Ø16 dans alésage TPU Ø15,6 ; cône Ø29,8–34,2 dans col Ø29,6–34 ; interférences volontaires de conception."),
    ("FL06","Récepteur cylindrique démontable",receiver,"PP","receiver_prototype","Corps Ø126, intérieur Ø106, fond 10 mm ; bride Ø154 ; six perçages M6 sur cercle Ø140. Aucune tenue au vide assignée."),
    ("FL07","Couvercle de réception avec évent",lambda:receiver_lid(False),"PP","receiver_prototype","Col conique dimensionné avec FL05 ; port de diamètre intérieur 4 mm pour évent en mode gravitaire. Aspiration non qualifiée."),
    ("FL08","Couvercle deux ports pour prototype de piège",lambda:receiver_lid(True),"PP","receiver_prototype","Deux embouts OD8 à bourrelets Ø9, passage Ø4. Réutilise FL06 et FL09 ; aucune efficacité de piège ou tenue au vide prouvée."),
    ("FL09","Joint de couvercle du récepteur TPU",lambda:ring(P["receiver_gasket_od"],P["receiver_gasket_id"],P["receiver_gasket_t"]),"TPU","seal","Ø130 / Ø106 × 3 mm ; compression et compatibilité réelles à qualifier ; six boulons M6 extérieurs au joint."),
    ("FL10","Plateau de station",station_base,"PETG","dry","235 × 195 × 12 mm ; perçages communs au pied de tige et au berceau de récepteur ; une impression par module."),
    ("FL11","Pied de tige métallique Ø12",rod_foot,"PETG","dry","Quatre vis M5 ; logement Ø12,4 ; vis de blocage à écrou ou insert adapté. Tige métallique et fixation non fournies."),
    ("FL12","Bras de soutien sous bride",support_arm,"PETG","dry","Anneau ID74/OD118 ; déport d'axe 112 mm ; logement de tige Ø12,4 ; deux bagues de blocage de tige commerciales nécessaires."),
    ("FL13","Berceau du récepteur",cradle,"PETG","dry","Logement Ø127,2 pour corps Ø126 ; quatre vis M5 à tête fraisée 90° vers FL10, têtes affleurantes ; il ne remplace pas une évaluation de stabilité."),
    ("FL14","Guide extérieur de tuyaux",hose_guide,"PETG","dry","Trois passages ouverts Ø9,2 pour tuyaux extérieurs compatibles ; ce n'est pas un raccord étanche."),
    ("FL15","Crochet de reprise de grille",disc_lifter,"PP","wetted","Manipuler une grille propre hors charge ; tester la prise et la résistance avant usage."),
    ("FL16","Coupon TPU d'ajustement de tige",tpu_coupon,"TPU","calibration","Trois trous Ø15,6 / 15,8 / 16 mm pour tester le vrai filament avant le joint conique complet."),
    ("FL17","Grille de support alternative ajourée",lambda:filter_disc(True),"PP","wetted","Même interface Ø55,2 × 4 mm ; trous Ø4 ; support de médium, pas de granulométrie de filtration garantie.")
]

records=[];checks=[]
for ident,title,builder,material,role,fit in SPECS:
    doc=None
    try:
        shape=builder();assert shape.isValid() and len(shape.Solids)==1 and shape.Volume>0,ident
        bb=shape.BoundBox;shift=[-bb.XMin,-bb.YMin,-bb.ZMin];shape.translate(V(*shift))
        folder=ROOT/"modeles"/ident;folder.mkdir(parents=True,exist_ok=True)
        doc=App.newDocument(ident);obj=doc.addObject("PartDesign::Feature","Piece");obj.Label=title;obj.Shape=shape
        for name,value in [("Matiere",material),("Interface",fit),("Qualification","Prototype non imprime ; aucune tenue chimique, thermique ou au vide assignee")]:
            obj.addProperty("App::PropertyString",name,"Documentation");setattr(obj,name,value)
        doc.recompute();doc.saveAs(str(folder/(ident+".FCStd")));shape.exportStep(str(folder/(ident+".step")))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.12,Relative=False)
        assert mesh.isSolid(),ident
        mesh.write(str(folder/(ident+".stl")));mb=mesh.BoundBox;dims=[mb.XLength,mb.YLength,mb.ZLength]
        assert max(dims)<240,ident
        App.closeDocument(doc.Name);doc=None
        step=Part.Shape();step.read(str(folder/(ident+".step")));native=App.openDocument(str(folder/(ident+".FCStd")))
        ns=[o.Shape for o in native.Objects if hasattr(o,"Shape") and not o.Shape.isNull()]
        assert step.isValid() and len(step.Solids)==1 and len(ns)==1 and ns[0].isValid()
        assert abs(step.Volume-ns[0].Volume)<max(.1,shape.Volume*1e-5)
        App.closeDocument(native.Name)
        record=dict(id=ident,title=title,series="filtration",family="14-filtration",kind=builder.__name__,
                    material_candidate=material,material=material,role=role,fit=fit,
                    path=folder.relative_to(ROOT).as_posix(),dimensions_mm=[round(x,3) for x in dims],
                    volume_material_mm3=round(shape.Volume,3),export_origin_shift_mm=shift,
                    physically_printed=False,chemical_qualified=False,vacuum_rating_assigned=False,
                    author="nktrois",license="CC-BY-4.0")
        records.append(record);checks.append(dict(id=ident,solid_valid=True,mesh_solid=True,step_readback=True,fcstd_readback=True))
        print("FILTER_PART_OK",ident,record["dimensions_mm"],flush=True)
    except Exception as exc:
        checks.append(dict(id=ident,error=str(exc)));traceback.print_exc();print("FILTER_PART_ERROR",ident,repr(exc),flush=True)
    finally:
        if doc:App.closeDocument(doc.Name)
ROOT.mkdir(exist_ok=True)
(ROOT/"catalogue.json").write_text(json.dumps(dict(units="mm",interfaces=P,parts=records),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"verification").mkdir(exist_ok=True)
(ROOT/"verification"/"cad.json").write_text(json.dumps(dict(parts=checks,physically_tested=False),indent=2)+"\n",encoding="utf-8")
assert len(records)==17 and not any("error" in r for r in checks),"Filtration build failed"
