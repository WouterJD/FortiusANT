cd ..\pythoncode
del dist\ExplorANT.exe
pyinstaller --clean MakeExplorANT.spec
move dist\ExplorANT.exe ..\WindowsExecutable
pause