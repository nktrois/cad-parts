"""Assembly and dimensional interface checks, no structural qualification."""
from pathlib import Path
import json,itertools
import FreeCAD as App
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[1]
cat=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"));P=cat["interfaces"];specs={s["id"]:s for s in cat["parts"]}
V=App.Vector

def shape_at(ident,location):
    s=specs[ident];shape=Part.Shape();shape.read(str(ROOT/s["path"]/(ident+".step")))
    shift=s["export_origin_shift_mm"]
    shape.translate(V(*[location[i]-shift[i] for i in range(3)]))
    return shape

# Canonical datums in millimetres: round parts are centred in XY, bottom at Z=0.
main=[("FL10",(0,0,0)),("FL11",(8,67.5,12)),("FL13",(140,97.5,12)),
      ("FL06",(140,97.5,15)),("FL09",(140,97.5,135)),("FL07",(140,97.5,138)),
      ("FL05",(140,97.5,156)),("FL01",(140,97.5,126)),("FL03",(140,97.5,215)),
      ("FL04",(140,97.5,219)),("FL02",(140,97.5,221.2)),("FL12",(8,38.5,201))]
stack=[(i,p) for i,p in main if i in ("FL01","FL02","FL03","FL04","FL05","FL06","FL07","FL09")]
exploded=[]
offsets={"FL06":0,"FL09":30,"FL07":60,"FL05":105,"FL01":190,"FL03":230,"FL04":250,"FL02":275}
for ident,pos in stack:exploded.append((ident,(pos[0],pos[1],pos[2]+offsets[ident])))
trap=[("FL10",(0,0,0)),("FL13",(140,97.5,12)),("FL06",(140,97.5,15)),
      ("FL09",(140,97.5,135)),("FL08",(140,97.5,138))]
jobs=[("station-gravitaire",main),("filtre-eclate",exploded),("recepteur-deux-ports",trap)]
report=[]
hardware_clearance=dict(receiver_washer_od_mm=12,
    receiver_washer_to_body_radial_clearance_mm=P["receiver_bolt_circle"]/2-6-P["receiver_od"]/2,
    receiver_washer_to_flange_edge_mm=P["receiver_flange_d"]/2-P["receiver_bolt_circle"]/2-6,
    receiver_gasket_to_bolt_hole_gap_mm=P["receiver_bolt_circle"]/2-P["receiver_bolt_hole"]/2-P["receiver_gasket_od"]/2,
    cradle_countersink_top_d_mm=11.6,cradle_countersink_depth_mm=3,
    intended_m5_flat_head_d_mm=10,intended_m5_flat_head_height_mm=2.8,
    support_arm_nut_access_d_mm=12,intended_m4_washer_od_mm=9,
    commercial_fasteners_modelled_with_threads=False)
assert hardware_clearance["receiver_washer_to_body_radial_clearance_mm"]>0
assert hardware_clearance["receiver_washer_to_flange_edge_mm"]>0
assert hardware_clearance["receiver_gasket_to_bolt_hole_gap_mm"]>0
assert hardware_clearance["cradle_countersink_top_d_mm"]>=hardware_clearance["intended_m5_flat_head_d_mm"]
assert hardware_clearance["cradle_countersink_depth_mm"]>=hardware_clearance["intended_m5_flat_head_height_mm"]
for name,parts in jobs:
    doc=App.newDocument(name.replace("-","_"));objects=[];placed=[]
    for number,(ident,pos) in enumerate(parts):
        shape=shape_at(ident,pos);obj=doc.addObject("PartDesign::Feature",ident);obj.Label=ident+" — "+specs[ident]["title"];obj.Shape=shape
        objects.append(obj);placed.append((ident,shape))
    if name=="station-gravitaire":
        # Metal rod is an authored reference solid, not a printable STL.
        obj=doc.addObject("PartDesign::Feature","TigeMetalNonImprimee");obj.Label="Tige métallique commerciale Ø12 × 300, non imprimée"
        obj.Shape=Part.makeCylinder(6,300,V(28,97.5,20));objects.append(obj)
    checks=[]
    if name=="station-gravitaire":
        expected={frozenset(("FL05","FL07")):"Interférence diamétrale volontaire du cône TPU : 0,2 mm nominal.",
                  frozenset(("FL05","FL01")):"Interférence diamétrale volontaire TPU/tige : 0,4 mm nominal."}
        for (a,sa),(b,sb) in itertools.combinations(placed,2):
            bb=sa.BoundBox;cc=sb.BoundBox
            if bb.XMax<cc.XMin or cc.XMax<bb.XMin or bb.YMax<cc.YMin or cc.YMax<bb.YMin or bb.ZMax<cc.ZMin or cc.ZMax<bb.ZMin:continue
            overlap=sa.common(sb).Volume
            if overlap>.01:
                reason=expected.get(frozenset((a,b)))
                checks.append(dict(parts=[a,b],intersection_mm3=round(overlap,6),expected_elastic_interference=bool(reason),reason=reason))
                assert reason,(a,b,overlap)
    doc.recompute();out=ROOT/"assemblages"/name;out.mkdir(parents=True,exist_ok=True)
    doc.saveAs(str(out/(name+".FCStd")));Part.makeCompound([o.Shape for o in objects]).exportStep(str(out/(name+".step")))
    App.closeDocument(doc.Name)
    report.append(dict(id=name,parts=parts,checks=checks,structural_or_leak_test_performed=False))
    print("FILTER_ASSEMBLY_OK",name,checks,flush=True)

# Visual cut-away is explicitly not a print model and is exported as PLY.
preview=ROOT/"illustrations";preview.mkdir(exist_ok=True)
for ident,pos in stack:
    shape=shape_at(ident,pos)
    cut=Part.makeBox(400,400,700,V(-60,97.5,-10))
    section=shape.cut(cut)
    if not section.isNull():
        mesh=MeshPart.meshFromShape(Shape=section,LinearDeflection=.1,AngularDeflection=.12,Relative=False)
        mesh.write(str(preview/("COUPE_"+ident+"_NON_IMPRIMABLE.ply")))
(ROOT/"verification"/"assemblages.json").write_text(json.dumps(dict(assemblies=report,reference_rod=dict(diameter=12,length=300),
    interface_checks=dict(stem_od_mm=P["stem_od"],bung_hole_mm=P["bung_hole_d"],nominal_diametral_interference_mm=.4,
                          bung_outer_d_mm=[P["bung_bottom_d"],P["bung_top_d"]],neck_inner_d_mm=[P["neck_cone_bottom_d"],P["neck_cone_top_d"]],
                          expected_cone_diametral_interference_mm=.2,filter_bolt_count=6,filter_bolt_circle_mm=88,
                          receiver_bolt_count=6,receiver_bolt_circle_mm=P["receiver_bolt_circle"],filter_disc_diameter_mm=55.2,pocket_diameter_mm=56),
    hardware_clearance=hardware_clearance,physically_tested=False,vacuum_rating_assigned=False),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
