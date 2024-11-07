@ECHO OFF
REM Dynamic configuration by dznpy user/developer
SET dzncmd=C:\SB\dezyne-2.17.8\dzn.cmd

REM Predefined static configuration
SET includes=-I . -I ..\shared\Facilities
SET callerroot=%CD%
SET scriptroot=%~dp0%
SET modelsroot=%~dp0%dezyne_models\system1
SET genfolder=%~dp0%dezyne_models\generated

REM Esnure to have an absolute filepath of dzn.cmd
CD %scriptroot%
CALL :absolutizeDznCmdPath %dzncmd%
SET dzncmd_abs=%ABSPATH_RETVAL%

ECHO Script configuration:
ECHO  - dzncmd (user) = %dzncmd%
ECHO  - dzncmd_abs    = %dzncmd_abs%
ECHO  - callerroot    = %callerroot%
ECHO  - scriptroot    = %scriptroot%
ECHO  - modelsroot    = %modelsroot%
ECHO  - genfolder     = %genfolder%
ECHO.

IF NOT EXIST %dzncmd_abs% (
  ECHO dzn.cmd not found, please correct script variable dzncmd
  goto :exitFailure
)

ECHO Starting processing

CD %modelsroot%
DEL /Q %genfolder%\* >nul 2> nul

CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ Hardware\Interfaces\IPowerCord.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ Hardware\Interfaces\IHeaterElement.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ Hardware\Interfaces\ILed.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ IExclusiveToaster.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ IToaster.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ ExclusiveToaster.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ StoneAgeToaster.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ Toaster.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ -s ToasterOne TwoToasters.dzn
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l c++ -s My.Project.ToasterSystem ToasterSystem.dzn

CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l json ToasterSystem.dzn > %genfolder%\ToasterSystem.json
CALL %dzncmd_abs% -v -p code %includes% -o %genfolder% -l json StoneAgeToaster.dzn > %genfolder%\StoneAgeToaster.json

ECHO Finished
CD %callerroot%
EXIT /B 0

:absolutizeDznCmdPath
SET ABSPATH_RETVAL=%~f1
EXIT /B

:exitFailure
CD %callerroot%
EXIT /B 1
