import arcpy
utilityNetwork = arcpy.GetParameterAsText(0)
electricDistributionDeviceFeatureClass = arcpy.GetParameterAsText(1)
DomainNetwork = "ElectricDistribution"
ServicePointCategoryName = "ServicePoint"
LoadField = "SERVICE_LOAD"
LoadAttribute = "Customer Load"
LoadAttribute2 = "Power Rating"
LoadAttribute3 = "Service Load"
needToAddCategory = False
needToAddNetworkAttribute = False
describe = arcpy.Describe(utilityNetwork)
networkAttributes = {na.name.lower() for na in describe.networkAttributes}
print("Network attributes = {0}\n".format(networkAttributes))
networkCategories = {cat.name.lower() for cat in describe.categories}
print("Categories = {0}\n".format(networkCategories))
if LoadAttribute.lower() not in networkAttributes:
	if LoadAttribute2.lower() not in networkAttributes:
		if LoadAttribute3.lower() not in networkAttributes:
			needToAddNetworkAttribute = True
if ServicePointCategoryName.lower() not in networkCategories:
	needToAddCategory = True
if needToAddCategory == True or needToAddNetworkAttribute == True:
	arcpy.AddMessage("Disabling Utility Network Topology")
	arcpy.un.DisableNetworkTopology(utilityNetwork)
	if needToAddNetworkAttribute == True:
		arcpy.AddMessage("Creating Customer Load Network Attribute")
		arcpy.un.AddNetworkAttribute(utilityNetwork, LoadAttribute, "Long", False, None, False)
		arcpy.AddMessage("Assigning Customer Load Network Attribute to Field")
		arcpy.un.SetNetworkAttribute(utilityNetwork, LoadAttribute, DomainNetwork, electricDistributionDeviceFeatureClass, LoadField)
	if needToAddCategory == True:
		arcpy.AddMessage("Adding ServicePoint Category")
		arcpy.un.AddNetworkCategory(utilityNetwork, ServicePointCategoryName)
		arcpy.AddMessage("Assigning ServicePoint Category")
		arcpy.un.SetNetworkCategory(utilityNetwork, DomainNetwork, electricDistributionDeviceFeatureClass, "Service Point", "Primary Meter", ServicePointCategoryName)
		arcpy.un.SetNetworkCategory(utilityNetwork, DomainNetwork, electricDistributionDeviceFeatureClass, "Service Point", "Single Phase Low Voltage Meter", ServicePointCategoryName)
		arcpy.un.SetNetworkCategory(utilityNetwork, DomainNetwork, electricDistributionDeviceFeatureClass, "Service Point", "Three Phase Low Voltage Meter", ServicePointCategoryName)
	arcpy.AddMessage("Enabling Utility Network Topology")
	arcpy.un.EnableNetworkTopology(utilityNetwork)
	arcpy.AddMessage("Schema modified to work with Load Report sample")
else:
	arcpy.AddMessage("Schema OK")