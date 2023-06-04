[Auto Hotkey](https://www.autohotkey.com/) shortcuts to reach the protocol0 api
and control the [protocol0 script](https://github.com/lebrunthibault/protocol0/tree/main/p0_script)

Doing hotkey detection in python didn't work as well, that's why I kept this (windows) dependency.

In the 'standard' way of executing backend code via ahk, we usually follow these steps :
- hotkey pressed
- ahk dispatches a GET request to the p0 http api
- the backend code executes, potentially forwarding the command to the script
- In this last case the ahk will in the end trigger a script command (eg 'ToggleSceneLoopCommand')

# Install
- install [AHK](https://www.autohotkey.com/)
- run protocol0.ahk