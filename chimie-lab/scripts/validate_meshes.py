"""Independent STL topology and dimensions checks (Python + NumPy).

This is a geometry check, not a physical print, watertightness or chemical test.
"""
from pathlib import Path
import hashlib, json, re, struct, sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def read_stl(path):
    data=Path(path).read_bytes()
    if len(data)>=84:
        count=struct.unpack_from("<I",data,80)[0]
        if len(data)==84+50*count:
            dtype=np.dtype([("normal","<f4",(3,)),("v","<f4",(3,3)),("attr","<u2")])
            return np.frombuffer(data,offset=84,count=count,dtype=dtype)["v"].astype(np.float64)
    vals=re.findall(rb"vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)",data)
    if not vals or len(vals)%3:
        raise ValueError("Invalid or empty STL")
    return np.asarray(vals,dtype=np.float64).reshape((-1,3,3))


def analyze(path):
    triangles=read_stl(path)
    if not np.isfinite(triangles).all():
        raise ValueError("NaN or infinity in STL")
    # Weld only positions to 0.00001 mm; no mesh repair or geometry change.
    vertices,inv=np.unique(np.round(triangles.reshape((-1,3)),5),axis=0,return_inverse=True)
    faces=inv.reshape((-1,3))
    cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
    degenerate=int(np.sum(np.linalg.norm(cross,axis=1)<1e-9))
    edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    sorted_edges=np.sort(edges,axis=1)
    unique_edges,einv,ecount=np.unique(sorted_edges,axis=0,return_inverse=True,return_counts=True)
    balance=np.bincount(einv,weights=np.where(edges[:,0]<edges[:,1],1,-1),minlength=len(unique_edges))
    parent=np.arange(len(vertices))
    def root(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]];a=parent[a]
        return a
    for a,b in unique_edges:
        ra,rb=root(int(a)),root(int(b))
        if ra!=rb:
            parent[rb]=ra
    components=len({root(i) for i in range(len(vertices))})
    dims=vertices.max(axis=0)-vertices.min(axis=0)
    volume=float(np.einsum("ij,ij->i",triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()/6)
    _,dupcounts=np.unique(np.sort(faces,axis=1),axis=0,return_counts=True)
    duplicates=int(np.sum(dupcounts-1))
    boundary=int(np.sum(ecount==1));nonmanifold=int(np.sum(ecount>2));badwinding=int(np.sum(balance!=0))
    valid=bool(boundary==0 and nonmanifold==0 and badwinding==0 and degenerate==0 and duplicates==0 and volume>0)
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                facets=len(faces),vertices=len(vertices),dimensions_mm=[round(float(v),4) for v in dims],
                minimum_mm=[round(float(v),4) for v in vertices.min(axis=0)],
                signed_volume_mm3=round(volume,4),boundary_edges=boundary,nonmanifold_edges=nonmanifold,
                inconsistent_edges=badwinding,degenerate_faces=degenerate,duplicate_faces=duplicates,components=components,
                topology_valid=valid,fits_creator_5_pro=bool(np.all(dims<=256.0001)),
                within_240mm_margin=bool(np.all(dims<=240.0001)),
                max_dimension_mm=round(float(dims.max()),4))

def main():
    catalogue=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"))["parts"]
    report=[]
    for p in catalogue:
        path=ROOT/p["path"]/(p["id"]+".stl");r=analyze(path);r["id"]=p["id"]
        assert r["topology_valid"] and r["components"]==1 and r["within_240mm_margin"],r
        assert max(abs(a-b) for a,b in zip(r["dimensions_mm"],p["dimensions_mm"]))<.01,p["id"]
        report.append(r);print("MESH_OK",p["id"],r["dimensions_mm"],flush=True)
    assert len(report)==80
    summary=dict(originals=len(report),valid_topology=len(report),one_component=len(report),fit_printer=sum(r["fits_creator_5_pro"] for r in report),within_240mm_margin=sum(r["within_240mm_margin"] for r in report),physically_printed=0,chemical_tests=0,leak_tests=0,vacuum_tests=0,scope="Numerical STL topology, winding, dimensions; no slicing or physical qualification.")
    (ROOT/"verification"/"mesh-report.json").write_text(json.dumps(dict(summary=summary,parts=report),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
