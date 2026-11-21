"""Render actual meshes. PP blue, TPU orange, dry supports teal; no bitmap invention."""
from pathlib import Path
import json,os,sys
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))
from validate_meshes import read_stl

def material(name,color,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get("Principled BSDF");n.inputs["Base Color"].default_value=(*color,1)
    n.inputs["Roughness"].default_value=.36;n.inputs["Metallic"].default_value=metal
    return m
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine="CYCLES";scene.cycles.device="CPU";scene.cycles.samples=16
scene.cycles.use_denoising=True;scene.cycles.max_bounces=3
scene.render.threads_mode="FIXED";scene.render.threads=6
scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG";scene.view_settings.view_transform="AgX";scene.view_settings.exposure=.8
scene.world.use_nodes=True;scene.world.node_tree.nodes["Background"].inputs[0].default_value=(.78,.83,.88,1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value=.45
mats={"PP":material("PP candidate",(.065,.30,.64)),"TPU":material("TPU candidate",(.95,.30,.045)),"PETG":material("Support sec",(.025,.40,.43)),"METAL":material("Tige commerciale",(.42,.46,.50),.7)}
ground=material("Fond",(.88,.91,.94))
bpy.ops.mesh.primitive_plane_add(size=4000,location=(0,0,-.2));plane=bpy.context.object;plane.data.materials.append(ground)
lights=[]
for name,direction,power in [("Key",(1,-1.5,2.2),1.0),("Fill",(-1.5,-.3,1.6),.6),("Rim",(.8,1.8,1.8),.9)]:
    d=bpy.data.lights.new(name,"AREA");d.shape="DISK";obj=bpy.data.objects.new(name,d);scene.collection.objects.link(obj);lights.append((obj,Vector(direction),power))
cd=bpy.data.cameras.new("Camera");cam=bpy.data.objects.new("Camera",cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type="ORTHO";cd.clip_end=10000
parts=json.loads((ROOT/"catalogue.json").read_text(encoding="utf-8"))["parts"];spec={p["id"]:p for p in parts}
jobs=[]
for p in parts:
    if p["series"]!="filtration":continue
    jobs.append(dict(id=p["id"],parts=[(p["id"],(0,0,0))],canonical=False))
assemblies=json.loads((ROOT/"filtration/verification/assemblages.json").read_text(encoding="utf-8"))["assemblies"]
for a in assemblies:jobs.append(dict(id=a["id"],parts=a["parts"],canonical=True,rod=a["id"]=="station-gravitaire"))
jobs.append(dict(id="coupe-filtration",cut=True,canonical=False,parts=[(i,(0,0,0)) for i in ["FL01","FL02","FL03","FL04","FL05","FL06","FL07","FL09"]]))
wanted=set(os.environ.get("LAB_RENDER","").split(","))-{ "" };done=[]
for job in jobs:
    if wanted and job["id"] not in wanted:continue
    objects=[];allv=[]
    for ident,offset in job["parts"]:
        p=spec[ident]
        if job.get("cut"):
            bpy.ops.wm.ply_import(filepath=str(ROOT/"filtration/illustrations"/("COUPE_"+ident+"_NON_IMPRIMABLE.ply")))
            obj=bpy.context.object;verts=np.asarray([v.co[:] for v in obj.data.vertices],dtype=float)
        else:
            tri=read_stl(ROOT/p["path"]/(ident+".stl"));verts,inv=np.unique(np.round(tri.reshape((-1,3)),5),axis=0,return_inverse=True)
            delta=np.asarray(offset,dtype=float)
            if job["canonical"]:delta-=np.asarray(p["export_origin_shift_mm"])
            verts+=delta
            mesh=bpy.data.meshes.new(ident);mesh.from_pydata(verts.tolist(),[],inv.reshape((-1,3)).tolist());mesh.update()
            obj=bpy.data.objects.new(ident,mesh);scene.collection.objects.link(obj)
        mat=p["material_candidate"].split()[0];obj.data.materials.append(mats.get(mat,mats["PP"]))
        objects.append(obj);allv.append(verts)
    if job.get("rod"):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=6,depth=300,location=(28,97.5,170))
        obj=bpy.context.object;obj.data.materials.append(mats["METAL"]);objects.append(obj)
        allv.append(np.asarray([(22,91.5,20),(34,103.5,320)]))
    v=np.concatenate(allv);lo=v.min(axis=0);hi=v.max(axis=0);center=(lo+hi)/2
    extent=float(np.ptp(v,axis=0).max());distance=max(450,extent*3)
    direction=(1.3,1.8,.9) if job.get("cut") else (1.2,-1.65,1.05)
    if job["id"]=="filtre-eclate":direction=(1.1,-1.8,.55)
    cam.location=Vector(center)+Vector(direction).normalized()*distance
    cam.rotation_euler=(Vector(center)-cam.location).to_track_quat("-Z","Y").to_euler()
    rot=cam.rotation_euler.to_matrix().transposed();projected=np.asarray([(rot@Vector(x-center))[:] for x in v]);span=np.ptp(projected,axis=0)
    cd.ortho_scale=max(span[0],span[1]*(960/720))*1.2
    plane.location.z=lo[2]-.2
    for light,direction,power in lights:
        light.location=Vector(center)+direction*extent;light.data.size=extent*1.4;light.data.energy=extent**2*7*power
        light.rotation_euler=(Vector(center)-light.location).to_track_quat("-Z","Y").to_euler()
    out=ROOT/"apercus"/(job["id"]+".png");scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
    for obj in objects:
        mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    done.append(job["id"]);print("RENDERED",job["id"],flush=True)
(ROOT/"verification"/"render-last-run.json").write_text(json.dumps(dict(engine="Blender Cycles CPU",samples=16,resolution=[960,720],rendered=done,source="Actual printable STL meshes; PLY sections are non-printable illustrations."),indent=2)+"\n",encoding="utf-8")
