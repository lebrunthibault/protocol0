#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
#SingleInstance force
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
SetTitleMatchMode, 2
CoordMode,mouse,screen

#Include %A_ScriptDir%/lib.ahk

; Control: ^
; Shift: +
; Alt: !
; Win: #

; loop must be before any return
Loop, 9 {
    HotKey, ^NumPad%A_Index%, FireSceneToPosition
}
Loop, 9 {
    HotKey, ^SC%A_Index%, FireSceneToPosition
}
return

; global hotkeys
^#+n::
	callBackend("reload_ableton")
return
^!+r::
	callBackend("reload_script")
return
^#+l::
	callBackend("tail_logs")
return
#e::
    Run, explorer.exe "D:\ableton projects"
return

; ableton hotkeys
#IfWinActive, Ableton Live
^+z::
    Send ^y  ; redo
return
^#+s::
    Send ^,  ; works best from ahk
    callBackend("save_set_as_template")
return
^!+l::
	callBackend("tail_logs_raw")
return
^!+t::
	callBackend("test")
return
^+a::
	callBackend("arm")
return
^space::
	callBackend("fire_selected_scene")
return
+space::
	callBackend("fire_scene_to_position")
return
^NumPad0::
	callBackend("fire_scene_to_position", "-1")
return
FireSceneToPosition:
    barLength:=SubStr(A_ThisHotkey,"^NumPad") - 1
	callBackend("fire_scene_to_position", barLength)
Return
^Enter::
	callBackend("go_to_group_track")
return
^!+r::
	callBackend("record_unlimited")
return
^Left::
	callBackend("scroll_scene_position", "prev")
return
^Right::
	callBackend("scroll_scene_position", "next")
return
^+Left::
	callBackend("scroll_scene_position_fine", "prev")
return
^+Right::
	callBackend("scroll_scene_position_fine", "next")
return
+Left::
	callBackend("scroll_scene_tracks", "prev")
return
+Right::
	callBackend("scroll_scene_tracks", "next")
return
^Up::
	callBackend("scroll_scenes", "next")
return
^Down::
	callBackend("scroll_scenes", "prev")
return
^!Up::
	callBackend("scroll_track_volume", "next")
return
^!Down::
	callBackend("scroll_track_volume", "prev")
return
^+i::
	callBackend("show_instrument")
return
^q::
	callBackend("show_automation", "next")
return
^+q::
	callBackend("show_automation", "prev")
return
^e::
	callBackend("toggle_clip_notes")
return
^+e::
	callBackend("edit_automation_value")
return
^l::
	callBackend("toggle_scene_loop")
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
~^+r::
	callBackend("check_audio_export_valid")
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

#IfWinActive
