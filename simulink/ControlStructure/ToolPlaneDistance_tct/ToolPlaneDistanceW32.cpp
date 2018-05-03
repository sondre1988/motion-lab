﻿// ****************** ToolPlaneDistanceW32.cpp *******************************
// Generated by TwinCAT Target for MATLAB/Simulink (TE1400)
// MATLAB R2017b (win64)
// TwinCAT 3.1.4022
// TwinCAT Target 1.2.1230
// Beckhoff Automation GmbH & Co. KG     (www.beckhoff.com)
// *************************************************************
#include "TcPch.h"
#pragma hdrstop

#include "TcPch.h"
#include "ToolPlaneDistanceCtrl.h"
#include "TcSysW32_i.c"

CComModule _Module;

const   CLSID   IID_ToolPlaneDistanceCtrl		=  {0x4883cf3d,0x8284,0x45eb,{0xb5,0x29,0x21,0x06,0xd8,0x6b,0xe9,0x87}};
const   CLSID   LIBID_ToolPlaneDistanceW32Lib	=  {0x4883cf3d,0x8284,0x45eb,{0xb5,0x29,0x21,0x06,0xd8,0x6b,0xe9,0x87}};
const   CLSID   CLSID_ToolPlaneDistanceCtrl   =  {0x4883cf3d,0x8284,0x45eb,{0xb5,0x29,0x21,0x06,0xd8,0x6b,0xe9,0x87}};

BEGIN_OBJECT_MAP(ObjectMap)
OBJECT_ENTRY(CLSID_ToolPlaneDistanceCtrl, CToolPlaneDistanceCtrl)
END_OBJECT_MAP()

/////////////////////////////////////////////////////////////////////////////
// DLL Entry Point

extern "C"
BOOL WINAPI DllMain(HANDLE hInstance, DWORD dwReason, LPVOID /*lpReserved*/)
{
	if (dwReason == DLL_PROCESS_ATTACH)
	{
		_Module.Init(ObjectMap, (HINSTANCE)hInstance);
#ifndef UNDER_CE
		DisableThreadLibraryCalls((HINSTANCE)hInstance);
#endif
	}
	else if (dwReason == DLL_PROCESS_DETACH)
		_Module.Term();
	return TRUE;    // ok
}

/////////////////////////////////////////////////////////////////////////////
// Used to determine whether the DLL can be unloaded by OLE

STDAPI DllCanUnloadNow(void)
{
	return (_Module.GetLockCount()==0) ? S_OK : S_FALSE;
}

/////////////////////////////////////////////////////////////////////////////
// Returns a class factory to create an object of the requested type

STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID* ppv)
{
	return _Module.GetClassObject(rclsid, riid, ppv);
}

/////////////////////////////////////////////////////////////////////////////
// DllRegisterServer - Adds entries to the system registry

STDAPI DllRegisterServer(void)
{
	// registers object, typelib and all interfaces in typelib
	return _Module.RegisterServer(TRUE);
}

/////////////////////////////////////////////////////////////////////////////
// DllUnregisterServer - Removes entries from the system registry

STDAPI DllUnregisterServer(void)
{
	_Module.UnregisterServer();
	return S_OK;
}

/////////////////////////////////////////////////////////////////////////////
STDAPI DllGetTcCtrl(ITcCtrl** ppCtrl)
{
	if ( ppCtrl == NULL )
		return E_POINTER;

	CComObject<CToolPlaneDistanceCtrl>* pCToolPlaneDistanceCtrl = new CComObject<CToolPlaneDistanceCtrl>();
	if (pCToolPlaneDistanceCtrl == NULL) return E_POINTER;
	return pCToolPlaneDistanceCtrl->QueryInterface(IID_ITcCtrl, reinterpret_cast<void**>(ppCtrl));
}