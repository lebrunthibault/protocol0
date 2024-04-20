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
^#+l::
	callBackend("tail_logs")
return
#e::
    Run, explorer.exe "D:\ableton projects"
return

; ableton hotkeys
#IfWinActive, ahk_exe Ableton Live 11 Suite.exe
^+z::
    Send ^y  ; redo
return
^#+s::
    Send ^,  ; works best from ahk
    callBackend("set/save_as_template")
return
^+a::
	callBackend("track/arm")
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
^Up::
	callBackend("scene/scroll?direction=next")
return
^Down::
	callBackend("scene/scroll?direction=prev")
return
;^q::
;	callBackend("clip/show_automation?direction=next")
;return
;^+q::
;	callBackend("clip/show_automation?direction=prev")
;return
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
^+_::
    Send {Up}
return
^+&::
    Send {Down}
return
^+$::
    Send {Left}
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
!f:: ; fold / unfold set
	Send `t
	Send !u
	Sleep 50
	Send !u
	Send `t
return
^+d::
	callBackend("scene/duplicate")
return
^+f::
	callBackend("search/track")
return

#IfWinActive

; minitaur editor
#IfWinActive ahk_class JUCE_18999b05416
^space::
	callBackend("scene/fire_selected")
return
#IfWinActive

; splice window
#IfWinActive ahk_exe Splice.exe
^space::
	callBackend("scene/fire_selected")
return
#IfWinActive
