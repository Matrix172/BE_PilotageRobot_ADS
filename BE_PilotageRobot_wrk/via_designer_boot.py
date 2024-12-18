# -*- coding: utf-8 -*-

# Copyright Keysight Technologies 2017 - 2020

def main():
	import os, sys
	varDictionary={}
	exprDictionary={}
	ADS_HPEESOF_DIR=r"D:\Keysight\ADS2025_Update1"
	libName=r"BE_PilotageRobot_lib"
	substName=r"substrate1"
	workspacePath=r"D:\Keysight\mdejeante\BE_PilotageRobot_ADS\BE_PilotageRobot_wrk"
	libdefs=r"lib.defs"
	envEMPROHOME=r"D:\Keysight\ADS2025_Update1\fem\2025.10/Win32_64/bin"
	verbose=False
	sys.path.append(os.path.join(envEMPROHOME))
	import empro.toolkit.via_designer as via_designer

	via_designer.mainGui.main(varDictionary, exprDictionary, ADS_HPEESOF_DIR, libName, substName, workspacePath=workspacePath, libdefs=libdefs, verbose=verbose)

if __name__=="__main__":
	main()
