@ECHO OFF

REM Run document compiler
CALL %~dp0compile_documents.bat

REM Run styles compiler
CALL %~dp0compile_styles.bat

REM
ECHO All done.