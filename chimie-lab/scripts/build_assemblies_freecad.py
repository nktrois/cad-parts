"""FreeCADCmd: assemble the exported parts and verify absence of interference."""
from pathlib import Path
import json
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/"catalogue-base.json").read_text(encoding="utf-8"))["parts"]
paths={s["id"]:ROOT/"originaux"/s["family"]/s["id"]/(s["id"]+".step") for s in catalog}
jobs=[dict(id="potence-entonnoir",title="Potence légère : bras Ø55",parts=[("F01",(0,0,0)),("F02",(18,45,3)),("F04",(10,20.5,155.9))]),
      dict(id="porte-pipettes",title="Porte-pipettes : assemblage",parts=[("P01",(0,0,0)),("P02",(75,52.5,3)),("P03",(5,10.5,200.9))])]
result=[]
for job in jobs:
    doc=App.newDocument("Assembly_"+job["id"].replace("-","_"));objects=[]
    for ident,position in job["parts"]:
        shape=Part.Shape();shape.read(str(paths[ident]));shape.translate(App.Vector(*position))
        obj=doc.addObject("PartDesign::Feature",ident);obj.Label=ident;obj.Shape=shape
        objects.append(obj)
    intersections=[]
    for i,a in enumerate(objects):
        for b in objects[i+1:]:
            common=a.Shape.common(b.Shape)
            volume=common.Volume
            intersections.append(dict(parts=[a.Name,b.Name],intersection_mm3=round(volume,9)))
            assert volume<1e-4, (job["id"],a.Name,b.Name,volume)
    doc.recompute()
    out=ROOT/"assemblages"/job["id"];out.mkdir(parents=True,exist_ok=True)
    doc.saveAs(str(out/(job["id"]+".FCStd")))
    Part.makeCompound([o.Shape for o in objects]).exportStep(str(out/(job["id"]+".step")))
    result.append(dict(id=job["id"],parts=job["parts"],interference_check=intersections,physical_fit_tested=False))
    App.closeDocument(doc.Name)
    print("ASSEMBLY",job["id"],"interference-free",flush=True)
(ROOT/"verification"/"assemblies.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
