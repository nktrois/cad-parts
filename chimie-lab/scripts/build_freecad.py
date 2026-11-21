"""Run with FreeCADCmd. Regenerate original solids, FCStd, STEP and STL.

Dimensions are read from ../catalogue.json. FCStd files contain the resulting
solid and metadata; edit JSON and rerun this script to regenerate geometry.
"""
from pathlib import Path
import json, math, os, sys, time, traceback
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
V = App.Vector
EPS = 0.1


def box(x,y,z,at=(0,0,0)):
    return Part.makeBox(x,y,z,V(*at))


def cyl(radius,height,at=(0,0,0),axis=(0,0,1)):
    return Part.makeCylinder(radius,height,V(*at),V(*axis))


def join(shapes):
    out = shapes[0]
    for shape in shapes[1:]:
        out = out.fuse(shape)
    return out.removeSplitter()


def cut_many(shape,tools):
    if tools:
        shape = shape.cut(Part.makeCompound(tools))
    return shape.removeSplitter()


def rounded_box(x,y,z,r=3):
    if r<=0:
        return box(x,y,z)
    return join([box(x-2*r,y,z,(r,0,0)),box(x,y-2*r,z,(0,r,0))]+
                [cyl(r,z,(cx,cy,0)) for cx in (r,x-r) for cy in (r,y-r)])


def rack(p,square=False):
    d = p.get("side",p.get("diameter"))
    nx,ny,pitch,edge,h,b = (p[k] for k in ("nx","ny","pitch","edge","height","bottom"))
    lx=(nx-1)*pitch+d+2*edge; ly=(ny-1)*pitch+d+2*edge
    shape=rounded_box(lx,ly,h,3)
    tools=[]
    for i in range(nx):
        for j in range(ny):
            x=edge+d/2+i*pitch; y=edge+d/2+j*pitch
            if square:
                tools.append(box(d,d,h-b+EPS,(x-d/2,y-d/2,b)))
            else:
                tools.append(cyl(d/2,h-b+EPS,(x,y,b)))
                tools.append(Part.makeCone(d/2,d/2+0.65,0.9,V(x,y,h-0.8)))
            tools.append(cyl(p["drain"]/2,b+2*EPS,(x,y,-EPS)))
    return cut_many(shape,tools)


def bottle_base(p):
    d,w,b,rh,m=(p[k] for k in ("diameter","wall","bottom","ring_height","margin"))
    side=d+2*m
    base=rounded_box(side,side,b,6)
    outer=cyl(d/2+w,rh,(side/2,side/2,b-EPS))
    ring=outer.cut(cyl(d/2,rh+2*EPS,(side/2,side/2,b-2*EPS)))
    return join([base,ring])


def stand_base(p):
    l,w,h,s,depth=(p[k] for k in ("length","width","height","socket","depth"))
    shape=rounded_box(l,w,h,9)
    x=p.get("socket_x",28); y=w/2
    return shape.cut(box(s,s,depth+EPS,(x-s/2,y-s/2,h-depth))).removeSplitter()


def stand_post(p):
    s,h,bt,tt,th=(p[k] for k in ("side","height","bottom_tenon","top_tenon","tenon_height"))
    return join([box(bt,bt,th,((s-bt)/2,(s-bt)/2,0)),
                 box(s,s,h,(0,0,th-EPS)),
                 box(tt,tt,th+EPS,((s-tt)/2,(s-tt)/2,th+h-2*EPS))])


def funnel_arm(p):
    d,w,t,s=(p[k] for k in ("diameter","wall","thickness","socket"))
    ro=d/2+w; cx=105; cy=ro+3
    ring=cyl(ro,t,(cx,cy,0))
    beam=box(cx,32,t,(0,cy-16,0))
    pad=box(36,40,t,(0,cy-20,0))
    shape=join([ring,beam,pad])
    return cut_many(shape,[cyl(d/2,t+2*EPS,(cx,cy,-EPS)),
                           box(s,s,t+2*EPS,(18-s/2,cy-s/2,-EPS))])


def pipette_comb(p):
    l,w,t,d,n,s=(p[k] for k in ("length","width","thickness","slot","slots","socket"))
    shape=rounded_box(l,w,t,4)
    tools=[]
    for i in range(n):
        x=16+i*(l-32)/(n-1)
        tools += [cyl(d/2,t+2*EPS,(x,22,-EPS)),box(d,22,t+2*EPS,(x-d/2,0,-EPS))]
    # Post at the rear, clear of the pipette slots.
    tools.append(box(s,s,t+2*EPS,(l/2-s/2,w-13-s/2,-EPS)))
    return cut_many(shape,tools)


def drying_rack(p):
    n,g,f,l,h,b=(p[k] for k in ("slots","gap","fin","length","height","base"))
    width=n*g+(n+1)*f+12
    return join([rounded_box(width,l,b,3)]+
                [box(f,l-12,h,(6+i*(g+f),6,b-EPS)) for i in range(n+1)])


def rod_rest(p):
    n,d,pitch,l,w,h=(p[k] for k in ("count","diameter","pitch","length","width","height"))
    shape=join([rounded_box(l,w,4,4),box(l,12,h-4,(0,7,4-EPS)),box(l,12,h-4,(0,w-19,4-EPS))])
    start=(l-(n-1)*pitch)/2
    return cut_many(shape,[cyl(d/2,w+2*EPS,(start+i*pitch,-EPS,h),(0,1,0)) for i in range(n)])


def probe_plate(p):
    d,t,holes=(p[k] for k in ("diameter","thickness","holes"))
    shape=cyl(d/2,t,(d/2,d/2,0))
    rr=d*0.26
    tools=[cyl(9,t+2*EPS,(d/2,d/2,-EPS))]
    for i,hd in enumerate(holes):
        a=2*math.pi*i/len(holes)
        tools.append(cyl(hd/2,t+2*EPS,(d/2+rr*math.cos(a),d/2+rr*math.sin(a),-EPS)))
    # Permanent edge vent prevents the plate being mistaken for a sealed lid.
    tools.append(box(8,d/2,t+2*EPS,(d/2-4,d/2,-EPS)))
    return cut_many(shape,tools)


def tube_comb(p):
    n,d,pitch,w,h=(p[k] for k in ("count","diameter","pitch","width","height"))
    l=(n-1)*pitch+d+16
    shape=rounded_box(l,w,h,3)
    tools=[]
    for i in range(n):
        x=8+d/2+i*pitch
        tools += [cyl(d/2,h+2*EPS,(x,w/2,-EPS)),box(d,w/2,h+2*EPS,(x-d/2,0,-EPS))]
    return cut_many(shape,tools)


def tube_bend(p):
    d,r,h,w=(p[k] for k in ("diameter","radius","height","wall"))
    outer=r+d/2+w; inner=r-d/2-w
    ring=cyl(outer,h).cut(cyl(inner,h+2*EPS,(0,0,-EPS)))
    quarter=ring.common(box(outer+EPS,outer+EPS,h+2*EPS,(0,0,-EPS)))
    groove=Part.makeTorus(r,d/2,V(0,0,h),V(0,0,1),0,360,90)
    return quarter.cut(groove).removeSplitter()


def tray(p):
    l,w,h,t,b,n=(p[k] for k in ("length","width","height","wall","bottom","dividers"))
    shape=rounded_box(l,w,h,4)
    inside=box(l-2*t,w-2*t,h-b+EPS,(t,t,b))
    shape=shape.cut(inside)
    if n:
        shape=join([shape]+[box(t,w-2*t,h-b,(i*l/(n+1)-t/2,t,b-EPS)) for i in range(1,n+1)])
    return shape.removeSplitter()


def scoop(p):
    d,h,w,handle=(p[k] for k in ("diameter","height","wall","handle"))
    cx=handle+d/2; cy=d/2
    bowl=cyl(d/2,h,(cx,cy,0)).cut(cyl(d/2-w,h-w+EPS,(cx,cy,w)))
    grip=box(handle+2,12,3,(0,cy-6,0))
    return join([bowl,grip])


def cup(p):
    d,h,w,b=(p[k] for k in ("diameter","height","wall","bottom"))
    shape=cyl(d/2,h,(d/2,d/2,0))
    return shape.cut(cyl(d/2-w,h-b+EPS,(d/2,d/2,b))).removeSplitter()


def funnel(p):
    d,od,di,h,sh,w=(p[k] for k in ("diameter","stem_od","stem_id","height","stem_height","wall"))
    outer=Part.makeCone(od/2,d/2,h,V(d/2,d/2,sh-EPS))
    stem=cyl(od/2,sh,(d/2,d/2,0))
    shape=join([outer,stem])
    bore=cyl(di/2,sh+2*EPS,(d/2,d/2,-EPS))
    cone=Part.makeCone(di/2,d/2-w,h+EPS,V(d/2,d/2,sh-EPS))
    return cut_many(shape,[bore,cone])


def bottle_tag(p):
    d,w,t,l,tw=(p[k] for k in ("diameter","wall","thickness","tab_length","tab_width"))
    ro=d/2+w; cx=ro; cy=max(ro,tw/2)
    ring=cyl(ro,t,(cx,cy,0)).cut(cyl(d/2,t+2*EPS,(cx,cy,-EPS)))
    tab=box(l+3,tw,t,(cx+ro-3,cy-tw/2,0))
    shape=join([ring,tab])
    return shape.cut(cyl(2,t+2*EPS,(cx+ro+l-6,cy,-EPS))).removeSplitter()


def gauge(p):
    ds=p["diameters"]; t=p["thickness"]; pitch=26
    nx=5; ny=2; l=nx*pitch+8; w=ny*pitch+8
    shape=rounded_box(l,w,t,4)
    tools=[]
    for i,d in enumerate(ds):
        tools.append(cyl(d/2,t+2*EPS,(17+(i%nx)*pitch,17+(i//nx)*pitch,-EPS)))
    return cut_many(shape,tools)


def fit_coupon(p):
    ss=p["sockets"]; t=p["thickness"]; peg=p["peg"]
    l=138; w=38
    shape=rounded_box(l,w,t,3)
    tools=[box(s,s,t+2*EPS,(7+i*33,8,-EPS)) for i,s in enumerate(ss)]
    shape=cut_many(shape,tools)
    return join([shape,box(peg,peg,12,(112,9,t-EPS))])


BUILDERS={"rack":rack,"square_rack":lambda p:rack(p,True),"bottle_base":bottle_base,
          "stand_base":stand_base,"stand_post":stand_post,"funnel_arm":funnel_arm,
          "pipette_comb":pipette_comb,"drying_rack":drying_rack,"rod_rest":rod_rest,
          "probe_plate":probe_plate,"tube_comb":tube_comb,"tube_bend":tube_bend,
          "tray":tray,"scoop":scoop,"cup":cup,"funnel":funnel,
          "bottle_tag":bottle_tag,"gauge":gauge,"fit_coupon":fit_coupon}


def main():
    catalog=json.loads((ROOT/"catalogue-base.json").read_text(encoding="utf-8"))
    wanted=set(os.environ.get("LAB_PARTS","").split(","))-{ "" }
    report=[]; start=time.time()
    for spec in catalog["parts"]:
        if wanted and spec["id"] not in wanted:
            continue
        tick=time.time(); ident=spec["id"]
        doc=None
        try:
            shape=BUILDERS[spec["kind"]](spec["parameters"])
            if not shape.isValid() or len(shape.Solids)!=1 or shape.Volume<=0:
                raise ValueError(f"Invalid solid: valid={shape.isValid()}, solids={len(shape.Solids)}, volume={shape.Volume}")
            bb=shape.BoundBox
            shape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
            bb=shape.BoundBox
            dims=[bb.XLength,bb.YLength,bb.ZLength]
            if any(v>240.01 for v in dims):
                raise ValueError(f"Oversize for library margin: {dims}")
            out=ROOT/"originaux"/spec["family"]/ident
            out.mkdir(parents=True,exist_ok=True)
            doc=App.newDocument("Lab_"+ident)
            obj=doc.addObject("PartDesign::Feature","Solid")
            obj.Label=spec["title"]
            obj.Shape=shape
            for name,value in [("Identifiant",ident),("Usage",spec["usage"]),("Matiere",spec["material"]),
                               ("ParametresJSON",json.dumps(spec["parameters"],ensure_ascii=False)),
                               ("Regeneration","Modifier catalogue-base.json puis executer scripts/build_freecad.py"),
                               ("Qualification","Geometrie numerique controlee ; aucune impression physique realisee")]:
                obj.addProperty("App::PropertyString",name,"Documentation")
                setattr(obj,name,value)
            doc.recompute()
            doc.saveAs(str(out/(ident+".FCStd")))
            shape.exportStep(str(out/(ident+".step")))
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.10,AngularDeflection=0.12,Relative=False)
            mesh.write(str(out/(ident+".stl")))
            if not mesh.isSolid():
                raise ValueError("STL mesh is not closed according to FreeCAD")
            mb=mesh.BoundBox
            mesh_dims=[mb.XLength,mb.YLength,mb.ZLength]
            item=dict(id=ident,title=spec["title"],path=out.relative_to(ROOT).as_posix(),
                      dimensions_mm=[round(v,3) for v in mesh_dims],
                      cad_bounds_conservative_mm=[round(v,3) for v in dims],solid_valid=True,solids=1,
                      volume_mm3=round(shape.Volume,3),facets=mesh.CountFacets,
                      freecad_mesh_solid=mesh.isSolid(),seconds=round(time.time()-tick,2))
            report.append(item)
            print("OK",ident,item["dimensions_mm"],item["facets"],flush=True)
        except Exception as exc:
            report.append(dict(id=ident,error=str(exc)))
            print("ERROR",ident,repr(exc),flush=True)
            traceback.print_exc()
        finally:
            if doc:
                App.closeDocument(doc.Name)
    (ROOT/"verification").mkdir(exist_ok=True)
    (ROOT/"verification"/"base-build.json").write_text(json.dumps(dict(freecad_version=App.Version(),linear_deflection_mm=0.10,angular_deflection_rad=0.12,elapsed_seconds=round(time.time()-start,2),parts=report),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    failures=[r for r in report if "error" in r]
    print(f"Finished: {len(report)-len(failures)}/{len(report)} valid solids in {time.time()-start:.1f}s",flush=True)
    if failures:
        raise RuntimeError(f"{len(failures)} build failures")


# FreeCADCmd evaluates Python files in its own module namespace.
main()
