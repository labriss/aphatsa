"""Aperçu des personnages GLB : rendu de face + liste des animations. blender -b -P apercu_modeles.py -- <dossier>"""
import glob
import math
import os
import sys

import bpy
from mathutils import Vector

dossier = sys.argv[sys.argv.index("--") + 1]
for f in sorted(glob.glob(os.path.join(dossier, "*.glb"))):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=f)
    actions = [a.name for a in bpy.data.actions]
    print("MODELE", os.path.basename(f), "|", ", ".join(actions[:40]))
    meshes = [o for o in sc.objects if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre, h = (mn + mx) / 2, mx.z - mn.z
    bpy.ops.object.camera_add(location=(centre.x, centre.y - h * 2.6, centre.z), rotation=(math.radians(90), 0, 0))
    sc.camera = bpy.context.object
    sc.camera.data.lens = 50
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), math.radians(10), math.radians(-30)))
    bpy.context.object.data.energy = 3.5
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.36, 0.36, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
    sc.world = w
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 400, 700
    sc.render.filepath = os.path.join(dossier, os.path.basename(f)[:-4] + ".png")
    bpy.ops.render.render(write_still=True)
