@echo pyinstaller is documented: https://pyinstaller.readthedocs.io/en/stable/
@echo the .exe is "unpacked" into C:\Users\%username%\AppData\Local\Temp

cd ..\pythoncode
del dist\FortiusANT.exe
@echo 2023-01-13 I hade to "pip install -U pyinstaller" to resolve errors
pyinstaller --clean MakeFortiusANT.spec
move dist\FortiusANT.exe ..\WindowsExecutable
pause