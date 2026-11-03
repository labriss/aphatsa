import bpy, time, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = sys.argv[-1]
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=64, ring_count=32)
m = bpy.data.materials.new("glass"); m.use_nodes = True
b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Transmission Weight"].default_value = 1; b.inputs["Roughness"].default_value = 0.02
bpy.context.object.data.materials.append(m)
bpy.ops.object.light_add(type="AREA", location=(3, -2, 3)); bpy.context.object.data.energy = 800
bpy.ops.object.camera_add(location=(0, -6, 0), rotation=(1.5708, 0, 0)); sc.camera = bpy.context.object
w = bpy.data.worlds.new("w"); sc.world = w
if sc.render.engine == "CYCLES":
    sc.cycles.samples = 32; sc.cycles.use_denoising = True
else:
    sc.eevee.taa_render_samples = 16
sc.render.filepath = "//../renders/speed_" + sc.render.engine + ".png"
sc.frame_start, sc.frame_end = 1, 3
sc.render.filepath = "//../renders/speed_" + sc.render.engine + "_"
t = time.time(); bpy.ops.render.render(animation=True); print("RENDERTIME", sc.render.engine, round(time.time() - t, 1))
