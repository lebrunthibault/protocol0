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
#IfWinActive, ahk_exe Ableton Live 11 Suite.exe
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
	callBackend("fire_scene_to_last_position")
return
^NumPad0::
	callBackend("fire_scene_to_position?bar_length=-1")
return
FireSceneToPosition:
    barLength:=SubStr(A_ThisHotkey,"^NumPad") - 1
	callBackend("fire_scene_to_position?bar_length="barLength)
Return
^Enter::
	callBackend("go_to_group_track")
return
^!+r::
	callBackend("record_unlimited")
return
^Left::
	callBackend("scroll_scene_position?direction=prev")
return
^Right::
	callBackend("scroll_scene_position?direction=next")
return
^+Left::
	callBackend("scroll_scene_position_fine?direction=prev")
return
^+Right::
	callBackend("scroll_scene_position_fine?direction=next")
return
+Left::
	callBackend("scroll_scene_tracks?direction=prev")
return
+Right::
	callBackend("scroll_scene_tracks?direction=next")
return
^Up::
	callBackend("scroll_scenes?direction=next")
return
^Down::
	callBackend("scroll_scenes?direction=prev")
return
^!Up::
	callBackend("scroll_track_volume?direction=next")
return
^!Down::
	callBackend("scroll_track_volume?direction=prev")
return
^+i::
	callBackend("show_instrument")
return
^q::
	callBackend("show_automation?direction=next")
return
^+q::
	callBackend("show_automation?direction=prev")
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
^+#r::
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

; minitaur editor
#IfWinActive ahk_class JUCE_18999b05416
^space::
	callBackend("fire_selected_scene")
return
#IfWinActive

; splice window
#IfWinActive ahk_exe Splice.exe
^space::
	callBackend("fire_selected_scene")
return
#IfWinActive
