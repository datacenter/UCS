class ModelDisplay:

	def __init__(self,system):
		self.display_header(system)
		for chas in system.Chassis:
			self.display_chassis(chas)
			for blade in chas.Blades:
				self.display_blade(blade)
				for proc in blade.Processors:
					self.display_proc(proc)

				self.display_memory(blade.Memory)

				for ctrl in blade.StorageCtrls:
					self.display_storage_controller(ctrl)
					for disk in ctrl.Disks:
						self.display_disk(disk)
				for adp in blade.Adaptors:
					self.display_adaptor(adp)
				self.display_end_of_blade()
			self.display_end_of_chassis()
		self.display_end_of_system()

	def display_header(self,system):
		pass

	def display_chassis(self,chas):
		pass

	def display_blade(self,blade):
		pass

	def display_proc(self,proc):
		pass

	def display_memory(self,memory):
		pass

	def display_storage_controller(self,ctrl):
		pass

	def display_disk(self,disk):
		pass

	def display_adaptor(self,adp):
		pass

	def display_end_of_blade(self):
		pass

	def display_end_of_chassis(self):
		pass

	def display_end_of_system(self):
		pass

	def display(self):
		pass
