"""Artisan en 3D façon pâte à modeler, en colère (planche de style). Usage :
blender -b -P artisan3d.py -- <sortie.png> [encre]
« encre » ajoute des contours noirs (Freestyle) pour le style BD.
"""
import math
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SORTIE = args[0] if args else "//artisan3d.png"
ENCRE = len(args) > 1 and args[1] == "encre"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(nom, couleur, rough=0.55, sss=0.0):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*couleur, 1)
    b.inputs["Roughness"].default_value = rough
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.6, 0.25, 0.15)
    return m


def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


PEAU = mat("peau", srgb("#D9654C"), 0.5, 0.15)          # visage rougi par la colère
PEAU2 = mat("peau2", srgb("#C2533D"), 0.5, 0.1)
CHEV = mat("cheveux", srgb("#2B211C"), 0.7)
VESTE = mat("veste", srgb("#24493B"), 0.6)
ORANGE = mat("orange", srgb("#E8650F"), 0.4)
BLANC = mat("blanc", srgb("#F4F1EC"), 0.35)
NOIR = mat("noir", srgb("#1A1210"), 0.3)
BOUCHE = mat("bouche", srgb("#4A1C14"), 0.6)
LANGUE = mat("langue", srgb("#C2564A"), 0.5)
JEAN = mat("jean", srgb("#1D2B33"), 0.7)
PAPIER = mat("papier", srgb("#F2EFE8"), 0.6)
VAPEUR = mat("vapeur", srgb("#EDEDED"), 0.9)


def sphere(nom, loc, ech, m, rot=(0, 0, 0), sub=2):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = nom
    o.scale = ech
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def membre(nom, a, b, r, m):
    """Segment arrondi entre deux points (capsule)."""
    ax, ay, az = a
    bx, by, bz = b
    L = math.dist(a, b)
    mid = ((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=r, depth=L, location=mid)
    o = bpy.context.object
    o.name = nom
    d = (bx - ax, by - ay, bz - az)
    o.rotation_mode = "QUATERNION"
    from mathutils import Vector
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    bev = o.modifiers.new("arrondi", "BEVEL")
    bev.width = r * 0.9
    bev.segments = 8
    o.modifiers.new("lisse", "SUBSURF").levels = 2
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    sphere(nom + "_a", a, (r, r, r), m)
    sphere(nom + "_b", b, (r, r, r), m)
    return o


def boite(nom, loc, dim, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = nom
    o.scale = (dim[0] / 2, dim[1] / 2, dim[2] / 2)
    bev = o.modifiers.new("arrondi", "BEVEL")
    bev.width = min(dim) * 0.45
    bev.segments = 6
    bev.affect = "EDGES"
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


# Jambes et chaussures
membre("jambeG", (-0.22, 0, 0.15), (-0.22, 0, 0.95), 0.17, JEAN)
membre("jambeD", (0.22, 0, 0.15), (0.22, 0, 0.95), 0.17, JEAN)
sphere("chG", (-0.22, -0.08, 0.08), (0.2, 0.28, 0.11), CHEV)
sphere("chD", (0.22, -0.08, 0.08), (0.2, 0.28, 0.11), CHEV)
# Corps : veste de travail avec bande orange
corps = sphere("corps", (0, 0, 1.45), (0.55, 0.38, 0.62), VESTE)
bande = sphere("bande", (0, 0, 1.25), (0.565, 0.395, 0.07), ORANGE)
sphere("col", (0, -0.2, 1.98), (0.18, 0.12, 0.1), BLANC)
# Bras levés au ciel (colère)
membre("brasG", (-0.48, 0, 1.85), (-0.95, -0.05, 2.75), 0.13, VESTE)
membre("brasD", (0.48, 0, 1.85), (0.95, -0.05, 2.75), 0.13, VESTE)
# sphere("bandeBG", (-0.8, -0.03, 2.45), (0.145, 0.145, 0.06), ORANGE, rot=(0, math.radians(28), 0))
# sphere("bandeBD", (0.8, -0.03, 2.45), (0.145, 0.145, 0.06), ORANGE, rot=(0, math.radians(-28), 0))
sphere("poingG", (-1.0, -0.06, 2.9), (0.16, 0.16, 0.16), PEAU)
sphere("poingD", (1.0, -0.06, 2.9), (0.16, 0.16, 0.16), PEAU)
# Cou et tête
membre("cou", (0, 0, 1.95), (0, 0, 2.15), 0.13, PEAU2)
tete = sphere("tete", (0, 0, 2.55), (0.42, 0.4, 0.5), PEAU)
sphere("oreilleG", (-0.42, 0.02, 2.55), (0.07, 0.05, 0.11), PEAU2)
sphere("oreilleD", (0.42, 0.02, 2.55), (0.07, 0.05, 0.11), PEAU2)
sphere("cheveux", (0, 0.04, 2.78), (0.44, 0.42, 0.33), CHEV)
sphere("nez", (0, -0.4, 2.52), (0.07, 0.07, 0.08), PEAU2)
# Yeux plissés de colère et sourcils froncés
for c in (-1, 1):
    sphere(f"oeil{c}", (0.15 * c, -0.35, 2.66), (0.075, 0.04, 0.05), BLANC)
    sphere(f"pupille{c}", (0.14 * c, -0.385, 2.655), (0.035, 0.02, 0.035), NOIR)
    boite(f"sourcil{c}", (0.15 * c, -0.37, 2.77), (0.17, 0.05, 0.045), CHEV, rot=(0, math.radians(-24 * c), 0))
# Bouche grande ouverte (il crie)
sphere("bouche", (0, -0.36, 2.34), (0.15, 0.06, 0.11), BOUCHE)
sphere("langue", (0, -0.39, 2.29), (0.08, 0.03, 0.04), LANGUE)
boite("dents", (0, -0.405, 2.42), (0.18, 0.02, 0.035), BLANC)
# Vapeur qui sort des oreilles
for c in (-1, 1):
    for k, (dx, dz, r) in enumerate(((0.12, 0.05, 0.07), (0.24, 0.2, 0.1), (0.36, 0.4, 0.13))):
        sphere(f"vap{c}{k}", (c * (0.5 + dx), 0.02, 2.6 + dz), (r, r, r), VAPEUR)
# Papiers qui volent
import random
random.seed(4)
for k in range(9):
    x, z = random.uniform(-1.6, 1.6), random.uniform(1.0, 3.4)
    if abs(x) < 0.7 and 1.6 < z < 3.0:
        x += 1.0 if x > 0 else -1.0
    bpy.ops.mesh.primitive_plane_add(size=0.34, location=(x, random.uniform(-0.6, 0.2), z),
                                     rotation=(math.radians(random.uniform(50, 110)), math.radians(random.uniform(-40, 40)),
                                               math.radians(random.uniform(-60, 60))))
    p = bpy.context.object
    p.scale = (1, 1.3, 1)
    p.data.materials.append(PAPIER)
    p.modifiers.new("ep", "SOLIDIFY").thickness = 0.006

# Fond : un mur chaud, sombre
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 3, 4), rotation=(math.radians(90), 0, 0))
mur = bpy.context.object
mm = mat("mur", srgb("#2A1810"), 0.9)
mur.data.materials.append(mm)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
bpy.context.object.data.materials.append(mat("sol", srgb("#1A110C"), 0.9))

# Lumières : clé chaude, contre-jour orange, débouchage froid doux
def lampe(nom, loc, rot, puissance, couleur, taille):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
    l = bpy.context.object
    l.data.energy = puissance
    l.data.color = couleur
    l.data.size = taille
    return l

lampe("cle", (-2.5, -3.5, 4.2), (math.radians(55), 0, math.radians(-35)), 900, (1, 0.9, 0.8), 3)
lampe("contre", (2.5, 2.0, 3.5), (math.radians(-60), 0, math.radians(140)), 700, (1, 0.45, 0.15), 2)
lampe("bouche", (2.5, -3, 2), (math.radians(75), 0, math.radians(40)), 220, (0.8, 0.9, 1), 4)

# Caméra en portrait
bpy.ops.object.camera_add(location=(0, -7.2, 2.05), rotation=(math.radians(88.5), 0, 0))
cam = bpy.context.object
cam.data.lens = 52
sc.camera = cam

sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = 50
sc.render.film_transparent = False
try:
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 64
except Exception:
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
if ENCRE:
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = 2.2
    ls = sc.view_layers[0].freestyle_settings.linesets[0]
    ls.linestyle.color = (0.05, 0.03, 0.02)
sc.render.filepath = SORTIE
bpy.ops.render.render(write_still=True)
print("RENDU", SORTIE)
