from ctypes import cdll, c_float, c_void_p, c_char_p
import numpy
OHMD_VENDOR = 0
OHMD_PRODUCT = 1
OHMD_PATH = 2
OHMD_ROTATION_QUAT = 1
lib = cdll.LoadLibrary("libopenhmd.so")
ohmd_list_open_device = lib.ohmd_list_open_device
ohmd_list_open_device.restype = c_void_p
ohmd_device_getf = lib.ohmd_device_getf
ohmd_ctx_get_error = lib.ohmd_ctx_get_error
ohmd_ctx_get_error.restype = c_char_p
ohmd_list_gets = lib.ohmd_list_gets
ohmd_list_gets.restype = c_char_p
class OpenHMD(object):
	def __init__(self, device_id=0):
		self.ctx = lib.ohmd_ctx_create()
		lib.ohmd_ctx_probe(self.ctx)
		self.device = ohmd_list_open_device(self.ctx, device_id)
		if self.device == 0:
			print("Failed to open HMD device: %s" % ohmd_ctx_get_error(self.ctx))
		else:
			device_info = (self.get_device_vendor(), self.get_device_product(), self.get_device_path())
			print("HMD Device found, vendor={}, product={}, path={}".format(*device_info))
		self.rotation = [0.0, 0.0, 0.0, 0.0]
	def poll(self):
		lib.ohmd_ctx_update(self.ctx)
		f = (c_float * 4)(0, 0, 0, 0)
		ohmd_device_getf(self.device, OHMD_ROTATION_QUAT, f)
		self.rotation = numpy.array(f)
	def close(self):
		lib.ohmd_ctx_destroy(self.ctx)
	def get_device_vendor(self):
		return ohmd_list_gets(self.ctx, self.device, OHMD_VENDOR)
	def get_device_product(self):
		return ohmd_list_gets(self.ctx, self.device, OHMD_PRODUCT)
	def get_device_path(self):
		return ohmd_list_gets(self.ctx, self.device, OHMD_PATH)