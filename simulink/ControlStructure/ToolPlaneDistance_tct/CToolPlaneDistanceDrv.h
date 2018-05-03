﻿// ****************** CToolPlaneDistanceDrv.h *******************************
// Generated by TwinCAT Target for MATLAB/Simulink (TE1400)
// MATLAB R2017b (win64)
// TwinCAT 3.1.4022
// TwinCAT Target 1.2.1230
// Beckhoff Automation GmbH & Co. KG     (www.beckhoff.com)
// *************************************************************
#ifndef CTOOLPLANEDISTANCEDRV_H_INCLUDED
#define CTOOLPLANEDISTANCEDRV_H_INCLUDED

#include "TcPch.h"

#define ToolPlaneDistanceDRV_NAME			"ToolPlaneDistance"
#define ToolPlaneDistanceDRV_Major			1
#define ToolPlaneDistanceDRV_Minor			0

#if defined DEVICE_MAIN		// is supposed to be __cplusplus

#define DEVICE_CLASS			CToolPlaneDistanceDrv

#include "ObjDriver.h"

class CToolPlaneDistanceDrv : public CObjDriver
{
public:
	virtual IOSTATUS	OnLoad( );
	virtual VOID		OnUnLoad( );
	
  //////////////////////////////////////////////////////
  // VxD-Services exported by this driver
  static unsigned long _cdecl ToolPlaneDistance_GetVersion( );
};

#endif	// #if defined DEVICE_MAIN

Begin_VxD_Service_Table( ToolPlaneDistanceDRV)
	VxD_Service( ToolPlaneDistance_GetVersion		)
End_VxD_Service_Table


#endif