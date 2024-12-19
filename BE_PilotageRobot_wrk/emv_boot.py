# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/isen/BE_PilotageRobot_ADS/BE_PilotageRobot_wrk"
	lib=r"BE_PilotageRobot_lib"
	subst=r"BE_PilotageRobot_lib/substrate1.subst"
	substlib=r"BE_PilotageRobot_lib"
	substname=r"substrate1"
	cell=r"antenna_layout"
	view=r"layout"
	libS3D=r"simulation/BE_PilotageRobot_lib/antenna_layout/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
