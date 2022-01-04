@echo pyinstaller is documented: https://pyinstaller.readthedocs.io/en/stable/
@echo the .exe is "unpacked" into C:\Users\%username%\AppData\Local\Temp

cd ..\pythoncode
del dist\FortiusANT.exe
pyinstaller --clean MakeFortiusANT.spec
move dist\FortiusANT.exe ..\WindowsExecutable
pause