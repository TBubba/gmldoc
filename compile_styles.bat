@ECHO OFF
REM This batch file will compile all styles in the \styles folder
REM This will most likely require admin privileges to run, since it will have to recognize python

REM "%~dp0" is the path to the batch file itself.

REM
SET sass_path=sass
SET styles_path=%~dp0styles\

REM Run compiler on \styles
ECHO Compiling styles\all.css
%sass_path% %styles_path%all.scss > %styles_path%all.css
ECHO Done.

REM Keep the console window open
ECHO All done.
PAUSE