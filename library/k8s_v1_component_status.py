from ansible.module_utils.k8s_common import KubernetesAnsibleModule, KubernetesAnsibleException
DOCUMENTATION = """
module: k8s_v1_component_status
short_description: Kubernetes ComponentStatus
description:
- Manage the lifecycle of a component_status object. Supports check mode, and attempts
  to to be idempotent.
version_added: 2.3.0
author: OpenShift (@openshift)
options:
  annotations:
    description:
    - Annotations is an unstructured key value map stored with a resource that may
      be set by external tools to store and retrieve arbitrary metadata. They are
      not queryable and should be preserved when modifying objects.
    type: dict
  api_key:
    description:
    - Token used to connect to the API.
  cert_file:
    description:
    - Path to a certificate used to authenticate with the API.
    type: path
  conditions:
    description:
    - List of component conditions observed
    type: list
  context:
    description:
    - The name of a context found in the Kubernetes config file.
  debug:
    description:
    - Enable debug output from the OpenShift helper. Logging info is written to KubeObjHelper.log
    default: false
    type: bool
  force:
    description:
    - If set to C(True), and I(state) is C(present), an existing object will updated,
      and lists will be replaced, rather than merged.
    default: false
    type: bool
  host:
    description:
    - Provide a URL for acessing the Kubernetes API.
  key_file:
    description:
    - Path to a key file used to authenticate with the API.
    type: path
  kubeconfig:
    description:
    - Path to an existing Kubernetes config file. If not provided, and no other connection
      options are provided, the openshift client will attempt to load the default
      configuration file from I(~/.kube/config.json).
    type: path
  labels:
    description:
    - Map of string keys and values that can be used to organize and categorize (scope
      and select) objects. May match selectors of replication controllers and services.
    type: dict
  name:
    description:
    - Name must be unique within a namespace. Is required when creating resources,
      although some resources may allow a client to request the generation of an appropriate
      name automatically. Name is primarily intended for creation idempotence and
      configuration definition. Cannot be updated.
  namespace:
    description:
    - Namespace defines the space within each name must be unique. An empty namespace
      is equivalent to the "default" namespace, but "default" is the canonical representation.
      Not all objects are required to be scoped to a namespace - the value of this
      field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated.
  password:
    description:
    - Provide a password for connecting to the API. Use in conjunction with I(username).
  ssl_ca_cert:
    description:
    - Path to a CA certificate used to authenticate with the API.
    type: path
  username:
    description:
    - Provide a username for connecting to the API.
  verify_ssl:
    description:
    - Whether or not to verify the API server's SSL certificates.
    type: bool
requirements:
- kubernetes == 4.0.0
"""
EXAMPLES = """
"""
RETURN = """
api_version:
  description: Requested API version
  type: string
component_status:
  type: complex
  returned: on success
  contains:
    api_version:
      description:
      - APIVersion defines the versioned schema of this representation of an object.
        Servers should convert recognized schemas to the latest internal value, and
        may reject unrecognized values.
      type: str
    conditions:
      description:
      - List of component conditions observed
      type: list
      contains:
        error:
          description:
          - Condition error code for a component. For example, a health check error
            code.
          type: str
        message:
          description:
          - Message about the condition for a component. For example, information
            about a health check.
          type: str
        status:
          description:
          - 'Status of the condition for a component. Valid values for "Healthy":
            "True", "False", or "Unknown".'
          type: str
        type:
          description:
          - 'Type of condition for a component. Valid value: "Healthy"'
          type: str
    kind:
      description:
      - Kind is a string value representing the REST resource this object represents.
        Servers may infer this from the endpoint the client submits requests to. Cannot
        be updated. In CamelCase.
      type: str
    metadata:
      description:
      - Standard object's metadata.
      type: complex
"""
def main():
	try:
		module = KubernetesAnsibleModule("component_status", "v1")
	except KubernetesAnsibleException as exc:
		raise Exception(exc.message)
	try:
		module.execute_module()
	except KubernetesAnsibleException as exc:
		module.fail_json(msg="Module failed!", error=str(exc))
if __name__ == "__main__":
	main()