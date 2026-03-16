Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d ""C:\Users\Sean Goudy\developer-automation-agent-visualizer"" && npm run dev", 0, False
