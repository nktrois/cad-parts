"""Merge selected original model series, without changing their CAD geometry."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
    previous={p["id"]:p for p in read(ROOT/"catalogue.json")["parts"]}
    builds=ROOT/"verification"/"base-build.json"
    build={p["id"]:p for p in read(builds)["parts"]} if builds.exists() else {}
    base=[]
    for source in read(ROOT/"catalogue-base.json")["parts"]:
        p=dict(previous[source["id"]]);p.update(source);p["series"]="atelier"
        if source["id"] in build:
            b=build[source["id"]];p.update(path=b["path"],dimensions_mm=b["dimensions_mm"],volume_material_mm3=b["volume_mm3"])
        base.append(p)
    assert len(base)==45
    parts=base
    for folder,series,family,count in [("recipients-chimiques","recipients","12-recipients",10),("outils-humides","humides","13-outils-humides",8),("filtration","filtration","14-filtration",17)]:
        rows=read(ROOT/folder/"catalogue.json")["parts"];assert len(rows)==count
        for row in rows:
            p=dict(row);p.update(series=series,family=family,path=folder+"/"+row["path"])
            p.setdefault("material_candidate",p.get("material","PP"))
            p.setdefault("chemical_qualified",False);parts.append(p)
    assert len(parts)==80 and len({p["id"] for p in parts})==80
    assert not any(p["id"].startswith(("QE","U")) for p in parts)
    result=dict(units="mm",author="nktrois",license="CC-BY-4.0",original_designs_only=True,parts=parts)
    (ROOT/"catalogue.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"verification").mkdir(exist_ok=True)
    (ROOT/"verification"/"selection.json").write_text(json.dumps(dict(originals=80,series={s:sum(p["series"]==s for p in parts) for s in ["atelier","recipients","humides","filtration"]},excluded_erlenmeyers=["QE100","QE250","QE500","QE1000"],third_party_models=0,remote_push_performed=False),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CONSOLIDATED",len(parts))
if __name__=="__main__":main()
