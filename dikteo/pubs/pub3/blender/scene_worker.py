"""L'ouvrier 3D (Quaternius, CC0) en colère dans une cuisine le soir. blender -b -P scene_worker.py -- <sortie.png> [encre]"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
SORTIE, ENCRE = args[0], len(args) > 1 and args[1] == "encre"
GLB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(SORTIE))), "modeles3d", "Worker.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
arm = next(o for o in sc.objects if o.type == "ARMATURE")
act = bpy.data.actions.get("Punch_Right") or bpy.data.actions[0]
arm.animation_data_create()
arm.animation_data.action = act
sc.frame_set(int(act.frame_range[0] + (act.frame_range[1] - act.frame_range[0]) * 0.45))
arm.rotation_euler[2] = math.radians(-18)

meshes = [o for o in sc.objects if o.type == "MESH"]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
h = max(p.z for p in pts) - min(p.z for p in pts)
cz = (max(p.z for p in pts) + min(p.z for p in pts)) / 2


def mat(c, r=0.8):
    m = bpy.data.materials.new("m")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = r
    return m


# Décor : mur, table couverte de papiers, papiers qui volent
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, h * 1.2, 0), rotation=(math.radians(90), 0, 0))
bpy.context.object.data.materials.append(mat((0.06, 0.035, 0.02)))
bpy.ops.mesh.primitive_plane_add(size=30)
bpy.context.object.data.materials.append(mat((0.03, 0.02, 0.015)))
bpy.ops.mesh.primitive_cube_add(location=(h * 0.55, h * 0.1, h * 0.25))
t = bpy.context.object
t.scale = (h * 0.35, h * 0.3, h * 0.02)
t.data.materials.append(mat((0.25, 0.14, 0.07), 0.5))
papier = mat((0.9, 0.88, 0.83), 0.6)
random.seed(3)
for k in range(14):
    bpy.ops.mesh.primitive_plane_add(size=h * 0.1, location=(random.uniform(-0.6, 0.9) * h, random.uniform(-0.3, 0.2) * h,
                                                            random.uniform(0.35, 1.15) * h),
                                     rotation=[math.radians(random.uniform(0, 360)) for _ in range(3)])
    bpy.context.object.scale = (1, 1.3, 1)
    bpy.context.object.data.materials.append(papier)

# Lumière : lampe de cuisine chaude au-dessus, contre-jour orange
bpy.ops.object.light_add(type="AREA", location=(-h * 0.4, -h * 0.9, h * 1.6), rotation=(math.radians(35), 0, math.radians(-20)))
bpy.context.object.data.energy, bpy.context.object.data.size = 220 * h * h, h * 0.6
bpy.context.object.data.color = (1, 0.82, 0.6)
bpy.ops.object.light_add(type="AREA", location=(h * 0.8, h * 0.8, h * 1.0), rotation=(math.radians(-70), 0, math.radians(140)))
bpy.context.object.data.energy, bpy.context.object.data.size = 260 * h * h, h * 0.4
bpy.context.object.data.color = (1, 0.42, 0.12)
w = bpy.data.worlds.new("w")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[1].default_value = 0.05
sc.world = w

bpy.ops.object.camera_add(location=(h * 0.15, -h * 2.3, cz * 1.05), rotation=(math.radians(88), 0, math.radians(4)))
sc.camera = bpy.context.object
sc.camera.data.lens = 45
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 64
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = 50
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
if ENCRE:
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = 2.4
    fs = sc.view_layers[0].freestyle_settings
    ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("encre")
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("encre")
    ls.linestyle.color = (0.04, 0.03, 0.02)
sc.render.filepath = SORTIE
bpy.ops.render.render(write_still=True)
print("RENDU", SORTIE)
