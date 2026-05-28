Set objShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
objShell.Run "msedge --app=""file:///" & Replace(strPath, "\", "/") & "/resonance-tuner.html"" --start-fullscreen", 0, False
