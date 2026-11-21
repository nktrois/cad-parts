"""Package this selected library locally. No Git commands or network actions."""
from pathlib import Path
import hashlib,json,sys,zipfile
from check_package import main as check
ROOT=Path(__file__).resolve().parents[1]
def main():
    check()
    assert len(sys.argv)==2,"Supply a local output directory"
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
    assert not out.is_relative_to(ROOT.resolve()),"Output must be outside the library"
    allowed={".stl",".step",".FCStd",".json",".md",".html",".csv",".py",".png",".jpg",".ply"}
    files=sorted(p for p in ROOT.rglob("*") if p.is_file() and (p.suffix in allowed or p.name=="LICENSE") and "__pycache__" not in p.parts)
    assert len([p for p in files if p.suffix==".stl"])==80
    target=out/"chimie-lab-80-originaux-filtration.zip"
    with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for p in files:z.write(p,"chimie-lab/"+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert not any("communaute/" in n or Path(n).stem.startswith("QE") for n in z.namelist())
    result=dict(file=target.name,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),files=len(files),printable_stl=80,part_step=80,part_fcstd=80,assembly_step=sum(p.suffix==".step" for p in files)-80,assembly_fcstd=sum(p.suffix==".FCStd" for p in files)-80,crc_verified=True,remote_push_performed=False)
    (out/"archive-verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    (out/(target.name+".sha256")).write_text(result["sha256"]+"  "+target.name+"\n",encoding="utf-8")
    print("PACKAGED",json.dumps(result))
if __name__=="__main__":main()
