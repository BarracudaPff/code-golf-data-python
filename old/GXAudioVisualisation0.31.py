"""
# "Bake Sound to F-Curves" doesn't support choosing audio chanels
# from audio files like left or right channel, so if you want to have a
# stereo visualisatnion, then You must separate your stereo audio file
# to two mono files (e.g. in audacity), or You can use same file for
# left and right channel
"""
file_l = "/media/music.ogg"
file_r = "/media/music.ogg"
bake = 1
stereo = 3
value_x = 8
value_y = 1
space_x = 3
space_y = 3
space_array = 1.3
scale = [1, 0.8, 0.5]
s = 1
offset = 1
center_space = 1
slash = 0
drivmod = 20.0
low = 200
herz = 20000
question = 1
pow = (8 / value_x) + 1
ouu = -1
def drivering():
	obj = bpy.data.objects[nc + "_" + ny + "_" + nx]
	mdf = obj.modifiers["Array"].driver_add("count")
	drv = mdf.driver
	drv.type = "AVERAGE"
	var = drv.variables.new()
	var.name = "name"
	var.type = "TRANSFORMS"
	targ = var.targets[0]
	targ.id = bpy.data.objects[no + "_" + ny + "_" + nx]
	targ.transform_type = "SCALE_Z"
	targ.bone_target = "Driver"
	fmod = mdf.modifiers[0]
	fmod.poly_order = 1
	if question == 2:
		fmod.coefficients = (0.0, drivmod + (2 * (rx + 1)))
	else:
		fmod.coefficients = (0.0, drivmod)
def curve_modifier():
	bpy.data.objects[no + "_" + ny + "_" + nx].animation_data.action.fcurves[2].modifiers.new("STEPPED")
	bpy.data.objects[no + "_" + ny + "_" + nx].animation_data.action.fcurves[2].modifiers.active.frame_step = offset
if stereo == 2 or stereo == 3:
	float_rx = 0 + center_space
	float_ry = 0
	step = 0
	start = s
	for ry in range(0, value_y):
		for rx in range(0, value_x):
			bpy.context.scene.frame_current = start
			bpy.ops.object.add(location=(float_rx + space_x / 2, float_ry, ouu))
			bpy.ops.anim.keyframe_insert_menu(type="Scaling")
			bpy.context.area.type = "GRAPH_EDITOR"
			step2 = step
			if bake == 1:
				if question == 1:
					step = herz
					for what in range(0, value_x - rx):
						step = step / pow
					bpy.ops.graph.sound_bake(filepath=file_r, low=(step2), high=step)
				elif question == 2:
					step = (rx + 1) * (herz / value_x)
					bpy.ops.graph.sound_bake(filepath=file_r, low=(step2), high=step)
			bpy.context.area.type = "TEXT_EDITOR"
			nx = rx + 1
			nx = str(nx)
			ny = ry + 1
			ny = str(ny)
			no = "obj_R"
			bpy.context.active_object.name = no + "_" + ny + "_" + nx
			bpy.data.objects[no + "_" + ny + "_" + nx].animation_data.action.fcurves[0].hide = True
			bpy.data.objects[no + "_" + ny + "_" + nx].animation_data.action.fcurves[1].hide = True
			bpy.ops.mesh.primitive_cube_add(location=(float_rx + space_x / 2, float_ry, 0))
			bpy.ops.transform.resize(value=(scale[0], scale[1], scale[2]))
			bpy.ops.object.transform_apply(scale=True)
			nc = "cub_R"
			bpy.context.active_object.name = nc + "_" + ny + "_" + nx
			if bake == 1:
				bpy.ops.object.modifier_add(type="ARRAY")
				bpy.context.active_object.modifiers["Array"].relative_offset_displace[0] = 0
				bpy.context.active_object.modifiers["Array"].relative_offset_displace[2] = space_array
				drivering()
			if offset >= 2:
				curve_modifier()
			float_rx = float_rx + space_x
			float_ry = float_ry + slash
		float_ry = float_ry + space_y - (slash * value_x)
		float_rx = float_rx - space_x * value_x
		start = start + offset
		step = 0
if stereo == 1 or stereo == 3:
	float_rx = 0 + center_space
	float_ry = 0
	step = 0
	start = s
	for ry in range(0, value_y):
		for rx in range(0, value_x):
			bpy.context.scene.frame_current = start
			bpy.ops.object.add(location=(-float_rx - space_x / 2, float_ry, ouu))
			bpy.ops.anim.keyframe_insert_menu(type="Scaling")
			bpy.context.area.type = "GRAPH_EDITOR"
			step2 = step
			if bake == 1:
				if question == 1:
					step = herz
					for what in range(0, value_x - rx):
						step = step / pow
					bpy.ops.graph.sound_bake(filepath=file_l, low=(step2), high=step)
				elif question == 2:
					step = (rx + 1) * (herz / value_x)
					bpy.ops.graph.sound_bake(filepath=file_l, low=(step2), high=step)
			bpy.context.area.type = "TEXT_EDITOR"
			nx = rx + 1
			nx = str(nx)
			ny = ry + 1
			ny = str(ny)
			no = "obj_L"
			bpy.context.active_object.name = no + "_" + ny + "_" + nx
			bpy.data.objects[no + "_" + ny + "_" + nx].animation_data.action.fcurves[0].hide = True
			bpy.data.objects[no + "_" + ny + "_" + nx].animation_data.action.fcurves[1].hide = True
			bpy.ops.mesh.primitive_cube_add(location=(-float_rx - space_x / 2, float_ry, 0))
			bpy.ops.transform.resize(value=(scale[0], scale[1], scale[2]))
			bpy.ops.object.transform_apply(scale=True)
			nc = "cub_L"
			bpy.context.active_object.name = nc + "_" + ny + "_" + nx
			if bake == 1:
				bpy.ops.object.modifier_add(type="ARRAY")
				bpy.context.active_object.modifiers["Array"].relative_offset_displace[0] = 0
				bpy.context.active_object.modifiers["Array"].relative_offset_displace[2] = space_array
				drivering()
			if offset >= 2:
				curve_modifier()
			float_rx = float_rx + space_x
			float_ry = float_ry + slash
		float_ry = float_ry + space_y - (slash * value_x)
		float_rx = float_rx - space_x * value_x
		start = start + offset
		step = 0