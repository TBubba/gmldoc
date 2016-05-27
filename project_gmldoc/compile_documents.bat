@ECHO OFF

REM
SET project_root=%~dp0..\

REM Set paths
SET python_path=C:\Python27\python.exe
SET script_path=D:\GitHub\gmldoc\gmdoc.py

SET project_path=%project_root%BubbasStash.project.gmx
SET output_path=%project_root%gmldoc\docs\

REM Create folder(s) for output path (in case they do not exist)
ECHO Creating output directories
md %output_path%

REM Run document generation script
ECHO Compiling documents
CALL %python_path% %script_path% %project_path% %output_path%

REM Keep the console window open
ECHO Documents done.
REM PAUSE