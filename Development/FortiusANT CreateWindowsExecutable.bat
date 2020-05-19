cd ..\pythoncode
del dist\FortiusANT.exe
pyinstaller --clean MakeFortiusANT.spec
move dist\FortiusANT.exe ..\WindowsExecutable
pause