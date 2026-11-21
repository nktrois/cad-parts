"""Independent readback of all selected STEP and native FreeCAD documents."""
from pathlib import Path
import json
import FreeCAD as App
import Part
ROOT=Path(__file__).resolve().parents[1]
parts=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"))["parts"]
result=[]
for p in parts:
    ident=p["id"];folder=ROOT/p["path"]
    step=Part.Shape();step.read(str(folder/(ident+".step")))
    doc=App.openDocument(str(folder/(ident+".FCStd")))
    native=[o.Shape for o in doc.Objects if hasattr(o,"Shape") and not o.Shape.isNull()]
    assert len(native)==1 and native[0].isValid() and len(native[0].Solids)==1,ident
    assert step.isValid() and len(step.Solids)==1,ident
    delta=abs(step.Volume-native[0].Volume);tolerance=max(.1,native[0].Volume*1e-5)
    assert delta<tolerance,(ident,delta,tolerance)
    assert abs(native[0].Volume-p["volume_material_mm3"])<max(.01,native[0].Volume*1e-6),ident
    result.append(dict(id=ident,step_valid=True,fcstd_valid=True,one_solid=True,volume_difference_mm3=round(delta,8),comparison_tolerance_mm3=round(tolerance,8)))
    App.closeDocument(doc.Name);print("CAD_READBACK",ident,"OK",flush=True)
(ROOT/"verification"/"cad-readback.json").write_text(json.dumps(dict(checked=len(result),parts=result,physical_tests=False),indent=2)+"\n",encoding="utf-8")
assert len(result)==80
