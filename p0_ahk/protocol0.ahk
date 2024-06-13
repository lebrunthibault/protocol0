#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
#SingleInstance force
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
SetTitleMatchMode, 2
CoordMode,mouse,screen

#Include %A_ScriptDir%/_lib.ahk

; Control: ^
; Shift: +
; Alt: !
; Win: #

; loop must be before any return
Loop, 9 {
    HotKey ~^NumPad%A_Index%, FireSceneToPosition
}
Loop, 9 {
    HotKey, ^SC%A_Index%, FireSceneToPosition
}
^NumPad0::
    GoSub, FireSceneToPosition
return

; global hotkeys
^#+n::
	callBackend("reload_ableton")
return
#e::
    Run, explorer.exe "D:\ableton projects\tracks"
return

; ableton hotkeys
#IfWinActive, ahk_exe Ableton Live 11 Suite.exe
^+z::
    Send ^y  ; redo
return
^space::
	callBackend("scene/fire_selected")
return
+space::
	callBackend("scene~/fire_to_last_position")
return
FireSceneToPosition:
    barLength:=SubStr(A_ThisHotkey,"^NumPad") - 1
	callBackend("scene/fire_to_position?bar_length="barLength)
Return
^+c::
    MouseGetPos, xpos, ypos
    ; Right-click at the current mouse position
    Click, Right, %xpos%, %ypos%
    Send crop
    Sleep 5
    Send {Enter}
    callBackend("clip/loop_selected")
return
~^e::
	callBackend("clip/toggle_notes")
return
;edit grid size
*^NumpadEnd::
    Send ^{numpad1}
return
*^NumpadDown::
    Send ^{numpad2}
return
;^+e::
;	callBackend("clip/edit_automation_value")
;return
~^l::
	callBackend("scene/toggle_loop")
return
^+*::
    Send {Right}
return
^s::
	callBackend("set/save")
	Sleep, 200
    Send ^s
return
^+!r::
	callBackend("export")
return
^!q::
    Send ^!p  ; left hand shortcut
return
^+d::
	callBackend("scene/duplicate")
return
!r::
	callBackend("monitoring/toggle_reference")
return
!+r::
	callBackend("monitoring/toggle_reference_filters")
return
!Numpad0::
	callBackend("monitoring/toggle_reference_filters")
return
!Numpad1::
	callBackend("monitoring/toggle_reference_filters?preset=sub")
return
!Numpad2::
	callBackend("monitoring/toggle_reference_filters?preset=bass")
return
!Numpad3::
	callBackend("monitoring/toggle_reference_filters?preset=low_mid")
return
!Numpad4::
	callBackend("monitoring/toggle_reference_filters?preset=mid")
return
!Numpad5::
	callBackend("monitoring/toggle_reference_filters?preset=high")
return
!Numpad7::
	callBackend("monitoring/toggle_reference_stereo_mode?stereo_mode=mono")
return
!Numpad8::
	callBackend("monitoring/toggle_reference_stereo_mode?stereo_mode=sides")
return
!Numpad9::
	callBackend("monitoring/toggle_reference_stereo_mode?stereo_mode=stereo")
return
~^+f::
	Send ^+f  ; cancel Ableton Follow
	callBackend("search/track")
return
^+!f::
	callBackend("search/track?reset=true")
return
^NumpadSub::
    callBackend("track/collapse_selected")
return

; SELECTING TRACKS
^+k::
    callBackend("track/select?name=kick")
return
^+h::
    callBackend("track/select?name=hat")
return
^+p::
    callBackend("track/select?name=perc")
return
^+v::
    callBackend("track/select?name=vocals")
return
^+::
    callBackend("track/select?name=harmony")
return
^+l::
    callBackend("track/select?name=lead")
return
^+b::
    callBackend("track/select?name=bass")
return

#IfWinActive

; splice window
#IfWinActive ahk_exe Splice.exe
^space::
	callBackend("scene/fire_selected")
return
!r::
	callBackend("monitoring/toggle_reference")
return
!+r::
	callBackend("monitoring/toggle_reference_filters")
return
#IfWinActive
