@ECHO OFF

REM
SET project_root=%~dp0..\

REM Set paths
SET sass_path=sass
SET styles_path=D:\GitHub\gmldoc\styles\

SET output_path=%project_root%gmldoc\docs\styles\

REM Create folder(s) for output path (in case they do not exist)
ECHO Creating output directories
md %output_path%

REM Run compiler on \styles
ECHO Compiling styles\all.css
CALL %sass_path% %styles_path%all.scss > %output_path%all.css
ECHO Done.

REM Run compressor on \styles
ECHO Compressing styles\all.min.css
CALL %sass_path% %styles_path%all.scss > %output_path%all.min.css --style compressed
ECHO Done.

REM Keep the console window open
ECHO Styles done.
REM PAUSE