@ECHO OFF
REM This batch file will ask the user for the paramters and then run the python code with them
REM This will most likely require admin privileges to run, since it will have to recognize python

REM "%~dp0" is the path to the batch file itself.

REM
SET python_path=C:\Python27\python.exe
SET script_path=%~dp0gmdoc.py

SET project_path=C:\GameMaker\Projects\Example.gmx\Example.project.gmx
SET output_path=%~dp0output\

REM Get project and output paths from the user
SET input_path=""
SET /p input_path="Enter Project File Path (ends with .project.gmx): "
IF [%input_path] == [] SET project_path=input_path

SET input_path=""
SET /p input_path="Enter Output Directory Path (does not need to exist): "
IF [%input_path] == [] SET output_input=input_path

REM Run document creation code
%python_path% %script_path% %project_path% %output_path%

REM Keep the console window open
PAUSE