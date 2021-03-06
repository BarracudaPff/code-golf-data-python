def test_create_volume_template(client):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id)
	vts = client.list_volumeTemplate(stackId=stack.id)
	assert len(vts) == 1
	vt = vts[0]
	assert vt.name == "foo"
	assert vt.driver == "nfs"
	assert vt.driverOpts == opts
	client.wait_success(stack.remove())
	wait_for(lambda: client.reload(vt).state == "removed")
def test_create_dup_volume_template(client):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id)
	with pytest.raises(ApiError) as e:
		client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id)
	assert e.value.error.status == 422
	assert e.value.error.code == "NotUnique"
	assert e.value.error.fieldName == "name"
def test_stack_volume(client, context):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	t = client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	svc1 = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	svc1 = client.wait_success(svc1)
	client.wait_success(svc1.activate())
	svc2 = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	svc2 = client.wait_success(svc2)
	client.wait_success(svc2.activate())
	c1 = _validate_compose_instance_start(client, svc1, stack, "1")
	path_to_mount = c1.dataVolumeMounts
	assert len(path_to_mount) == 1
	volume_id_1 = 0
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
		volume_id_1 = value
	volumes = client.list_volume(name_like=stack.name + "_foo_%")
	assert len(volumes) == 1
	volume = volumes[0]
	assert volume.id == volume_id_1
	assert volume.driver == "nfs"
	assert volume.driverOpts == opts
	c2 = _validate_compose_instance_start(client, svc2, stack, "1")
	path_to_mount = c2.dataVolumeMounts
	assert len(path_to_mount) == 1
	volume_id_2 = 0
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
		volume_id_2 = value
	assert volume_id_2 == volume_id_1
	client.wait_success(svc1.remove())
	client.wait_success(svc2.remove())
	wait_for(lambda: client.reload(volume).state == "inactive")
	compose_config = stack.exportconfig()
	assert compose_config is not None
	docker_yml = yaml.load(compose_config.dockerComposeConfig)
	assert t.name in docker_yml["volumes"]
	vol = docker_yml["volumes"][t.name]
	assert vol["driver"] == "nfs"
	assert vol["driver_opts"] == opts
	assert "external" not in vol
	assert "per_container" not in vol
	client.wait_success(stack.remove())
	wait_for(lambda: client.reload(volume).state == "removed")
def test_external_volume(client, context):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	t = client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id, external=True)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	service = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	service = client.wait_success(service)
	assert service.state == "inactive"
	with pytest.raises(ClientApiError) as e:
		client.wait_success(service.activate())
	assert "Failed to locate" in e.value.message
	v = client.create_volume(name="foo", driver="nfs", volumeTemplateId=t.id, stackId=stack.id)
	client.wait_success(v)
	wait_state(client, service, "active")
	compose_config = stack.exportconfig()
	assert compose_config is not None
	docker_yml = yaml.load(compose_config.dockerComposeConfig)
	assert t.name in docker_yml["volumes"]
	vol = docker_yml["volumes"][t.name]
	assert vol["external"] is True
	assert vol["driver"] == "nfs"
	assert vol["driver_opts"] == opts
	assert "per_container" not in vol
def test_du_unhealthy_reuse_volume(new_context, super_client):
	client = new_context.client
	storage_stack = client.create_stack(name=random_str())
	super_client.update(storage_stack, system=True)
	storage = client.create_storage_driver_service(name=random_str(), stackId=storage_stack.id, storageDriver={"name": "nfs", "volumeAccessMode": "singleHostRW", "blockDevicePath": "some path", "volumeCapabilities": ["superAwesome"]})
	storage = client.wait_success(storage)
	client.wait_success(storage.activate())
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	t = client.create_volumeTemplate(name=random_str(), driver="nfs", stackId=stack.id, perContainer=True)
	launch_config = {"imageUuid": new_context.image_uuid, "dataVolumes": t.name + ":/bar"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=2)
	svc = client.wait_success(svc)
	svc = client.wait_success(svc.activate())
	assert len(svc.instanceIds) == 2
	c1 = client.by_id_container(svc.instanceIds[0])
	c1 = client.wait_success(c1)
	assert c1.state == "running"
	c2 = client.by_id_container(svc.instanceIds[1])
	c2 = client.wait_success(c2)
	assert c2.state == "running"
	assert c1.id != c2.id
	super_client.update(c2, healthState="unhealthy")
	c2.restart()
	c2 = client.wait_success(c2)
	c2 = wait_for_condition(client, c2, lambda x: x.removed is not None)
	svc = wait_state(client, svc, "active")
	assert len(svc.instanceIds) == 2
	c3 = None
	for i in svc.instanceIds:
		if i != c1.id:
			c3 = client.by_id_container(i)
	assert c3.id != c2.id
	assert dict(c1.dataVolumeMounts) != dict(c2.dataVolumeMounts)
	assert dict(c2.dataVolumeMounts) == dict(c3.dataVolumeMounts)
	svc = client.update(svc, scale=1)
	wait_state(client, svc, "active")
	c3 = client.wait_success(c3)
	assert c3.removed is not None
	volume = client.by_id_volume(dict(c3.dataVolumeMounts).values()[0])
	volume = client.wait_success(volume)
	assert volume.removed is None
	client.delete(stack)
	stack = client.wait_success(stack)
	assert stack.removed is not None
	volume = client.by_id_volume(dict(c2.dataVolumeMounts).values()[0])
	volume = client.wait_success(volume)
	assert volume.removed is not None
	volume = client.by_id_volume(dict(c1.dataVolumeMounts).values()[0])
	volume = client.wait_success(volume)
	assert volume.removed is not None
def test_du_volume(new_context, super_client):
	context = new_context
	client = context.client
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	t = client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id, perContainer=True)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	secondary_lc = {"imageUuid": image_uuid, "name": "secondary", "dataVolumes": "foo:/bar"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=2, secondaryLaunchConfigs=[secondary_lc])
	svc = client.wait_success(svc)
	client.wait_success(svc.activate())
	c11 = _validate_compose_instance_start(client, svc, stack, "1")
	path_to_mount = c11.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c11 = super_client.reload(c11)
	du = c11.deploymentUnitUuid
	name = stack.name + "_foo_1_" + du
	volumes = client.list_volume(name_like=name + "_%")
	assert len(volumes) == 1
	v11 = volumes[0]
	assert v11.driver == "nfs"
	assert v11.driverOpts == opts
	c12 = _validate_compose_instance_start(client, svc, stack, "1", "secondary")
	path_to_mount = c12.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c12 = super_client.reload(c12)
	du = c12.deploymentUnitUuid
	name = stack.name + "_foo_1_" + du
	volumes = client.list_volume(name_like=name + "_%")
	assert len(volumes) == 1
	v12 = volumes[0]
	assert v12.id == v11.id
	assert v12.driver == "nfs"
	assert v12.driverOpts == opts
	c21 = _validate_compose_instance_start(client, svc, stack, "2")
	path_to_mount = c21.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c21 = super_client.reload(c21)
	du = c21.deploymentUnitUuid
	name = stack.name + "_foo_2_" + du
	volumes = client.list_volume(name_like=name + "_%")
	assert len(volumes) == 1
	v21 = volumes[0]
	assert v21.id != v11.id
	assert v21.driver == "nfs"
	assert v21.driverOpts == opts
	svc = client.update(svc, scale=1)
	client.wait_success(svc, 120)
	wait_state(client, c21, "removed")
	wait_state(client, v21, "removed")
	compose_config = stack.exportconfig()
	assert compose_config is not None
	docker_yml = yaml.load(compose_config.dockerComposeConfig)
	assert t.name in docker_yml["volumes"]
	vol = docker_yml["volumes"][t.name]
	assert vol["per_container"] is True
	assert vol["driver"] == "nfs"
	assert vol["driver_opts"] == opts
	assert "external" not in vol
def _validate_compose_instance_start(client, service, env, number, launch_config_name=None):
	cn = launch_config_name + "-" if launch_config_name is not None else ""
	name = env.name + "-" + service.name + "-" + cn + number
	def wait_for_map_count(service):
		instances = client.list_container(name=name, state="running")
		return len(instances) == 1
	wait_for(lambda: wait_for_condition(client, service, wait_for_map_count))
	instances = client.list_container(name=name, state="running")
	return instances[0]
def test_upgrade_du_volume(client, context, super_client):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id, perContainer=True)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	secondary_lc = {"imageUuid": image_uuid, "name": "secondary", "dataVolumes": "foo:/bar"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1, secondaryLaunchConfigs=[secondary_lc])
	svc = client.wait_success(svc)
	client.wait_success(svc.activate())
	c11 = _validate_compose_instance_start(client, svc, stack, "1")
	path_to_mount = c11.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c11 = super_client.reload(c11)
	du = c11.deploymentUnitUuid
	name = stack.name + "_foo_1_" + du
	volumes = client.list_volume(name_like=name + "_%")
	assert len(volumes) == 1
	v11 = volumes[0]
	assert v11.driver == "nfs"
	assert v11.driverOpts == opts
	strategy = {"launchConfig": launch_config, "intervalMillis": 100}
	svc.upgrade_action(inServiceStrategy=strategy)
	svc = client.wait_success(svc)
	c12 = _validate_compose_instance_start(client, svc, stack, "1")
	assert c11.id != c12.id
	path_to_mount = c12.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c12 = super_client.reload(c12)
	du = c12.deploymentUnitUuid
	name = stack.name + "_foo_1_" + du
	volumes = client.list_volume(name_like=name + "_%")
	assert len(volumes) == 1
	v12 = volumes[0]
	assert v11.id == v12.id
	client.wait_success(svc.finishupgrade())
	volumes = client.list_volume(name_like=name + "_%")
	assert len(volumes) == 1
	v12 = volumes[0]
	assert v11.id == v12.id
def test_classic_volume(client, context):
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	secondary_lc = {"imageUuid": image_uuid, "name": "secondary", "dataVolumes": "foo:/bar"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1, secondaryLaunchConfigs=[secondary_lc])
	svc = client.wait_success(svc)
	client.wait_success(svc.activate())
	c11 = _validate_compose_instance_start(client, svc, stack, "1")
	assert len(c11.dataVolumeMounts) == 0
	assert "foo:/bar" in c11.dataVolumes
def test_prev_version_service(client, context, super_client):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id)
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	secondary_lc = {"imageUuid": image_uuid, "name": "secondary", "dataVolumes": "foo:/bar"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1, secondaryLaunchConfigs=[secondary_lc])
	svc = wait_state(client, svc, "inactive")
	svc = super_client.update(svc, serviceIndexStrategy="noop")
	svc = super_client.wait_success(svc)
	assert svc.serviceIndexStrategy == "noop"
	client.wait_success(svc.activate())
	c11 = _validate_compose_instance_start(client, svc, stack, "1")
	assert len(c11.dataVolumeMounts) == 0
	assert "foo:/bar" in c11.dataVolumes
	assert len(super_client.list_deploymentUnit(uuid=c11.deploymentUnitUuid)) == 0
def test_no_scope(client):
	opts = {"foo": "true", "bar": "true"}
	with pytest.raises(ApiError) as e:
		client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts)
	assert e.value.error.status == 422
def test_v1_v2_mix_export(client, context):
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	t = client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id, external=True)
	image_uuid = context.image_uuid
	data_volumes = ["foo:/bar", "bar:/foo", "baz", "/bar:/foo"]
	launch_config = {"imageUuid": image_uuid, "dataVolumes": data_volumes, "volumeDriver": "nfs"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	svc = client.wait_success(svc)
	assert svc.state == "inactive"
	compose_config = stack.exportconfig()
	assert compose_config is not None
	docker_yml = yaml.load(compose_config.dockerComposeConfig)
	volumes = docker_yml["volumes"]
	assert len(volumes) == 2
	assert t.name in volumes
	vol = volumes[t.name]
	assert vol["external"] is True
	assert vol["driver"] == "nfs"
	assert vol["driver_opts"] == opts
	assert "per_container" not in vol
	assert "bar" in volumes
	vol = volumes["bar"]
	assert vol["external"] is True
	assert vol["driver"] == "nfs"
	assert "per_container" not in vol
	assert "volume_driver" not in docker_yml["services"][svc.name]
def test_null_driver_export(client, context):
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	image_uuid = context.image_uuid
	data_volumes = ["foo:/bar"]
	launch_config = {"imageUuid": image_uuid, "dataVolumes": data_volumes}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	svc = client.wait_success(svc)
	assert svc.state == "inactive"
	compose_config = stack.exportconfig()
	assert compose_config is not None
	docker_yml = yaml.load(compose_config.dockerComposeConfig)
	assert "volumes" not in docker_yml
def test_volume_template_without_driver_fields(client, context):
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	t = client.create_volumeTemplate(name="foo", stackId=stack.id, external=False)
	image_uuid = context.image_uuid
	data_volumes = ["foo:/bar"]
	launch_config = {"imageUuid": image_uuid, "dataVolumes": data_volumes}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	svc = client.wait_success(svc)
	assert svc.state == "inactive"
	compose_config = stack.exportconfig()
	assert compose_config is not None
	docker_yml = yaml.load(compose_config.dockerComposeConfig)
	volumes = docker_yml["volumes"]
	assert len(volumes) == 1
	assert t.name in volumes
	vol = volumes[t.name]
	assert len(vol) == 0
def test_du_volume_recreate_disabled_host(new_context, super_client):
	context = new_context
	client = context.client
	register_simulated_host(new_context)
	opts = {"foo": "true", "bar": "true"}
	stack = client.create_stack(name=random_str())
	stack = client.wait_success(stack)
	client.create_volumeTemplate(name="foo", driver="nfs", driverOpts=opts, stackId=stack.id, perContainer=True)
	image_uuid = context.image_uuid
	launch_config = {"imageUuid": image_uuid, "dataVolumes": "foo:/bar"}
	svc = client.create_service(name=random_str(), stackId=stack.id, launchConfig=launch_config, scale=1)
	svc = client.wait_success(svc)
	client.wait_success(svc.activate())
	c11 = _validate_compose_instance_start(client, svc, stack, "1")
	path_to_mount = c11.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c11 = super_client.reload(c11)
	du = c11.deploymentUnitUuid
	name = stack.name + "_foo_1_" + du
	volumes = client.list_volume(name_like=name + "_%", stack_id=stack.id)
	assert len(volumes) == 1
	v11 = volumes[0]
	instance_host = c11.instanceHostMaps()[0].host()
	assert instance_host is not None
	client.wait_success(instance_host.deactivate())
	client.wait_success(c11.stop(remove=True))
	c12 = _validate_compose_instance_start(client, svc, stack, "1")
	path_to_mount = c12.dataVolumeMounts
	assert len(path_to_mount) == 1
	for key, value in path_to_mount.iteritems():
		assert key == "/bar"
		assert value is not None
	c12 = super_client.reload(c12)
	assert c12.hostId != c11.hostId
	du = c12.deploymentUnitUuid
	name = stack.name + "_foo_1_" + du
	volumes = client.list_volume(name_like=name + "_%", stack_id=stack.id)
	assert len(volumes) == 1
	assert volumes[0].id != v11.id