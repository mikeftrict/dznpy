@ECHO OFF
REM Configuration by dznpy/developer
SET dzncmd=C:\SB\dezyne-2.17.8\dzn.cmd

REM Predefined configuration
SET includes=-I . -I ..\shared\Facilities
SET scriptroot=%~dp0%
SET modelsroot=%~dp0%dezyne_models\system1
SET genfolder=%~dp0%dezyne_models\generated

ECHO Script configuration:
ECHO  - dzncmd=%dzncmd%
ECHO  - scriptroot=%scriptroot%
ECHO  - modelsroot=%modelsroot%
ECHO  - genfolder=%genfolder%
ECHO.

IF NOT EXIST %dzncmd% (
  ECHO dzn.cmd not found, please correct script variable dzncmd
  goto :exitFailure
)

ECHO Starting processing

CD %modelsroot%
DEL /Q %genfolder%\* >nul 2> nul

CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ Hardware\Interfaces\IPowerCord.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ Hardware\Interfaces\IHeaterElement.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ Hardware\Interfaces\ILed.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ IToaster.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ StoneAgeToaster.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ Toaster.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ -s ToasterOne TwoToasters.dzn
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l c++ -s My.Project.ToasterSystem ToasterSystem.dzn

CALL %dzncmd% -v -p code %includes% -o %genfolder% -l json ToasterSystem.dzn > %genfolder%\ToasterSystem.json
CALL %dzncmd% -v -p code %includes% -o %genfolder% -l json StoneAgeToaster.dzn > %genfolder%\StoneAgeToaster.json

ECHO Finished
CD %scriptroot%
EXIT /B 0

:exitFailure
CD %scriptroot%
EXIT /B 1
