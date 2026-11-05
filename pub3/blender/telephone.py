"""Téléphone 3D réaliste qui tourne dans le vide, l'écran joue la vraie capture du site (ecran/sombre).
blender -b -P telephone.py -- <dossier_sortie> [nb_images] [pourcentage]"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
SORTIE = args[0]
N = int(args[1]) if len(args) > 1 else 120
PCT = int(args[2]) if len(args) > 2 else 100
VIDEO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ECRAN = os.path.join(VIDEO, "pub2", "ecran", "sombre", "ecran_0001.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, N
sc.render.fps = 30

LW, LH, EP, R = 0.75, 1.56, 0.085, 0.12  # largeur, hauteur, épaisseur, rayon des coins


def rect_arrondi(w, h, r, seg=14):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def objet(nom, me):
    o = bpy.data.objects.new(nom, me)
    sc.collection.objects.link(o)
    return o


def mat(nom, couleur, metal=0.0, rug=0.4, emis=None, force=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*couleur, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rug
    if emis:
        b.inputs["Emission Color"].default_value = (*emis, 1)
        b.inputs["Emission Strength"].default_value = force
    return m


# ——— le corps : rectangle arrondi extrudé, chanfrein sur le pourtour ———
me = bpy.data.meshes.new("corps")
bm = bmesh.new()
vs = [bm.verts.new((x, y, -EP / 2)) for x, y in rect_arrondi(LW, LH, R)]
f = bm.faces.new(vs)
ext = bmesh.ops.extrude_face_region(bm, geom=[f])
for v in ext["geom"]:
    if isinstance(v, bmesh.types.BMVert):
        v.co.z += EP
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me)
corps = objet("corps", me)
bev = corps.modifiers.new("chanfrein", "BEVEL")
bev.width, bev.segments, bev.limit_method, bev.angle_limit = 0.028, 6, "ANGLE", math.radians(40)
for p in me.polygons:
    p.use_smooth = True
corps.modifiers.new("lisse", "WEIGHTED_NORMAL")
cadre = mat("titane", (0.55, 0.52, 0.5), 1.0, 0.22)
dos = mat("verre_dos", (0.015, 0.015, 0.02), 0.0, 0.18)
me.materials.append(cadre)
me.materials.append(dos)
for p in me.polygons:
    p.material_index = 1 if p.normal.z < -0.9 else 0

# ——— la vitre noire de face et l'écran ———
def plaque(nom, w, h, r, z):
    m = bpy.data.meshes.new(nom)
    b = bmesh.new()
    vs = [b.verts.new((x, y, z)) for x, y in rect_arrondi(w, h, r)]
    b.faces.new(vs)
    uv = b.loops.layers.uv.new()
    for fa in b.faces:
        for l in fa.loops:
            l[uv].uv = (l.vert.co.x / w + 0.5, l.vert.co.y / h + 0.5)
    b.to_mesh(m)
    return objet(nom, m)


vitre = plaque("vitre", LW - 0.03, LH - 0.03, R - 0.015, EP / 2 + 0.001)
vitre.data.materials.append(mat("vitre", (0.0, 0.0, 0.0), 0.0, 0.05))
ecran = plaque("ecran", LW - 0.075, (LW - 0.075) * 1914 / 897, R - 0.04, EP / 2 + 0.0015)

m = bpy.data.materials.new("ecran")
m.use_nodes = True
nt = m.node_tree
nt.nodes.clear()
tex = nt.nodes.new("ShaderNodeTexImage")
img = bpy.data.images.load(ECRAN)
img.source = "SEQUENCE"
tex.image = img
tex.image_user.frame_duration = 375
tex.image_user.frame_start = 1
tex.image_user.frame_offset = 0
tex.image_user.use_auto_refresh = True
em = nt.nodes.new("ShaderNodeEmission")
em.inputs["Strength"].default_value = 3.2
gl = nt.nodes.new("ShaderNodeBsdfGlossy")
gl.inputs["Roughness"].default_value = 0.04
fr = nt.nodes.new("ShaderNodeFresnel")
fr.inputs["IOR"].default_value = 1.15
mix = nt.nodes.new("ShaderNodeMixShader")
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tex.outputs["Color"], em.inputs["Color"])
nt.links.new(fr.outputs[0], mix.inputs[0])
nt.links.new(em.outputs[0], mix.inputs[1])
nt.links.new(gl.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs[0])
ecran.data.materials.append(m)

# ——— le bloc photo au dos ———
bpy.ops.mesh.primitive_cube_add(size=1, location=(-LW / 2 + 0.2, LH / 2 - 0.2, -EP / 2 - 0.008))
bloc = bpy.context.object
bloc.scale = (0.3, 0.3, 0.02)
bpy.ops.object.transform_apply(scale=True)
bv = bloc.modifiers.new("b", "BEVEL")
bv.width, bv.segments = 0.07, 8
bloc.data.materials.append(mat("bloc", (0.03, 0.03, 0.035), 0.0, 0.12))
for dx, dy in ((-0.065, 0.065), (0.065, 0.0), (-0.065, -0.065)):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.03, location=(-LW / 2 + 0.2 + dx, LH / 2 - 0.2 + dy, -EP / 2 - 0.025))
    o = bpy.context.object
    o.data.materials.append(mat("objectif", (0.005, 0.005, 0.01), 0.3, 0.05))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.047, minor_radius=0.006, location=o.location)
    bpy.context.object.data.materials.append(cadre)

# ——— tout le téléphone sous un pivot animé ———
pivot = bpy.data.objects.new("pivot", None)
sc.collection.objects.link(pivot)
for o in list(sc.objects):
    if o is not pivot and o.type == "MESH":
        o.parent = pivot


def ease(t):
    return 1 - (1 - t) ** 3


T_ARRIVEE = min(54, N)  # le téléphone se retourne vers nous
for fr_ in range(1, N + 1, 2):
    t = min(1.0, (fr_ - 1) / (T_ARRIVEE - 1))
    e = ease(t)
    rest = (fr_ - T_ARRIVEE) / 30 if fr_ > T_ARRIVEE else 0
    pivot.rotation_euler = (math.radians(-12 * (1 - e) + 4 * math.sin(rest * 1.3)),
                            math.radians(-200 * (1 - e) + 7 * math.sin(rest * 0.9)),
                            math.radians(-25 * (1 - e) - 3 + 1.5 * math.sin(rest * 1.1)))
    pivot.location = (0, 0.04 * math.sin(fr_ / 30 * 1.6), -1.6 * (1 - e))
    pivot.keyframe_insert("rotation_euler", frame=fr_)
    pivot.keyframe_insert("location", frame=fr_)

# ——— poussière lumineuse (bokeh) ———
random.seed(5)
poussiere = mat("poussiere", (1, 0.5, 0.15), emis=(1, 0.45, 0.12), force=6)
froide = mat("poussiere2", (0.8, 0.85, 1), emis=(0.8, 0.85, 1), force=3)
for k in range(110):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.004, 0.012),
                                          location=(random.uniform(-2.2, 2.2), random.uniform(-3, 3), random.uniform(-3.5, 1.6)))
    o = bpy.context.object
    o.data.materials.append(poussiere if k % 3 else froide)
    o.keyframe_insert("location", frame=1)
    o.location.z += random.uniform(0.05, 0.25)
    o.location.y += random.uniform(0.05, 0.2)
    o.keyframe_insert("location", frame=N)

# ——— lumière : contre-jour orange, contre-jour froid, bande blanche qui balaie le verre ———
def lampe(nom, typ, loc, rot, energie, couleur, taille=1.0, taille_y=None):
    l = bpy.data.lights.new(nom, typ)
    l.energy, l.color = energie, couleur
    if typ == "AREA":
        l.shape = "RECTANGLE"
        l.size, l.size_y = taille, taille_y or taille
    o = bpy.data.objects.new(nom, l)
    o.location, o.rotation_euler = loc, [math.radians(a) for a in rot]
    sc.collection.objects.link(o)
    return o


lampe("orange", "AREA", (2.2, 0.6, -1.2), (0, 115, 15), 900, (1, 0.42, 0.1), 1.5)
lampe("froide", "AREA", (-2.4, 1.2, -0.6), (0, -110, 0), 420, (0.55, 0.7, 1), 1.2)
bande = lampe("bande", "AREA", (-1.5, 2.6, 2.4), (-40, -25, 0), 220, (1, 0.97, 0.92), 0.12, 4.0)
bande.keyframe_insert("location", frame=1)
bande.location.x = 1.8
bande.keyframe_insert("location", frame=N)
lampe("face", "AREA", (0, -0.5, 3.5), (0, 0, 0), 60, (1, 0.9, 0.82), 2.0)

w = bpy.data.worlds.new("monde")
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.002, 0.002, 0.004, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
vol = w.node_tree.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value = 0.004
w.node_tree.links.new(vol.outputs[0], w.node_tree.nodes["World Output"].inputs["Volume"])
sc.world = w

# ——— caméra : légère poussée, profondeur de champ ———
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 60
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 2.0
cam.location = (0, 0, 4.7)
cam.keyframe_insert("location", frame=1)
cam.location = (0, 0, 4.0)
cam.keyframe_insert("location", frame=N)
foyer = bpy.data.objects.new("foyer", None)
sc.collection.objects.link(foyer)
foyer.parent = pivot
cam.data.dof.focus_object = foyer

sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 32
sc.eevee.use_raytracing = True
sc.render.use_motion_blur = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = PCT
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.render.film_transparent = False
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(SORTIE, "tel_")
for o in sc.objects:
    if o.type == "MESH" and o.name.startswith(("Cube", "Cyl", "Tor")):
        print("POS", o.name, tuple(round(v, 3) for v in o.location), o.parent and o.parent.name)
if os.environ.get("IMAGES"):
    for fr_ in map(int, os.environ["IMAGES"].split(",")):
        sc.frame_set(fr_)
        sc.render.filepath = os.path.join(SORTIE, f"tel_{fr_:04d}.png")
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("FINI", SORTIE)
