python pygame2exe.py py2exe
for %%i in (.\dist\*) do move "%%i" "."
rmdir dist /s /q