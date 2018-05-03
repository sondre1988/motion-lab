﻿// ****************** CToolPlaneDistanceDrv.cpp *******************************
// Generated by TwinCAT Target for MATLAB/Simulink (TE1400)
// MATLAB R2017b (win64)
// TwinCAT 3.1.4022
// TwinCAT Target 1.2.1230
// Beckhoff Automation GmbH & Co. KG     (www.beckhoff.com)
// *************************************************************
#include "TcPch.h"
#pragma hdrstop
#define DEVICE_MAIN

#include "CToolPlaneDistanceDrv.h"
#include "CToolPlaneDistance.h"
#include "CToolPlaneDistanceClassFactory.h"
#include "ToolPlaneDistanceVersion.h"

DECLARE_GENERIC_DEVICE(ToolPlaneDistanceDRV)
#undef DEVICE_MAIN

IOSTATUS CToolPlaneDistanceDrv::OnLoad( )
{
	TRACE(_T("CToolPlaneDistanceClassFactory::OnLoad()\n") );
	m_pObjClassFactory = new CToolPlaneDistanceClassFactory();

	return IOSTATUS_SUCCESS;
}

VOID CToolPlaneDistanceDrv::OnUnLoad( )
{
	delete m_pObjClassFactory;
}

unsigned long _cdecl CToolPlaneDistanceDrv::ToolPlaneDistance_GetVersion( )
{
	return(0);
}