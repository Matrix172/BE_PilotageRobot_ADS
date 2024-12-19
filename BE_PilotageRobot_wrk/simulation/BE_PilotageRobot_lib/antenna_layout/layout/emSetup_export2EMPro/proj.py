# Automatically generated file proj.py"

# Generated with $Id: extrusion_to_empro.cpp 11193 2023-01-22 13:42:22Z mdewilde $ 

import empro, empro.toolkit

def getVersion():
	return 11

def getSessionVersion(session):
	try:
		return session.getVersion()
	except AttributeError:
		return 0

def get_ads_import_version():
	try:
		ads_import_version = empro.toolkit.ads_import.getVersion()
	except AttributeError:
		ads_import_version = 0
	return ads_import_version

def ads_simulation_settings():
	set_frequency_plan_and_common_options()
	set_FEM_options()

def set_frequency_plan_and_common_options():
	try:
		sim=empro.activeProject.simulationSettings
	except AttributeError:
		sim=empro.activeProject.createSimulationData()
	sim.saveFieldsFor="NoFrequencies"
	# Frequency plan:
	frequency_plan_list=sim.femFrequencyPlanList()
	frequency_plan_list.clear()
	try:
		frequency_plan_list._frequencyPlanType="NoInterpolating_NoFields"
	except Exception:
		pass
	frequency_plan=empro.simulation.FrequencyPlan()
	frequency_plan.type="Adaptive"
	frequency_plan.startFrequency=10000000
	frequency_plan.stopFrequency=16000000
	frequency_plan.samplePointsLimit=100
	frequency_plan_list.append(frequency_plan)
	if 'minFreq' in empro.activeProject.parameters:
		empro.activeProject.parameters.setFormula('minFreq','0.01 GHz')
	if 'maxFreq' in empro.activeProject.parameters:
		empro.activeProject.parameters.setFormula('maxFreq','0.016 GHz')

def set_FEM_options():
	# Simulation options:
	try:
		sim=empro.activeProject.simulationSettings
	except AttributeError:
		sim=empro.activeProject.createSimulationData()
	sim.simulator = "com.keysight.xxpro.simulator.fem"
	try:
		sim.ambientConditions.backgroundTemperature = "25 degC"
	except AttributeError:
		pass
	try:
		sim.femEigenMode = False
	except AttributeError:
		pass
	try:
		sim.portOnlyMode = False
	except AttributeError:
		pass
	try:
		sim.transfinitePorts  = False
	except AttributeError:
		pass
	sim.femMeshSettings.minimumNumberOfPasses      = 2
	sim.femMeshSettings.maximumNumberOfPasses      = 15
	sim.femMeshSettings.deltaError                 = 0.02
	sim.femMeshSettings.refineAtSpecificFrequency  = False
	sim.femMeshSettings.refinementFrequency        = "0 GHz"
	sim.femMeshSettings.requiredConsecutivePasses  = 1
	sim.femMeshSettings.meshRefinementPercentage   = 25
	sim.femMeshSettings.orderOfBasisFunctions      = 2
	try:
		sim.femMeshSettings.useMinMeshSize               = False
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.minMeshSize                  = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.autoTargetMeshSize           = True
		sim.femMeshSettings.useTargetMeshSize            = True
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.targetMeshSize               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.edgeMeshLength               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.vertexMeshLength               = "0 m" 
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.mergeObjectsOfSameMaterial = True
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.alwaysSolveOnFinestMesh = False
	except AttributeError:
		pass
	try:
		sim.femMeshSettings.autoConductorMeshing = False
	except AttributeError:
		pass
	try:
		empro.activeProject.gridGenerator.femPadding.useDefault = False
	except AttributeError:
		pass
	try:
		sim.dataSetFileName                            = ''
	except AttributeError:
		pass
	try:
		sim.femMatrixSolver.solverType                    = "MatrixSolverAuto"
	except ValueError: # Old versions of EMPro (< 2017) do not have the auto-select solver option
		sim.femMatrixSolver.solverType                    = "MatrixSolverDirect"
	sim.femMatrixSolver.maximumNumberOfIterations     = 500
	sim.femMatrixSolver.tolerance                     = 1e-05
	try:
		sim.femMeshSettings.refinementStrategy="maxFrequency"
	except AttributeError:
		pass

def get_session(usedFlow="ADS"):
	ads_import_version = get_ads_import_version()
	if ads_import_version >= 3:
		session=empro.toolkit.ads_import.Import_session(units="um", wall_boundary="Radiation",usedFlow=usedFlow,adsProjVersion=getVersion())
		return session
	try:
		session=empro.toolkit.ads_import.Import_session(units="um", wall_boundary="Radiation",usedFlow=usedFlow)
	except TypeError: # usedFlow may not be available in old FEM bits
		session=empro.toolkit.ads_import.Import_session(units="um", wall_boundary="Radiation")
	return session

def _dummyUpdateProgress(value):
	pass

def _createIfToggleExtensionToBoundingBoxExpression(exprTrue,exprFalse):
	if get_ads_import_version() >= 11:
		return "if(toggleExtensionToBoundingBox, %s, %s)" % (exprTrue, exprFalse)
	else:
		return exprFalse

def ads_import(usedFlow="ADS",topAssembly=None,session=None,demoMode=False,includeInvalidPorts=True,suppressNotification=False,updateProgressFunction=_dummyUpdateProgress,materialForEachLayer=False):
	ads_simulation_settings()
	importer = projImporter(usedFlow,session,updateProgressFunction)
	rv = importer.ads_import(usedFlow,topAssembly,demoMode,includeInvalidPorts,suppressNotification,materialForEachLayer)
	try:
		empro.activeProject.gridGenerator.femPadding.useDefault = False
	except AttributeError:
		pass
	return rv

class projImporter():
	def __init__(self,usedFlow="ADS",session=None,updateProgressFunction=_dummyUpdateProgress):
		self.usedFlow = usedFlow
		if session==None:
			self.session=get_session(usedFlow)
		else:
			self.session = session
		if getSessionVersion(self.session) >= 8:
			self.session.setProjImporter(self)
		self.roughnesses={}
		self.materials={}
		self.substratePartNameMap={}
		self.substrateLayers=[] # ordered list with substrate layers
		self.waveforms={}
		self.circuitComponentDefinitions={}
		self.initNetlists()
		self.updateProgressFunction = updateProgressFunction
		if updateProgressFunction == _dummyUpdateProgress:
			if getSessionVersion(self.session) >= 10:
				self.updateProgressFunction = self.session.getUpdateProgressFunction()
		self.geoProgress = 0

	def _updateProgress(self,progress):
		self.updateProgressFunction(progress)

	def _setModelTypeForMetals(self,material,value):
		if getSessionVersion(self.session) >= 2:
			self.session.setModelTypeForMetals(material,value)
			return
		try:
			material.details.electricProperties.parameters.useSurfaceConductivityCorrection = value
		except:
			pass
	def _checked_roughness(self,roughnessTypeString,*args):
		try:
			roughnessConstructor = getattr(empro.material,roughnessTypeString)
			return roughnessConstructor(*args)
		except AttributeError:
			print("Warning: unsupported surface roughness type %s. Roughness will be ignored." % roughnessTypeString)
			return None
	def _create_parameter(self,iParName,iFormula,iNotes,iUserEditable,fixGridAxis=""):
		if getSessionVersion(self.session) >= 2:
			self.session.create_parameter(iParName,iFormula,iNotes,iUserEditable,fixGridAxis)
			return
		try:
			self.session.create_parameter(iParName,iFormula,iNotes,iUserEditable)
		except AttributeError:
			empro.activeProject.parameters.append(iParName,iFormula,iNotes,iUserEditable)
		if fixGridAxis in ['X','Y','Z']:
			gG = empro.activeProject.gridGenerator
			newFP = empro.libpyempro.mesh.FixedPoint()
			if fixGridAxis == 'X':
				location = (iParName,0,0)
			elif fixGridAxis == 'Y':
				location = (0,iParName,0)
			elif fixGridAxis == 'Z':
				location = (0,0,iParName)
			newFP.location = location
			newFP.axes=fixGridAxis
			gG.addManualFixedPoint(newFP)
	def _circularGridRegion(self,x,y,radius):
		radius = empro.core.Expression(radius)
		newGRP = empro.libpyempro.mesh.ManualGridRegionParameters()
		newGRP.cellSizes.target = (radius,radius,0)
		newGRP.gridRegionDirections="X|Y"
		newGRP.regionBounds.lower = (x-radius,y-radius,0)
		newGRP.regionBounds.upper = (x+radius,y+radius,0)
		return newGRP
	def _partGridParameters(self,targetCellSize):
		targetCellSize = empro.core.Expression(targetCellSize)
		newGP = empro.libpyempro.mesh.PartGridParameters()
		newGP.cellSizes.target = (targetCellSize,targetCellSize,0)
		newGP.gridRegionDirections="X|Y"
		newGP.useGridRegions = True
		return newGP
	def _create_sketch(self,pointString,sketch=None,closed=True):
		if getSessionVersion(self.session) >= 4:
			return self.session.create_sketch(pointString,sketch,closed)
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		def stringToPoint(s):
			sList = s.split('#')
			return V(sList[0],sList[1],0)
		if sketch == None:
			sketch=empro.geometry.Sketch()
		pointList = [ stringToPoint(x) for x in pointString.split(';') ]
		if closed:
			edges = [ L(pointList[i-1],pointList[i]) for i in range(len(pointList)) ]
		else:
			edges = [ L(pointList[2*i],pointList[2*i+1]) for i in range(len(pointList)/2) ]
		sketch.addEdges(edges)
		return sketch
	def _create_extrude(self, pointStrings, height, up):
		if getSessionVersion(self.session) >= 14:
			return self.session.create_extrude(pointStrings, height, up)
		else:
			sketch = None
			for pointString in pointStrings:
				sketch = self._create_sketch(pointString, sketch)
			part = empro.geometry.Model()
			part.recipe.append(empro.geometry.Extrude(sketch, height, empro.geometry.Vector3d(0, 0, (-1, 1)[up])))
			return part
	def _create_cover(self, pointStrings):
		if getSessionVersion(self.session) >= 14:
			return self.session.create_cover(pointStrings)
		else:
			sketch = None
			for pointString in pointStrings:
				sketch = self._create_sketch(pointString, sketch)
			part = empro.geometry.Model()
			part.recipe.append(empro.geometry.Cover(sketch))
			return part
	def _create_bondwire(self,radius, segments, points, name=None,bwAssembly=None,topAssembly=None,material=None,partModifier=(lambda x : x),profile=None,above=True):
		if getSessionVersion(self.session) >= 13:
			part = self.session.create_bondwire(radius, segments, points, name, bwAssembly,topAssembly,material,partModifier,profile,above)
		else:
			if profile is not None:
				part = empro.geometry.Model()
				try:
					part.recipe.append(empro.geometry.Bondwire(points[0],points[-1],profile))
				except TypeError:
					# Only for compatibility with EMPro 2011.02 or older
					self.session.warnings.append('For importing bondwires with profile definitions it is advised to use EMPro 2012.09 or later.')
					bw=empro.geometry.Bondwire(points[0],points[-1],empro.geometry.BondwireDefinition(name,radius,segments))
					bw.definition=profile
					part.recipe.append(bw)
				if not above:
					import math
					part.coordinateSystem.rotate(math.pi,0,0)
				part = partModifier(part)
				bwAssembly.append(part)
				part.name = name
				empro.toolkit.applyMaterial(part,material)
			else:
				try:
					part = self.session.create_bondwire(radius, segments, points, name, bwAssembly,topAssembly,material,partModifier)
				except TypeError:
					part = self.session.create_bondwire(radius, segments, points)
					part = partModifier(part)
					bwAssembly.append(part)
					part.name = name
					empro.toolkit.applyMaterial(part,material)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=2000
		return part
	def _create_internal_port(self, name, definitionString, head, tail, extent=None):
		if getSessionVersion(self.session) < 15 and (isinstance(head, list) or isinstance(tail, list)):
			raise RuntimeError("Ports having multiple positive or negative pins are not yet supported")
		if getSessionVersion(self.session) >= 9:
			return self.session.create_internal_port(name, definitionString, head, tail, extent)
		port=empro.components.CircuitComponent()
		port.name=name
		port.definition=self.circuitComponentDefinitions[definitionString]
		port.head=head
		port.tail=tail
		if extent != None:
			port.extent=extent
			port.useExtent=True
		return port
	def _set_extra_port_info(self, port, termType, number, name, feedType, mode = -1):
		try:
			if get_ads_import_version() >= 17:
				self.session.set_extra_port_info(port=port, termType=termType, number=number, name=name, mode=mode, feedType=feedType)
			else:
				self.session.set_extra_port_info(port=port, termType=termType, number=number, name=name, mode=mode)
		except AttributeError:
			pass
		global g_portNbToName
		g_portNbToName[number] = (name, mode)
	def _setAssemblyMeshSettings(self,a,vertexMeshLength=0,edgeMeshLength=0,surfaceMeshLength=0):
		if vertexMeshLength==0 and edgeMeshLength==0 and surfaceMeshLength==0:
			return
		if getSessionVersion(self.session) >= 12:
			self.session.setAssemblyMeshSettings(a,vertexMeshLength,edgeMeshLength,surfaceMeshLength)
			return
		parts = [x for x in a.flatList(False)]
		for x in parts:
			x.meshParameters.vertexMeshLength=vertexMeshLength
			x.meshParameters.edgeMeshLength=edgeMeshLength
			x.meshParameters.surfaceMeshLength=surfaceMeshLength
	def _getEMProMaterialName(self,ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1):
		EMProMaterialName=ADSmaterialName
		if ADSmaterialName in [x for (x,y) in ADSmaterialMap.keys()]:
			EMProMaterialName+="_"+str(extraMaterialProperties)
			if not ADSmaterialName in ADSmaterialsNo1to1:
				ADSmaterialsNo1to1.append(ADSmaterialName)
				self.session.warnings.append('The ADS material '+ADSmaterialName+' is used on masks with different precedence, sheet thickness or modeltype for metals and has therefore been mapped to multiple EMPro materials.')
		return EMProMaterialName
	def create_bondwire_definitions(self):
		self.bondwire_definitions={}
		if not hasattr(empro.activeProject,"bondwireDefinitions"):
			return
	def create_materials(self,materialForEachLayer=False):
		ADSmaterialMap={}
		EMProNameMaterialMap={}
		layerEMProMaterialNameMap={}
		ADSmaterialsNo1to1=[]
		ADSmaterialName=["AIR","simulation_box"][materialForEachLayer]
		extraMaterialProperties=(0,None,None,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,255,255,0), permittivity=1, permeability=1)
			try:
				material.priority=0
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["simulation_box"]=material
		layerEMProMaterialNameMap["simulation_box"]=EMProMaterialName
		ADSmaterialName=["PERFECT_CONDUCTOR","cond"][materialForEachLayer]
		extraMaterialProperties=(162,3.5e-05,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(238,106,80,255), thickness="3.5e-05 m", resistance=0)
			try:
				material.details.electricProperties.parameters.thickness = "3.5e-05 m"
			except AttributeError:
				pass
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=162
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["cond"]=material
		layerEMProMaterialNameMap["cond"]=EMProMaterialName
		ADSmaterialName=["PERFECT_CONDUCTOR","cond2"][materialForEachLayer]
		extraMaterialProperties=(160,3.5e-05,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(255,255,0,255), thickness="3.5e-05 m", resistance=0)
			try:
				material.details.electricProperties.parameters.thickness = "3.5e-05 m"
			except AttributeError:
				pass
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=160
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["cond2"]=material
		layerEMProMaterialNameMap["cond2"]=EMProMaterialName
		ADSmaterialName=["PERFECT_CONDUCTOR","hole"][materialForEachLayer]
		extraMaterialProperties=(64,1e-09,False,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(0,191,255,255), thickness="1e-09 m", resistance=0)
			try:
				material.details.electricProperties.parameters.thickness = "1e-09 m"
			except AttributeError:
				pass
			self._setModelTypeForMetals(material,False)
			try:
				material.priority=64
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["hole"]=material
		layerEMProMaterialNameMap["hole"]=EMProMaterialName
		ADSmaterialName=["Alumina","__SubstrateLayer1___BOTTOM"][materialForEachLayer]
		extraMaterialProperties=(50,None,None,False) # (priority,thickness,modelTypeForMetals,convertedToResistance)
		material=ADSmaterialMap.get((ADSmaterialName,extraMaterialProperties),None)
		if material == None:
			EMProMaterialName = self._getEMProMaterialName(ADSmaterialName,ADSmaterialMap,extraMaterialProperties,ADSmaterialsNo1to1)
			material=self.session.create_material(name=EMProMaterialName, color=(202,225,255,128), permittivity=9.6, permeability=1)
			try:
				material.priority=50
				material.autoPriority=False
			except AttributeError:
				pass
			ADSmaterialMap[(ADSmaterialName,extraMaterialProperties)]=material
			EMProNameMaterialMap[EMProMaterialName]=material
		else:
			EMProMaterialName=material.name
		self.materials["__SubstrateLayer1___BOTTOM"]=material
		layerEMProMaterialNameMap["__SubstrateLayer1___BOTTOM"]=EMProMaterialName
		self.substratePartNameMap["__SubstrateLayer1___BOTTOM"]=ADSmaterialName
		self.substrateLayers.append("__SubstrateLayer1___BOTTOM")
		self.numberSubstratePartNameMap()
		if getSessionVersion(self.session) >= 6:
			self.session.appendUniqueMaterials(EMProNameMaterialMap)
		else:
			for name,material in EMProNameMaterialMap.items():
				empro.activeProject.materials().append(material)
				EMProNameMaterialMap[name] = empro.activeProject.materials().at(empro.activeProject.materials().size()-1)
		self.materials={}
		for layerName in layerEMProMaterialNameMap.keys():
			self.materials[layerName]=EMProNameMaterialMap.get(layerEMProMaterialNameMap.get(layerName,None),None)
		# End of create_materials
	def numberSubstratePartNameMap(self):
		materialCount={}
		for m in self.substratePartNameMap.keys():
			materialCount[self.substratePartNameMap[m]] = materialCount.get(self.substratePartNameMap[m],0) + 1
		multipleUsedMaterials = [m for m in materialCount.keys() if materialCount[m] > 1]
		for layer in self.substrateLayers:
			mat=self.substratePartNameMap.get(layer,None)
			if mat in multipleUsedMaterials:
				self.substratePartNameMap[layer]+=' '+str(materialCount[mat])
				materialCount[mat]-=1
	def setBoundaryConditions(self):
		pass
		# End of setBoundaryConditions
	def setPortWarnings(self,includeInvalidPorts):
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"P2\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		if includeInvalidPorts:
			self.session.warnings.append("No suitable implicit reference has been found for port \"P3\". The minus pin has therefore been colocated with the plus pin and will need to be corrected by hand.")
		pass
		# End of setPortWarnings
	def initNetlists(self):
		netlistNames = ['net_0_P1']
		if getSessionVersion(self.session) >= 5:
			self.session.initNetlists(netlistNames)
			return
		self.groupList = []
		try:
			for i in netlistNames:
				g = empro.core.ShortcutGroup(i)
				self.groupList.append(g)
		except:
			pass
	def addShortcut(self,netId,part):
		if getSessionVersion(self.session) >= 5:
			self.session.addShortcut(netId,part)
			return
		try:
			s = empro.core.Shortcut(part)
			self.groupList[netId].append(s)
		except:
			pass
	def addShortcutsToProject(self):
		if getSessionVersion(self.session) >= 5:
			self.session.addShortcutsToProject()
			return
		try:
			for g in self.groupList:
				empro.activeProject.shortcuts().append(g)
		except:
			pass

	def ads_import(self,usedFlow="ADS",topAssembly=None,demoMode=False,includeInvalidPorts=True,suppressNotification=False,materialForEachLayer=False):
		if getSessionVersion(self.session) >= 1:
			self.session.prepare_import()
		self.create_materials(materialForEachLayer=materialForEachLayer)
		self.create_parameters()
		if topAssembly != None:
			topAssemblyShouldBeAdded = False
		else:
			topAssembly = empro.geometry.Assembly()
			topAssembly.name = usedFlow+'_import'
			if demoMode:
				empro.activeProject.geometry.append(topAssembly)
				topAssemblyShouldBeAdded = False
			else:
				topAssemblyShouldBeAdded = True
		param_list = empro.activeProject.parameters
		param_list.setFormula( "lateralExtension", "0 um")
		param_list.setFormula( "verticalExtension", "0 um")
		self.create_bondwire_definitions()
		self.setBoundaryConditions()
		symbPinData = self.create_geometry(topAssembly)
		self.create_ports( topAssembly, includeInvalidPorts, symbPinData )
		if get_ads_import_version() >= 11 :
			Expr=empro.core.Expression
			if topAssembly != None:
				bbox_geom = topAssembly.boundingBox()
			else:
				bbox_geom = empro.activeProject.geometry.boundingBox()
			param_list = empro.activeProject.parameters
			param_list.setFormula( "xLowerBoundingBox", str(bbox_geom.lower.x.formula()) +" m - xLowerExtension" )
			param_list.setFormula( "xUpperBoundingBox", str(bbox_geom.upper.x.formula()) +" m + xUpperExtension" )
			param_list.setFormula( "yLowerBoundingBox", str(bbox_geom.lower.y.formula()) +" m - yLowerExtension" )
			param_list.setFormula( "yUpperBoundingBox", str(bbox_geom.upper.y.formula()) +" m + yUpperExtension" )
			param_list.setFormula( "zLowerBoundingBox", str(bbox_geom.lower.z.formula()) +" m - zLowerExtension" )
			param_list.setFormula( "zUpperBoundingBox", str(bbox_geom.upper.z.formula()) +" m + zUpperExtension" )
			param_list.setFormula( "toggleExtensionToBoundingBox", "1" )
		param_list.setFormula( "lateralExtension", "3125 um")
		param_list.setFormula("verticalExtension", "5000 um")
		self.addShortcutsToProject()
		if topAssemblyShouldBeAdded:
			empro.activeProject.geometry.append(topAssembly)
			self.session.adjust_view()
		self.session.renumber_waveguides()
		if getSessionVersion(self.session) >= 10:
			self.session.post_import()
		if not suppressNotification:
			self.session.notify_success()
		return self.session.warnings
		#End of ads_import method

	def create_geometry(self,topAssembly):
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		unit2meterFactor = 1e-06
		symbPinData = None
		assembly=empro.geometry.Assembly()
		assembly.name="bondwires"
		assembly=empro.geometry.Assembly()
		part=empro.geometry.Model()
		simBox = empro.geometry.Box( _createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox-xLowerBoundingBox", "abs((0-xLowerExtension)-(0.01+xUpperExtension))"), _createIfToggleExtensionToBoundingBoxExpression("zUpperBoundingBox-zLowerBoundingBox", "((((stack_substrate1_layer_7_Z) + (zUpperExtension)) - ((stack_substrate1_layer_1_Z) - (zLowerExtension))))"), _createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox-yLowerBoundingBox" , " abs((-0.005-yLowerExtension)-(0.01+yUpperExtension))"))
		part.recipe.append(simBox)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(_createIfToggleExtensionToBoundingBoxExpression("(xUpperBoundingBox+xLowerBoundingBox)/2", "(0.01+xUpperExtension+0-xLowerExtension)/2"), _createIfToggleExtensionToBoundingBoxExpression("(yUpperBoundingBox+yLowerBoundingBox)/2", "(0.01+yUpperExtension+-0.005-yLowerExtension)/2"), _createIfToggleExtensionToBoundingBoxExpression("zLowerBoundingBox","(((stack_substrate1_layer_1_Z) - (zLowerExtension)) - (0))")))
		part.name="Simulation box"
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=0
		empro.toolkit.applyMaterial(part,self.materials["simulation_box"])
		assembly.append(part)
		assembly.name="simulation_box"
		self.session.hide_part(assembly)
		topAssembly.append(assembly)
		self.session.adjust_view()
		assembly=empro.geometry.Assembly()
		pointString='0.01+xUpperExtension#-0.005-yLowerExtension;0.01+xUpperExtension#0.01+yUpperExtension;0-xLowerExtension#0.01+yUpperExtension;0-xLowerExtension#-0.005-yLowerExtension'
		sketch = self._create_sketch(pointString)
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex0",V(_createIfToggleExtensionToBoundingBoxExpression("xLowerBoundingBox","0-xLowerExtension"),_createIfToggleExtensionToBoundingBoxExpression("yLowerBoundingBox","-0.005-yLowerExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex1",V(_createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox","0.01+xUpperExtension"),_createIfToggleExtensionToBoundingBoxExpression("yLowerBoundingBox","-0.005-yLowerExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex2",V(_createIfToggleExtensionToBoundingBoxExpression("xUpperBoundingBox","0.01+xUpperExtension"),_createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox","0.01+yUpperExtension"),0)))
		sketch.constraintManager().append(empro.geometry.FixedPositionConstraint("vertex3",V(_createIfToggleExtensionToBoundingBoxExpression("xLowerBoundingBox","0-xLowerExtension"),_createIfToggleExtensionToBoundingBoxExpression("yUpperBoundingBox","0.01+yUpperExtension"),0)))
		part=empro.geometry.Model()
		part.recipe.append(empro.geometry.Extrude(sketch,"(stack_substrate1_layer_5_Z) - ((stack_substrate1_layer_1_Z) - (zLowerExtension))",V(0,0,1)))
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"((stack_substrate1_layer_1_Z) - (zLowerExtension)) - (0)"))
		part.name=self.substratePartNameMap["__SubstrateLayer1___BOTTOM"]
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=50
		empro.toolkit.applyMaterial(part,self.materials["__SubstrateLayer1___BOTTOM"])
		self.session.hide_part(part)
		assembly.append(part)
		assembly.name="substrate"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.0088#0.0024;0.0088#0.0088;0.0012#0.0088;0.0012#0.0012;0.01#0.0012;0.01#0.01;0#0.01;0#0;0.0044#0;0.0044#-0.005;0.005#-0.005;0.005#0.0006;0.0006#0.0006;0.0006#0.0094;0.0094#0.0094;0.0094#0.0018;0.0018#0.0018;0.0018#0.0082;0.0082#0.0082;0.0082#0.003;0.0056#0.003;0.0056#0.0024']
		part = self._create_extrude(pointStrings, "(mask_cond_Zmax) - (mask_cond_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=162
		empro.toolkit.applyMaterial(part,self.materials["cond"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._update_geoProgress()
		pointStrings=['0.0062#-0.005;0.0062#0.0006;0.0056#0.0006;0.0056#-0.005']
		part = self._create_extrude(pointStrings, "(mask_cond_Zmax) - (mask_cond_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 1)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=162
		empro.toolkit.applyMaterial(part,self.materials["cond"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="cond"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.0062#0;0.0062#0.003;0.0056#0.003;0.0056#0']
		part = self._create_extrude(pointStrings, "(mask_cond2_Zmax) - (mask_cond2_Zmin)", up=False)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_cond2_Zmax) - (0)"))
		part.setAttribute('LtdLayerNumber', 2)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=160
		empro.toolkit.applyMaterial(part,self.materials["cond2"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="cond2"
		topAssembly.append(assembly)
		assembly=empro.geometry.Assembly()
		pointStrings=['0.00589426#0.000286142;0.00590574#0.000286142;0.005913858#0.00029426;0.005913858#0.00030574;0.00590574#0.000313858;0.00589426#0.000313858;0.005886142#0.00030574;0.005886142#0.00029426']
		part = self._create_extrude(pointStrings, "(mask_hole_Zmax) - (mask_hole_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_hole_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["hole"])
		assembly.append(part)
		self.addShortcut(0,part)
		pointStrings=['0.00589426#0.002686142;0.00590574#0.002686142;0.005913858#0.00269426;0.005913858#0.00270574;0.00590574#0.002713858;0.00589426#0.002713858;0.005886142#0.00270574;0.005886142#0.00269426']
		part = self._create_extrude(pointStrings, "(mask_hole_Zmax) - (mask_hole_Zmin)", up=True)
		part.coordinateSystem.anchorPoint = empro.geometry.CoordinateSystemPositionExpression(V(0,0,"(mask_hole_Zmin) - (0)"))
		part.setAttribute('LtdLayerNumber', 5)
		part.meshParameters=empro.mesh.ModelMeshParameters()
		part.meshParameters.priority=64
		empro.toolkit.applyMaterial(part,self.materials["hole"])
		assembly.append(part)
		self.addShortcut(0,part)
		self._setAssemblyMeshSettings(assembly,0,0,0)
		assembly.name="hole"
		topAssembly.append(assembly)
		return symbPinData
		# End of create_geometry

	def _update_geoProgress(self):
		self.geoProgress+= 1
		if self.geoProgress % 1 == 0:
			progress = (self.geoProgress * 100)/1
			self._updateProgress(progress)

	def getMaskHeights(self,parameterized=False):
		mask_heights={}
		mask_heights_parameterized={}
		mask_heights[2]=(0, 3.5e-05)
		mask_heights_parameterized[2]=("(mask_cond2_Zmin) - (0)", "(mask_cond2_Zmax) - (0)")
		mask_heights[5]=(3.5e-05, 0.001051)
		mask_heights_parameterized[5]=("(mask_hole_Zmin) - (0)", "(mask_hole_Zmax) - (0)")
		mask_heights[1]=(0.001051, 0.001086)
		mask_heights_parameterized[1]=("(mask_cond_Zmin) - (0)", "(mask_cond_Zmax) - (0)")
		if(parameterized):
			return mask_heights_parameterized
		else:
			return mask_heights

	def getMaskHeightsParameterized(self):
		return self.getMaskHeights(parameterized=True)

	def create_ports( self, topAssembly, includeInvalidPorts=True, symbPinData=None):
		self.setPortWarnings(includeInvalidPorts)
		V=empro.geometry.Vector3d
		L=empro.geometry.Line
		SPAresabs=empro.activeProject.newPartModelingUnit.toReferenceUnits(1e-6)
		if topAssembly != None:
			bbox_geom = topAssembly.boundingBox()
		else:
			bbox_geom = empro.activeProject.geometry.boundingBox()
		xLowerBoundary = float(bbox_geom.lower.x)
		xUpperBoundary = float(bbox_geom.upper.x)
		yLowerBoundary = float(bbox_geom.lower.y)
		yUpperBoundary = float(bbox_geom.upper.y)
		zLowerBoundary = float(bbox_geom.lower.z)
		zUpperBoundary = float(bbox_geom.upper.z)
		internalPortOnXLowerBoundary = False
		internalPortOnXUpperBoundary = False
		internalPortOnYLowerBoundary = False
		internalPortOnYUpperBoundary = False
		internalPortOnZLowerBoundary = False
		internalPortOnZUpperBoundary = False
		ports=[]
		waveguides={}
		portShortcutGroups=[]
		assembly=empro.geometry.Assembly()
		waveform=empro.waveform.Waveform("Broadband Pulse")
		waveform.shape=empro.waveform.MaximumFrequencyWaveformShape()
		self.waveforms["Broadband Pulse"]=waveform
		if getSessionVersion(self.session) >= 7:
			self.session.appendUniqueWaveforms(self.waveforms)
		else:
			for name,waveform in self.waveforms.items():
				empro.activeProject.waveforms.append(waveform)
				self.waveforms[name] = empro.activeProject.waveforms[len(empro.activeProject.waveforms)-1]
		feed=empro.components.Feed()
		feed.name="50 ohm Voltage Source"
		feed.impedance.resistance=50
		feed.waveform=self.waveforms["Broadband Pulse"]
		self.circuitComponentDefinitions[feed.name]=feed
		if getSessionVersion(self.session) >= 7:
			self.session.appendUniqueCircuitComponentDefinitions(self.circuitComponentDefinitions)
		else:
			for name,compDef in self.circuitComponentDefinitions.items():
				empro.activeProject.circuitComponentDefinitions.append(compDef)
				self.circuitComponentDefinitions[name] = empro.activeProject.circuitComponentDefinitions[len(empro.activeProject.circuitComponentDefinitions)-1]
		if includeInvalidPorts:
			head=V("(0.0047) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			tail=V("(0.0047) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			extent=empro.components.SheetExtent()
			extent.endPoint1Position=V("(0.0044) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			extent.endPoint2Position=V("(0.005) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			port = self._create_internal_port("P2","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 1, "P2", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		if includeInvalidPorts:
			head=V("(0.0059) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			tail=V("(0.0059) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			extent=empro.components.SheetExtent()
			extent.endPoint1Position=V("(0.0056) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			extent.endPoint2Position=V("(0.0062) - (0)","(-0.005) - (0)","(((mask_cond_Zmax) + (mask_cond_Zmin)) / (2)) - (0)")
			port = self._create_internal_port("P3","50 ohm Voltage Source",head,tail,extent)
			portShortcutGroups.append((0,port))
			ports.append(port)
			self._set_extra_port_info(port, "inputOutput", 2, "P3", "Direct")
			headsAndTails = (head if isinstance(head, list) else [head]) + (tail if isinstance(tail, list) else [tail])
			for headOrTail in headsAndTails:
				if abs(float(headOrTail.x) - xLowerBoundary) < SPAresabs: internalPortOnXLowerBoundary = True
				if abs(float(headOrTail.x) - xUpperBoundary) < SPAresabs: internalPortOnXUpperBoundary = True
				if abs(float(headOrTail.y) - yLowerBoundary) < SPAresabs: internalPortOnYLowerBoundary = True
				if abs(float(headOrTail.y) - yUpperBoundary) < SPAresabs: internalPortOnYUpperBoundary = True
				if abs(float(headOrTail.z) - zLowerBoundary) < SPAresabs: internalPortOnZLowerBoundary = True
				if abs(float(headOrTail.z) - zUpperBoundary) < SPAresabs: internalPortOnZUpperBoundary = True
		setPortNbToNameMappingInitialized()
		try:
			if getSessionVersion(self.session) >= 5:
				self.session.appendPortList(ports,None,portShortcutGroups)
			else:
				self.session.appendPortList(ports,self.groupList,portShortcutGroups)
		except AttributeError:
			empro.activeProject.circuitComponents().appendList(ports)
			for group,port in portShortcutGroups:
				self.addShortcut(group,port)
		for i in waveguides.keys():
			empro.activeProject.waveGuides.append(waveguides[i])
		assembly.name="waveguide_planes"
		self.session.hide_part(assembly)

	def create_grid_regions(self):
		gG = empro.activeProject.gridGenerator

	def create_parameters(self):
		self._create_parameter("stack_substrate1_layer_1_Z", "0 um", "Z of topology level (level 1 of stack substrate1)",True,fixGridAxis='Z')
		self._create_parameter("stack_substrate1_layer_3_Z", "35 um", "Z of topology level (level 3 of stack substrate1)",True,fixGridAxis='Z')
		self._create_parameter("stack_substrate1_layer_5_Z", "1051 um", "Z of topology level (level 5 of stack substrate1)",True,fixGridAxis='Z')
		self._create_parameter("stack_substrate1_layer_7_Z", "1086 um", "Z of topology level (level 7 of stack substrate1)",True,fixGridAxis='Z')
		self._create_parameter("lateralExtension","3125 um","Substrate LATERAL extension", True)
		self._create_parameter("verticalExtension","5000 um","Substrate VERTICAL extension", True)
		self._create_parameter("xLowerExtension", "lateralExtension", "Lower X extension", True)
		self._create_parameter("xUpperExtension", "lateralExtension", "Upper X extension", True)
		self._create_parameter("yLowerExtension", "lateralExtension", "Lower Y extension", True)
		self._create_parameter("yUpperExtension", "lateralExtension", "Upper Y extension", True)
		self._create_parameter("zLowerExtension", "verticalExtension", "Lower Z extension", True)
		self._create_parameter("zUpperExtension", "verticalExtension", "Upper Z extension", True)
		if get_ads_import_version() >= 11 :
			self._create_parameter("toggleExtensionToBoundingBox", 0, "toggle extension of gnd/substrate layers to bounding box of geometry", True)
			self._create_parameter("xLowerBoundingBox", 0.0, "lower X coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("yLowerBoundingBox", 0.0, "lower Y coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("zLowerBoundingBox", 0.0, "lower Z coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("xUpperBoundingBox", 0.0, "upper X coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("yUpperBoundingBox", 0.0, "upper Y coordinate of bounding box of geometry (for extension of covers)", True)
			self._create_parameter("zUpperBoundingBox", 0.0, "upper Z coordinate of bounding box of geometry (for extension of covers)", True)
		self._create_parameter("mask_cond2_Zmin",str("0 um"),"Zmin of mask cond2",True,fixGridAxis='Z')
		self._create_parameter("mask_cond2_Zmax",str("35 um"),"Zmax of mask cond2",True,fixGridAxis='Z')
		self._create_parameter("mask_hole_Zmin",str("35 um"),"Zmin of mask hole",True,fixGridAxis='Z')
		self._create_parameter("mask_hole_Zmax",str("1051 um"),"Zmax of mask hole",True,fixGridAxis='Z')
		self._create_parameter("mask_cond_Zmin",str("1051 um"),"Zmin of mask cond",True,fixGridAxis='Z')
		self._create_parameter("mask_cond_Zmax",str("1086 um"),"Zmax of mask cond",True,fixGridAxis='Z')

def maxNbThreadsADS():
	maxNbThreads=0
	return maxNbThreads


g_portNbToName={}
g_portNbToNameInitialized=False

def portNbToName():
	if g_portNbToNameInitialized == True:
		return g_portNbToName
	raise RuntimeError("portNbToName used uninitialized")

def setPortNbToNameMappingInitialized( state = True ):
	global g_portNbToNameInitialized
	g_portNbToNameInitialized = True

def radiationPossible():
	return True

def main():
	try:
		demoMode=empro.toolkit.ads_import.useDemoMode()
	except AttributeError:
		demoMode=False
	try:
		ads_import(demoMode=demoMode)
	except Exception:
		empro.toolkit.ads_import.notify_failure()
		raise

if __name__=="__main__":
	main()
	del ads_import
