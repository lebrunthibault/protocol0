executeCliCommand(command, args*)
{
    arg_string := Join(" ", args*)
    Run py cli.py %command% %arg_string%, %A_ScriptDir%\.., hide
}

Join(sep, params*) {
    str := ""
    for index,param in params
        str .= param . sep
    return SubStr(str, 1, -StrLen(sep))
}

callBackend(command, arg:="") {
	url := "http://127.0.0.1:8000/"command
	if (arg != "") {
		url = %url%/%arg%
	}
	oHttp := ComObjCreate("WinHttp.Winhttprequest.5.1")

	try {
        oHttp.open("GET", url)
        oHttp.send()
    } catch e {
;        MsgBox, Error: Could not reach the server. Please check if the server is running.
        return ""  ; Return an empty string or handle the error as needed
    }

    return oHttp.responseText  ; Return the response if the request is successful
}
