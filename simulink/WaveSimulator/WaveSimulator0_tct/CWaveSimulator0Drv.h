﻿// ****************** CWaveSimulator0Drv.h *******************************
// Generated by TwinCAT Target for MATLAB/Simulink (TE1400)
// MATLAB R2019a (win64)
// TwinCAT 3.1.4022
// TwinCAT Target 1.2.1237
// Beckhoff Automation GmbH & Co. KG     (www.beckhoff.com)
// *************************************************************
#ifndef CWAVESIMULATOR0DRV_H_INCLUDED
#define CWAVESIMULATOR0DRV_H_INCLUDED

#include "TcPch.h"

#define WaveSimulator0DRV_NAME			"WaveSimulator0"
#define WaveSimulator0DRV_Major			1
#define WaveSimulator0DRV_Minor			0

#if defined DEVICE_MAIN		// is supposed to be __cplusplus

#define DEVICE_CLASS			CWaveSimulator0Drv

#include "ObjDriver.h"

class CWaveSimulator0Drv : public CObjDriver
{
public:
	virtual IOSTATUS	OnLoad( );
	virtual VOID		OnUnLoad( );
	
  //////////////////////////////////////////////////////
  // VxD-Services exported by this driver
  static unsigned long _cdecl WaveSimulator0_GetVersion( );
};

#endif	// #if defined DEVICE_MAIN

Begin_VxD_Service_Table( WaveSimulator0DRV)
	VxD_Service( WaveSimulator0_GetVersion		)
End_VxD_Service_Table


#endif
