"""Check that every selected model, preview and local documentation link exists."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import ast,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def main():
    cat=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"));parts=cat["parts"]
    assert len(parts)==80 and cat["original_designs_only"]
    expected=set()
    for p in parts:
        assert p["author"]=="nktrois" and p["license"]=="CC-BY-4.0",p["id"]
        assert not p["id"].startswith(("QE","U")),p["id"]
        for ext in ("stl","step","FCStd"):
            f=ROOT/p["path"]/(p["id"]+"."+ext);assert f.is_file() and f.stat().st_size>100,f
            if ext=="stl":expected.add(f.resolve())
        assert (ROOT/p["path"]/"README.md").is_file()
        assert (ROOT/p["path"]/"README.fr.md").is_file()
        assert (ROOT/p["path"]/"source.json").is_file()
        assert (ROOT/p["path"]/"preview.jpg").is_file()
        assert (ROOT/"apercus"/(p["id"]+".png")).is_file()
    assert expected=={p.resolve() for p in ROOT.rglob("*.stl")},"Extra or missing printable STL"
    assert not (ROOT/"communaute").exists()
    assert not any(p.stem.startswith("QE") for p in ROOT.rglob("*")),"Excluded Erlen file"
    mesh=json.loads((ROOT/"verification/mesh-report.json").read_text(encoding="utf-8"))
    cad=json.loads((ROOT/"verification/cad-readback.json").read_text(encoding="utf-8"))
    assert mesh["summary"]["valid_topology"]==80 and cad["checked"]==80
    for r in mesh["parts"]:
        assert hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest()==r["sha256"],r["id"]
    for p in ROOT.rglob("*.py"):ast.parse(p.read_text(encoding="utf-8"),str(p))
    links=[]
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for k,v in attrs:
                if k in ("href","src") and v:links.append((ROOT/"catalogue.html",v))
    parser=Links();parser.feed((ROOT/"catalogue.html").read_text(encoding="utf-8"))
    for p in ROOT.rglob("*.md"):
        for href in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)',p.read_text(encoding="utf-8")):links.append((p,href.strip("<>")))
    checked=0
    for source,href in links:
        u=urlsplit(href)
        if u.scheme or u.netloc or not u.path:continue
        target=(source.parent/unquote(u.path)).resolve()
        assert target.is_relative_to(ROOT.resolve()) and target.exists(),(source,href)
        checked+=1
    html=(ROOT/"catalogue.html").read_text(encoding="utf-8")
    assert html.count("<article ")==80 and "__CARDS__" not in html and "__OPTIONS__" not in html
    result=dict(parts=80,stl=80,step=80,fcstd=80,originals_only=True,local_links_checked=checked,mesh_hashes_current=True,python_syntax_valid=True,excluded_models_absent=True,remote_push_performed=False)
    (ROOT/"verification/package-check.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("PACKAGE_CHECK_OK",json.dumps(result))
    return result
if __name__=="__main__":main()
