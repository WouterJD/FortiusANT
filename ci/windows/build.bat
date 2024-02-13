@echo off

:: Automated build for the FortiusANT and ExplorANT executables on Windows.
call :DOWNLOAD_LIBUSB || goto :ERROR
call :INSTALL_PACKAGES || goto :ERROR
call :BUILD_EXPLORANT || goto :ERROR
call :BUILD_FORTIUSANT || goto :ERROR

echo Build succeeded
exit /b 0
::

:: DOWNLOAD_LIBUSB
:: 
:: Download libusb driver and place it in the system32 folder so it can be found by pyinstaller
:DOWNLOAD_LIBUSB
setlocal
bitsadmin /transfer downloadJob /download /priority foreground https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/libusb-win32-bin-1.2.6.0.zip %cd%\libusb-win32-bin-1.2.6.0.zip ^
  || exit /b 1
tar -xf %cd%\libusb-win32-bin-1.2.6.0.zip ^
  || exit /b 1
copy %cd%\libusb-win32-bin-1.2.6.0\bin\amd64\libusb0.dll C:\Windows\System32\libusb0.dll ^
  || exit /b 1

exit /b 0
endlocal
::

:: INSTALL_PACKAGES
::
:: Install all required pip packages
:INSTALL_PACKAGES
setlocal
pushd pythoncode
python -m pip install --upgrade pip ^
  || exit /b 1
pip install pyinstaller ^
  || exit /b 1
pip install -r requirements.txt ^
  || exit /b 1

popd
exit /b 0
endlocal
::

:: BUILD_EXPLORANT
::
:: Build the ExplorANT executable
:BUILD_EXPLORANT
setlocal
pushd pythoncode
pyinstaller --clean MakeExplorANT.spec ^
  || exit /b 1

popd
exit /b 0
endlocal
::

:: BUILD_FORTIUSANT
::
:: Build the FortiusANT executable
:BUILD_FORTIUSANT
setlocal
pushd
cd pythoncode
pyinstaller --clean MakeFortiusANT.spec ^
  || exit /b 1

exit /b 0
popd
endlocal
::

:: ERROR
::
:: Exit on failure
:ERROR
echo Build failed
exit /b 1
::
