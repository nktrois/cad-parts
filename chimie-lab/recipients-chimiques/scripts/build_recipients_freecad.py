"""FreeCADCmd: vessels intended for qualification of chemical-contact PP prints.

No chemical suitability, leak resistance, heat rating or calibration is inferred
from the shape. Capacities below are geometric cavity volumes, not certificates.
"""
from pathlib import Path
import json,math,traceback
import FreeCAD as App
import Part,MeshPart

ROOT=Path(__file__).resolve().parents[1]
V=App.Vector
EPS=.12
SPECS=[]


def add(ident,title,kind,params,nominal=None):
    SPECS.append(dict(id=ident,title=title,kind=kind,parameters=params,
                      nominal_working_ml=nominal,material_candidate="PP non chargé, grade et usage à qualifier",
                      intended_use="Manipulation en récipient ouvert de solutions ou produits compatibles avec le grade et le procédé effectivement qualifiés.",
                      chemical_qualified=False,leak_tested=False,physically_printed=False,hot_use_qualified=False,
                      author="nktrois",license="CC-BY-4.0"))


for ident,vol,r,h in [("QB100",100,25,75),("QB250",250,35,95),("QB500",500,44,120),("QB1000",1000,55,155)]:
    add(ident,f"Bécher PP à bec verseur — nominal {vol} mL","beaker",
        dict(inner_radius=r,height=h,wall=3.6,bottom=4.8,inside_fillet=3,spout_height=12,spout_extension=7),vol)
for ident,diameter,h in [("QC090",90,28),("QC140",140,38)]:
    add(ident,f"Cristallisoir PP Ø intérieur {diameter} mm","dish",
        dict(inner_radius=diameter/2,height=h,wall=3.6,bottom=4.8,inside_fillet=4))
for ident,d,stemid,ch in [("QF060",60,10,43),("QF090",90,12,65),
                         ("QP080",80,24,44),("QP110",110,32,56)]:
    powder=ident.startswith("QP")
    add(ident,("Entonnoir PP pour poudres" if powder else "Entonnoir PP pour liquides")+f" Ø{d}","funnel",
        dict(top_inner_diameter=d,stem_inner_diameter=stemid,cone_height=ch,stem_height=24 if powder else 45,wall=3.6))


def line(a,b):
    return Part.makeLine(V(a[0],0,a[1]),V(b[0],0,b[1]))


def revolved(edges):
    return Part.Face(Part.Wire(edges)).revolve(V(0,0,0),V(0,0,1),360)


def profile_solid(points):
    return revolved([line(a,b) for a,b in zip(points,points[1:]+points[:1])])


def interior(r,b,f,upper):
    # Rounded floor-to-wall transition, tangent to the floor and cylindrical wall.
    start=(r-f,b);end=(r,b+f)
    mid=(r-f+f/math.sqrt(2),b+f-f/math.sqrt(2))
    edges=[line((0,b),start),Part.Arc(V(start[0],0,start[1]),V(mid[0],0,mid[1]),V(end[0],0,end[1])).toShape()]
    prev=end
    for pt in upper:
        edges.append(line(prev,pt));prev=pt
    edges += [line(prev,(0,prev[1])),line((0,prev[1]),(0,b))]
    return revolved(edges)


def outside(r,h,f=2):
    start=(r-f,0);end=(r,f)
    mid=(r-f+f/math.sqrt(2),f-f/math.sqrt(2))
    edges=[line((0,0),start),Part.Arc(V(start[0],0,start[1]),V(mid[0],0,mid[1]),V(end[0],0,end[1])).toShape(),
           line(end,(r,h)),line((r,h),(0,h)),line((0,h),(0,0))]
    return revolved(edges)


def spout_wire(r,z,extension):
    # Smooth local radial bulge, represented by a closed 144-sided contour.
    points=[]
    for i in range(144):
        a=2*math.pi*i/144
        aa=min(a,2*math.pi-a)
        bump=extension*math.cos(aa/(math.pi/5)*math.pi/2)**2 if aa<math.pi/5 else 0
        rr=r+bump
        points.append(V(rr*math.cos(a),rr*math.sin(a),z))
    return Part.makePolygon(points+[points[0]])


def beaker(p):
    r,h,w,b,f,sh,se=(p[k] for k in ("inner_radius","height","wall","bottom","inside_fillet","spout_height","spout_extension"))
    z=h-sh
    outer=outside(r+w,z+EPS).fuse(Part.makeLoft([spout_wire(r+w,z,0),spout_wire(r+w,h,se)],True,True))
    inner=interior(r,b,f,[(r,z+EPS)]).fuse(Part.makeLoft([spout_wire(r,z,0),spout_wire(r,h+EPS,se)],True,True))
    cavity=outer.common(inner)
    return outer.cut(inner).removeSplitter(),cavity,dict(max_inward_overhang_deg=0,inside_floor_fillet_mm=f,
                 spout_note="Bec évasé sur les 12 derniers mm ; épaisseur radiale nominale 3,6 mm, pas une preuve d'épaisseur normale uniforme dans le bec.")


def dish(p):
    r,h,w,b,f=(p[k] for k in ("inner_radius","height","wall","bottom","inside_fillet"))
    outer=outside(r+w,h)
    inner=interior(r,b,f,[(r,h+EPS)])
    return outer.cut(inner).removeSplitter(),outer.common(inner),dict(max_inward_overhang_deg=0,inside_floor_fillet_mm=f)


def funnel(p):
    d,di,ch,sh,w=(p[k] for k in ("top_inner_diameter","stem_inner_diameter","cone_height","stem_height","wall"))
    ri=di/2;rt=d/2
    outer=Part.makeCylinder(ri+w,sh+EPS).fuse(Part.makeCone(ri+w,rt+w,ch,V(0,0,sh)))
    inner=Part.makeCylinder(ri,sh+2*EPS,V(0,0,-EPS)).fuse(Part.makeCone(ri,rt,ch+EPS,V(0,0,sh)))
    angle=math.degrees(math.atan((rt-ri)/ch))
    return outer.cut(inner).removeSplitter(),None,dict(max_inward_overhang_deg=0,
                cone_angle_from_vertical_deg=round(angle,3),minimum_cone_wall_normal_design_mm=round(w*math.cos(math.radians(angle)),3),
                stem_inside_diameter_mm=di,geometry_note="Passage continu, aucune chambre fermée ni grille interne.")


BUILDERS=dict(beaker=beaker,dish=dish,funnel=funnel)


def level(cavity,target_ml):
    bb=cavity.BoundBox;lo=bb.ZMin;hi=bb.ZMax
    for _ in range(20):
        mid=(lo+hi)/2
        clip=Part.makeBox(bb.XLength+4,bb.YLength+4,mid-bb.ZMin+1,V(bb.XMin-2,bb.YMin-2,bb.ZMin-1))
        vol=cavity.common(clip).Volume/1000
        if vol<target_ml:lo=mid
        else:hi=mid
    return round((lo+hi)/2,3)


report=[]
for spec in SPECS:
    ident=spec["id"];doc=None
    try:
        shape,cavity,design=BUILDERS[spec["kind"]](spec["parameters"])
        assert shape.isValid() and len(shape.Solids)==1 and shape.Volume>0,ident
        assert design["max_inward_overhang_deg"]<=45,design
        # Translate only in XY; the bottom plane is already Z=0.
        bb=shape.BoundBox;translation=V(-bb.XMin,-bb.YMin,0);shape.translate(translation)
        if cavity:cavity.translate(translation)
        b=shape.BoundBox
        assert max(b.XLength,b.YLength,b.ZLength)<240,ident
        folder=ROOT/"modeles"/ident;folder.mkdir(parents=True,exist_ok=True)
        doc=App.newDocument(ident)
        obj=doc.addObject("PartDesign::Feature","Recipient");obj.Label=spec["title"];obj.Shape=shape
        for name,value in [("MatiereCandidate",spec["material_candidate"]),("ParametresJSON",json.dumps(spec["parameters"])),
                           ("Qualification","Conception pour contact chimique ; compatibilite, etancheite et tenue thermique non qualifiees.")]:
            obj.addProperty("App::PropertyString",name,"Documentation");setattr(obj,name,value)
        doc.recompute();doc.saveAs(str(folder/(ident+".FCStd")))
        shape.exportStep(str(folder/(ident+".step")))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.06,AngularDeflection=.1,Relative=False)
        assert mesh.isSolid(),ident
        mesh.write(str(folder/(ident+".stl")))
        mb=mesh.BoundBox
        spec.update(path=folder.relative_to(ROOT).as_posix(),dimensions_mm=[round(v,3) for v in (mb.XLength,mb.YLength,mb.ZLength)],
                    volume_material_mm3=round(shape.Volume,3),design=design,facets=mesh.CountFacets)
        if cavity:
            brim=cavity.Volume/1000;spec["capacity_to_rim_calculated_ml"]=round(brim,2)
            if spec["nominal_working_ml"]:
                target=spec["nominal_working_ml"];assert brim>target*1.1,(ident,brim,target)
                spec["nominal_level_from_bottom_calculated_mm"]=level(cavity,target)
                spec["headspace_at_nominal_calculated_percent"]=round((brim-target)/brim*100,1)
        report.append(dict(id=ident,solid_valid=True,solids=1,mesh_solid=True,dimensions_mm=spec["dimensions_mm"],design=design))
        print("VESSEL_OK",ident,spec["dimensions_mm"],spec.get("capacity_to_rim_calculated_ml"),flush=True)
    except Exception as exc:
        report.append(dict(id=ident,error=str(exc)));traceback.print_exc()
        print("VESSEL_ERROR",ident,repr(exc),flush=True)
    finally:
        if doc:App.closeDocument(doc.Name)
(ROOT/"catalogue.json").write_text(json.dumps(dict(units="mm",parts=SPECS),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"verification").mkdir(exist_ok=True)
(ROOT/"verification"/"build.json").write_text(json.dumps(dict(parts=report,physically_printed=0,chemical_tests=0),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
assert len(report)==10 and not any("error" in r for r in report),"Recipient build failed"
