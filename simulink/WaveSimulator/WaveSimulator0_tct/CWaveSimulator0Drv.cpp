﻿// ****************** CWaveSimulator0Drv.cpp *******************************
// Generated by TwinCAT Target for MATLAB/Simulink (TE1400)
// MATLAB R2019a (win64)
// TwinCAT 3.1.4022
// TwinCAT Target 1.2.1237
// Beckhoff Automation GmbH & Co. KG     (www.beckhoff.com)
// *************************************************************
#include "TcPch.h"
#pragma hdrstop
#define DEVICE_MAIN

#include "CWaveSimulator0Drv.h"
#include "CWaveSimulator0.h"
#include "CWaveSimulator0ClassFactory.h"
#include "WaveSimulator0Version.h"

DECLARE_GENERIC_DEVICE(WaveSimulator0DRV)
#undef DEVICE_MAIN

IOSTATUS CWaveSimulator0Drv::OnLoad( )
{
	TRACE(_T("CWaveSimulator0ClassFactory::OnLoad()\n") );
	m_pObjClassFactory = new CWaveSimulator0ClassFactory();

	return IOSTATUS_SUCCESS;
}

VOID CWaveSimulator0Drv::OnUnLoad( )
{
	delete m_pObjClassFactory;
}

unsigned long _cdecl CWaveSimulator0Drv::WaveSimulator0_GetVersion( )
{
	return(0);
}