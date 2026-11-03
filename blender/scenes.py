# Les plans 3D de la pub Fuitéo, construits entièrement en code (aucun modèle téléchargé).
# Usage : blender -b -P scenes.py -- <plan> <image|anim> <sortie> [écran.png | dossier d'écrans]
#   plans : goutte, cuisine_nuit, cuisine_soir, telephone
# Échelle : 1 unité = 10 cm, pour garder des valeurs lisibles.
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
SHOT = ARGS[0] if ARGS else "goutte"
MODE = ARGS[1] if len(ARGS) > 1 else "image"
OUT = Path(ARGS[2] if len(ARGS) > 2 else "out.png").resolve()
SCREEN = ARGS[3] if len(ARGS) > 3 and ARGS[3] != "-" else None
FRAME = int(ARGS[4]) if len(ARGS) > 4 else None
ASSETS = Path(__file__).resolve().parent.parent / "assets"
FPS = 30

# Les couleurs de la marque (src/lib/theme-colors.ts), en linéaire pour Blender.
def srgb(hexa, a=1.0):
    h = hexa.lstrip("#")
    c = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, a)

ORANGE = "#FF7A33"
ORANGE_DEEP = "#F25C14"
NIGHT = "#0E1412"


# ——— Scène et rendu ———

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.fps = FPS
    sc.eevee.taa_render_samples = 48
    sc.eevee.use_raytracing = True
    sc.eevee.use_shadows = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.new("monde")
    world.use_nodes = True
    sc.world = world
    return sc


def world_color(hexa, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb(hexa)
    bg.inputs["Strength"].default_value = strength


def material(name, color="#808080", metallic=0.0, roughness=0.5, transmission=0.0, ior=1.45, emission=None, strength=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = srgb(color)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Coat Weight"].default_value = coat
    if emission:
        b.inputs["Emission Color"].default_value = srgb(emission)
        b.inputs["Emission Strength"].default_value = strength
    return m


def image_material(name, path, emission_strength=0.0, roughness=0.5, gloss=False):
    """Matériau à image : en émission pour un écran, en couleur pour du papier."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    p = Path(path)
    if p.is_dir():
        files = sorted(p.glob("*.png"))
        img = bpy.data.images.load(str(files[0]))
        img.source = "SEQUENCE"
        tex.image_user.frame_duration = len(files)
        tex.image_user.frame_start = 1
        tex.image_user.use_auto_refresh = True
    else:
        img = bpy.data.images.load(str(p))
    tex.image = img
    tex.interpolation = "Cubic"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = roughness
    if emission_strength:
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emission_strength
        b.inputs["Base Color"].default_value = (0, 0, 0, 1)
        nt.links.remove(b.inputs["Base Color"].links[0])
        b.inputs["Coat Weight"].default_value = 1.0 if gloss else 0.0
        b.inputs["Coat Roughness"].default_value = 0.03
    return m


def link(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def box(name, size, loc, mat, bevel=0.0, segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("biseau", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = "NONE"
        smooth(o)
    return link(o, mat)


def cylinder(name, r, depth, loc, mat, rot=(0, 0, 0), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=vertices)
    o = bpy.context.object
    o.name = name
    return link(o, mat)


def area_light(name, loc, target, energy, size, color="#FFFFFF", shape="RECTANGLE", size_y=None):
    bpy.ops.object.light_add(type="AREA", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = energy
    o.data.shape = shape
    o.data.size = size
    o.data.size_y = size_y or size
    o.data.color = srgb(color)[:3]
    aim(o, target)
    return o


def point_light(name, loc, energy, color="#FFFFFF", radius=0.1):
    bpy.ops.object.light_add(type="POINT", location=loc)
    o = bpy.context.object
    o.name = name
    o.data.energy = energy
    o.data.shadow_soft_size = radius
    o.data.color = srgb(color)[:3]
    return o


def aim(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50, fstop=None, focus=None):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    aim(cam, target)
    cam.data.lens = lens
    cam.data.sensor_width = 36
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_distance = focus or (Vector(target) - Vector(loc)).length
    bpy.context.scene.camera = cam
    return cam


def key(obj, path, frame, value, interp="BEZIER"):
    setattr(obj, path, value) if not isinstance(value, tuple) else setattr(obj, path, value)
    obj.keyframe_insert(path, frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fc in iter_fcurves(obj.animation_data.action):
            for kp in fc.keyframe_points:
                if int(kp.co.x) == frame:
                    kp.interpolation = interp


def iter_fcurves(action):
    # Blender 5 : les courbes vivent dans les calques de l'action.
    if hasattr(action, "layers") and action.layers:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
    else:
        yield from getattr(action, "fcurves", [])


def glow_wall(loc, color, strength, size=36, radius=(9, 12), edge=0.75):
    """Un fond lumineux qui s'éteint vers les bords (halo), dans le plan vertical."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=(math.pi / 2, 0, 0))
    glow = bpy.context.object
    gm = bpy.data.materials.new("lueur")
    gm.use_nodes = True
    nt = gm.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = "SPHERICAL"
    mapping = nt.nodes.new("ShaderNodeMapping")
    # Le dégradé sphérique vaut 1 au centre et 0 à une unité : on l'étire au rayon voulu (largeur, hauteur).
    mapping.inputs["Scale"].default_value = (1 / radius[0], 1 / radius[1], 1 / radius[1])
    coord = nt.nodes.new("ShaderNodeTexCoord")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    ramp.color_ramp.elements[0].color = srgb(NIGHT)
    ramp.color_ramp.elements[1].position = edge
    ramp.color_ramp.elements[1].color = srgb(color)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return link(glow, gm)


# ——— Plan 1 : la goutte sous l'écrou ———

def shot_goutte(sc):
    world_color("#05080A", 1.0)
    copper = material("cuivre", "#C27A4A", metallic=1.0, roughness=0.22)
    brass = material("laiton", "#B8955A", metallic=1.0, roughness=0.3)
    water = material("eau", "#FFFFFF", roughness=0.0, transmission=1.0, ior=1.33)
    z = 6.0
    pipe = cylinder("tuyau", 0.55, 30, (0, 0, z), copper, rot=(0, math.pi / 2, 0))
    smooth(pipe)
    # L'écrou tourne d'abord sur son axe (rotation figée), puis se couche : une arête vers nous, deux pans visibles.
    nut = cylinder("ecrou", 0.85, 1.3, (0, 0, z), brass, rot=(0, 0, math.pi / 6), vertices=6)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    nut.rotation_euler = (0, math.pi / 2, 0)
    bev = nut.modifiers.new("biseau", "BEVEL")
    bev.width, bev.segments = 0.06, 3
    for x in (-0.75, 0.75):
        ring = cylinder("bague", 0.68, 0.18, (x, 0, z), brass, rot=(0, math.pi / 2, 0))
        smooth(ring)
    # Une perle d'eau sur l'écrou, puis la goutte qui se forme et tombe.
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, segments=64, ring_count=32, location=(0.1, 0, z - 0.8))
    drop = smooth(link(bpy.context.object, water))
    drop.name = "goutte"
    hang = z - 0.95
    key(drop, "scale", 1, (0.25, 0.25, 0.25))
    key(drop, "location", 1, (0.1, 0, z - 0.78))
    key(drop, "scale", 40, (0.85, 0.85, 1.0))
    key(drop, "location", 40, (0.1, 0, hang))
    key(drop, "scale", 58, (0.8, 0.8, 1.35))
    key(drop, "location", 58, (0.1, 0, hang - 0.25))
    key(drop, "scale", 75, (0.7, 0.7, 1.6))
    key(drop, "location", 75, (0.1, 0, -14), "QUAD")
    # Le cuivre ne brille que s'il a quelque chose à refléter : de longues bandes de lumière froide
    # de chaque côté, une boîte à lumière au-dessus ; derrière, un halo bleuté qui découpe la goutte.
    area_light("bande_g", (-7, -3, z + 1), (0, 0, z), 900, 1.2, "#DCE8FF", size_y=16)
    area_light("bande_d", (7, -2, z - 1), (0, 0, z), 700, 1.2, "#B9D0F5", size_y=16)
    area_light("dessus", (0, -2, z + 8), (0, 0, z), 1400, 10, "#E8F0FF", size_y=4)
    area_light("contre_jour", (0, 8, z - 2), (0, 0, z - 1.5), 600, 4, "#9EC2FF")
    glow_wall((0, 16, z - 2.5), "#22364F", 0.5, size=60, radius=(8, 12), edge=1.0)
    # Un léger trois-quarts : on voit le pan hexagonal de l'écrou, le tuyau fuit en perspective.
    area_light("face_douce", (-5, -12, z + 3), (0, 0, z), 260, 6, "#C9D6E6")
    camera((5.5, -20, z - 3.2), (0.1, 0, z - 1.7), lens=85, fstop=2.8, focus=20.8)
    sc.frame_start, sc.frame_end = 1, 75
    return 48  # l'image clé du storyboard : la goutte prête à tomber


# ——— Plans 2, 3, 9 : la table de cuisine ———

def clock_hands(center, hour, minute):
    """Aiguilles pilotées par un pivot ; renvoie les deux pivots pour l'animation."""
    pivots = []
    dark = material("aiguille", "#1A1D1F", roughness=0.4)
    for length, width, angle in ((0.95, 0.09, hour), (1.35, 0.055, minute)):
        bpy.ops.object.empty_add(location=center)
        pivot = bpy.context.object
        hand = box("aiguille", (width, 0.03, length), (center[0], center[1] - 0.06, center[2] + length / 2 - 0.12), dark)
        hand.parent = pivot
        hand.matrix_parent_inverse = pivot.matrix_world.inverted()
        pivot.rotation_euler = (0, angle, 0)
        pivots.append(pivot)
    return pivots


def angles(h, m):
    return (math.radians((h % 12 + m / 60) * 30), math.radians(m * 6))


def shot_cuisine(sc, soir=False):
    world_color("#0A0E12" if not soir else "#3A3A44", 0.4)
    wood = material("bois", "#3A2A1E", roughness=0.55)
    # Grain du bois : une texture à vagues sur la couleur.
    nt = wood.node_tree
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = 1.2
    wave.inputs["Distortion"].default_value = 6
    wave.bands_direction = "X"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb("#2B1E15")
    ramp.color_ramp.elements[1].color = srgb("#4A3626")
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    box("table", (40, 22, 0.6), (0, 3, -0.3), wood)
    box("mur", (60, 0.4, 40), (0, 12, 18), material("mur", "#2B3431" if not soir else "#C9BFB1", roughness=0.85))

    # L'ordinateur portable, son tableur allumé la nuit, fermé le soir. Tout tient dans le cadre vertical.
    lx = -0.7
    alu = material("alu", "#8E959A", metallic=1.0, roughness=0.45)
    box("clavier", (3.3, 2.3, 0.14), (lx, 2.2, 0.07), alu, bevel=0.05)
    keys = material("touches", "#1C1F22", roughness=0.6)
    box("touches", (2.9, 1.1, 0.02), (lx, 2.55, 0.15), keys)
    bpy.ops.object.empty_add(location=(lx, 3.35, 0.14))
    hinge = bpy.context.object
    lid = box("ecran", (3.3, 0.1, 2.2), (lx, 3.35, 0.14 + 1.1), alu, bevel=0.04)
    lid.parent = hinge
    lid.matrix_parent_inverse = hinge.matrix_world.inverted()
    bpy.ops.mesh.primitive_plane_add(size=1, location=(lx, 3.29, 0.14 + 1.12), rotation=(math.pi / 2, 0, 0))
    panel = bpy.context.object
    panel.scale = (3.05, 1.95, 1)
    link(panel, image_material("tableur", ASSETS / "tableur.png", emission_strength=0 if soir else 1.6))
    panel.parent = hinge
    panel.matrix_parent_inverse = hinge.matrix_world.inverted()
    hinge.rotation_euler = (math.radians(-12) if not soir else math.radians(90), 0, 0)  # le soir, refermé sur le clavier
    if soir:
        panel.hide_render = True

    # Le carnet raturé, le stylo, le café froid.
    nx, ny, nr = 1.45, 0.55, math.radians(-16)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(nx, ny, 0.06), rotation=(0, 0, nr))
    note = bpy.context.object
    note.scale = (1.25, 1.75, 1)
    link(note, image_material("carnet", ASSETS / "carnet.png", roughness=0.8))
    box("dos_carnet", (1.31, 1.81, 0.05), (nx, ny, 0.025), material("couverture", "#24303A", roughness=0.7)).rotation_euler = (0, 0, nr)
    pen = cylinder("stylo", 0.045, 1.3, (2.1, -0.15, 0.1), material("stylo", "#1B1E22", roughness=0.3), rot=(0, math.pi / 2, math.radians(40)))
    smooth(pen)
    if soir:
        # Le soir, plus de paperasse : le carnet et le stylo ont quitté la table.
        for o in (note, pen, bpy.data.objects["dos_carnet"]):
            o.hide_render = True
    ceramic = material("tasse", "#E9ECEC", roughness=0.25, coat=0.5)
    mx, my = 1.75, 3.3
    cup = cylinder("tasse", 0.42, 0.95, (mx, my, 0.475), ceramic)
    sol = cup.modifiers.new("épaisseur", "SOLIDIFY")
    sol.thickness = 0.04
    bm = bmesh.new()
    bm.from_mesh(cup.data)
    top = [f for f in bm.faces if f.normal.z > 0.9]
    bmesh.ops.delete(bm, geom=top, context="FACES")
    bm.to_mesh(cup.data)
    bm.free()
    smooth(cup)
    cylinder("cafe", 0.39, 0.02, (mx, my, 0.62), material("café", "#1E120B", roughness=0.08))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.05, location=(mx + 0.46, my, 0.5), rotation=(math.pi / 2, 0, 0))
    link(smooth(bpy.context.object), ceramic)

    # L'horloge murale, au-dessus de l'ordinateur.
    cx, cz = 0.2, 6.3
    cylinder("cadran", 1.55, 0.12, (cx, 11.75, cz), material("cadran", "#ECEDE8", roughness=0.6), rot=(math.pi / 2, 0, 0))
    rim = cylinder("bord", 1.7, 0.2, (cx, 11.8, cz), material("bord", "#1C1F21", metallic=0.6, roughness=0.35), rot=(math.pi / 2, 0, 0))
    smooth(rim)
    for i in range(12):
        a = math.radians(i * 30)
        long = i % 3 == 0
        r = 1.28
        t = box("repère", (0.07 if not long else 0.1, 0.03, 0.22 if not long else 0.32), (cx + math.sin(a) * r, 11.66, cz + math.cos(a) * r), material("repère", "#1A1D1F"))
        t.rotation_euler = (0, a, 0)
    h, m = (18, 30) if soir else (22, 47)
    hour, minute = clock_hands((cx, 11.66, cz), *angles(h, m))
    if not soir:
        # Plan 3 : les aiguilles filent de 22:47 à 23:38.
        for f, (hh, mm) in ((1, (22, 47)), (60, (23, 38))):
            ah, am = angles(hh, mm)
            if hh == 23:
                am += 2 * math.pi  # une heure qui passe : un tour complet de la grande aiguille
            hour.rotation_euler = (0, ah, 0)
            hour.keyframe_insert("rotation_euler", frame=f)
            minute.rotation_euler = (0, am, 0)
            minute.keyframe_insert("rotation_euler", frame=f)

    if soir:
        # Le soleil couchant entre par une fenêtre hors champ : son croisillon se dessine sur le mur, en doré.
        bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
        sun = bpy.context.object
        sun.data.energy = 6.5
        sun.data.color = srgb("#FFC58A")[:3]
        sun.data.angle = math.radians(1.5)
        sun.rotation_euler = (math.radians(62), 0, math.radians(-58))
        frame_mat = material("cadre", "#000000")
        # Le mur percé de la fenêtre, entre le soleil et la pièce : quatre pans autour d'une ouverture, et la croix.
        wx, wy, wz = -9, 2, 9
        for size, loc in (((0.3, 30, 30), (wx, wy, wz + 18)), ((0.3, 30, 30), (wx, wy, wz - 18)), ((0.3, 15, 6), (wx, wy - 10.5, wz)), ((0.3, 15, 6), (wx, wy + 10.5, wz)), ((0.3, 6, 0.25), (wx, wy, wz)), ((0.3, 0.25, 6), (wx, wy, wz))):
            o = box("fenetre", size, loc, frame_mat)
            o.visible_camera = False
        point_light("lampe", (-2, 3, 8), 1100, "#FFC489", 1.5)
        area_light("ambiance", (0, -8, 9), (0, 4, 1), 650, 10, "#E8D8C8")
        area_light("ciel", (8, 0, 9), (0, 4, 1), 120, 8, "#AFC3E0")
    else:
        # La nuit : la lueur froide de l'écran, la lune par la fenêtre sur l'horloge et la table.
        area_light("lueur_ecran", (lx, 2.9, 1.4), (lx, 0.2, 0), 30, 3, "#BFD4F2", size_y=2)
        area_light("lune", (-9, -2, 8), (0.5, 3, 0), 420, 4, "#6F8FC4")
        area_light("lune_mur", (-7, 3, 10), (cx + 1, 11.6, cz - 1), 900, 2.5, "#7A97C8")
        area_light("contre", (6, 11, 9), (0, 3, 0), 90, 6, "#5D7699")
    camera((0.35, -7.6, 4.3), (0.3, 4.5, 2.9), lens=36, fstop=2.8, focus=9.0)
    if not soir:
        # Plan 3 : lente avancée vers l'horloge pendant que l'heure file.
        cam = sc.camera
        key(cam, "location", 1, tuple(cam.location))
        key(cam, "location", 60, (0.25, -1.5, 6.0))
        cam.data.dof.focus_distance = 9.0
    sc.frame_start, sc.frame_end = 1, 75
    return 1


# ——— Plans 5, 7 : le téléphone ———

def rounded_rect(name, w, h, radius, depth, loc, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (w, depth, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    vertical = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().y) > 0.99]
    bmesh.ops.bevel(bm, geom=vertical, offset=radius, segments=24, affect="EDGES", profile=0.5)
    bm.to_mesh(o.data)
    bm.free()
    mod = o.modifiers.new("arrondi", "BEVEL")
    mod.width = depth * 0.42
    mod.segments = 8
    mod.limit_method = "ANGLE"
    smooth(o)
    return link(o, mat)


def screen_plane(w, h, radius, loc, mat, segments=24):
    """Dalle de l'écran : un rectangle aux coins arrondis, triangulé en éventail depuis le centre (forme convexe)."""
    pts = []
    for cx, cy, start in ((w / 2 - radius, h / 2 - radius, 0), (-w / 2 + radius, h / 2 - radius, 90), (-w / 2 + radius, -h / 2 + radius, 180), (w / 2 - radius, -h / 2 + radius, 270)):
        for k in range(segments + 1):
            a = math.radians(start + 90 * k / segments)
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a), 0))
    mesh = bpy.data.meshes.new("ecran")
    verts = [(0, 0, 0)] + pts
    faces = [(0, i + 1, (i + 1) % len(pts) + 1) for i in range(len(pts))]
    mesh.from_pydata(verts, [], faces)
    # Coordonnées d'image d'après la position : l'interface remplit l'écran sans déformation.
    uv = mesh.uv_layers.new()
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = (co.x / w + 0.5, co.y / h + 0.5)
    o = bpy.data.objects.new("ecran", mesh)
    bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = (math.pi / 2, 0, 0)
    o.location = loc
    return link(o, mat)


def shot_telephone(sc, screen):
    world_color(NIGHT, 1.0)
    titanium = material("titane", "#3A3F42", metallic=1.0, roughness=0.3)
    black = material("verre_noir", "#050607", roughness=0.05, coat=1.0)
    bpy.ops.object.empty_add(location=(0, 0, 0))
    rig = bpy.context.object
    rig.name = "telephone"
    W, H, D = 7.15, 14.7, 0.8
    parts = [rounded_rect("coque", W, H, 1.1, D, (0, 0, 0), titanium)]
    parts.append(rounded_rect("face", W - 0.12, H - 0.12, 1.05, D * 0.3, (0, -D * 0.38, 0), black))
    screen_mat = image_material("interface", screen, emission_strength=2.4, gloss=True) if screen else material("éteint", "#000000")
    parts.append(screen_plane(W - 0.62, H - 0.62, 0.82, (0, -D * 0.54, 0), screen_mat))
    island = rounded_rect("ilot", 2.0, 0.6, 0.29, 0.05, (0, -D * 0.56, H / 2 - 0.85), material("ilot", "#000000", roughness=0.1))
    parts.append(island)
    for z, hgt in ((3.6, 1.6), (1.6, 1.2), (0.1, 1.2)):
        b = rounded_rect("bouton", 0.12, hgt, 0.05, 0.3, (-W / 2 - 0.04, 0, z), titanium)
        parts.append(b)
    for p in parts:
        p.parent = rig
    # La lueur orange derrière le téléphone : un disque lumineux qui s'éteint vers les bords.
    glow_wall((0, 9, 0), ORANGE_DEEP, 1.0, size=80, radius=(8, 12), edge=1.0)
    # Lumières : liseré orange derrière, grande boîte blanche douce pour le reflet sur le verre.
    area_light("liseré_g", (-8, 5, 4), (0, 0, 0), 1800, 3, ORANGE, size_y=14)
    area_light("liseré_d", (8, 5, -2), (0, 0, 0), 1200, 3, ORANGE_DEEP, size_y=14)
    area_light("reflet", (6, -14, 10), (0, 0, 0), 500, 8, "#FFF2E8", size_y=3)
    # Le téléphone monte, pivote et se tourne vers nous (plan 5), puis s'incline (plan 7).
    key(rig, "location", 1, (0, 0, -24))
    key(rig, "rotation_euler", 1, (math.radians(25), 0, math.radians(-38)))
    key(rig, "location", 40, (0, 0, 0))
    key(rig, "rotation_euler", 52, (math.radians(4), 0, math.radians(-12)))
    key(rig, "rotation_euler", 150, (0, 0, 0))
    camera((0, -42, 0.5), (0, 0, 0), lens=70)
    sc.frame_start, sc.frame_end = 1, 150
    return 150


def main():
    sc = reset()
    if SHOT == "goutte":
        still = shot_goutte(sc)
    elif SHOT in ("cuisine_nuit", "cuisine_soir"):
        still = shot_cuisine(sc, soir=SHOT == "cuisine_soir")
    elif SHOT == "telephone":
        still = shot_telephone(sc, SCREEN)
    else:
        raise SystemExit(f"plan inconnu : {SHOT}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if MODE == "image":
        sc.frame_set(FRAME or still)
        sc.render.filepath = str(OUT)
        bpy.ops.render.render(write_still=True)
    else:
        sc.render.filepath = str(OUT) + "_"
        bpy.ops.render.render(animation=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT.with_suffix(".blend")))


main()
