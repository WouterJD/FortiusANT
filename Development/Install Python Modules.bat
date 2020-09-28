@rem for %~dp0 refer to https://stackoverflow.com/questions/672693/windows-batch-file-starting-directory-when-run-as-admin

@echo Upgrade pip and install modules

@if "%~dp0"=="%cd%\" if exist "C:\Program Files (x86)\Python38-32" (
@echo Python is installed for all users, run as administrator!
@goto Done
)

@rem check pip itself
python -m pip install --upgrade pip

@rem check modules
pip install -r "%~dp0%\..\pythoncode\requirements.txt"

:Done
@pause