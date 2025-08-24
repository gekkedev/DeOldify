REM for powershell: docker run --rm -v ${PWD}/../video:/app/video deoldify python VideoColorizer.py
docker run --rm -v %cd%\..\video:/app/video deoldify python VideoColorizer.py & PAUSE