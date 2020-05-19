sys.path.append("../pytorch_Realtime_Multi-Person_Pose_Estimation")
def remove_noise(img):
	th = filters.threshold_otsu(img)
	bin_img = img > th
	regions, num = ndimage.label(bin_img)
	areas = []
	for i in range(num):
		areas.append(np.sum(regions == i + 1))
	img[regions != np.argmax(areas) + 1] = 0
	return img
def create_label(shape, joint_list, person_to_joint_assoc):
	label = np.zeros(shape, dtype=np.uint8)
	for limb_type in range(17):
		for person_joint_info in person_to_joint_assoc:
			joint_indices = person_joint_info[joint_to_limb_heatmap_relationship[limb_type]].astype(int)
			if -1 in joint_indices:
				continue
			joint_coords = joint_list[joint_indices, :2]
			coords_center = tuple(np.round(np.mean(joint_coords, 0)).astype(int))
			limb_dir = joint_coords[0, :] - joint_coords[1, :]
			limb_length = np.linalg.norm(limb_dir)
			angle = math.degrees(math.atan2(limb_dir[1], limb_dir[0]))
			polygon = cv2.ellipse2Poly(coords_center, (int(limb_length / 2), 4), int(angle), 0, 360, 1)
			cv2.fillConvexPoly(label, polygon, limb_type + 1)
	return label
def get_pose(param, heatmaps, pafs):
	shape = heatmaps.shape[:2]
	joint_list_per_joint_type = NMS(param, heatmaps)
	joint_list = np.array([tuple(peak) + (joint_type,) for joint_type, joint_peaks in enumerate(joint_list_per_joint_type) for peak in joint_peaks])
	paf_upsamp = cv2.resize(pafs, shape, interpolation=cv2.INTER_CUBIC)
	connected_limbs = find_connected_joints(param, paf_upsamp, joint_list_per_joint_type)
	person_to_joint_assoc = group_limbs_of_same_person(connected_limbs, joint_list)
	label = create_label(shape, joint_list, person_to_joint_assoc)
	return label