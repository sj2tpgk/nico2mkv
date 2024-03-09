SET SCRIPTDIR=%~dp0
SET VENVDIR=%SCRIPTDIR%\nico2mkv\.venv-win\

if not exist %VENVDIR% ( echo Creating venv ... && python3 -m venv %VENVDIR% )
call %VENVDIR%\Scripts\activate

python %SCRIPTDIR%\nico2mkv\nico2mkv.py %*
