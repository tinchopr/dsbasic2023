Attribute VB_Name = "python"
Option Explicit
Dim ws As Worksheet
Dim ClearRange As Range
Const Dropbox_Folder As String = "Dropbox (Scalar Analytics)\"
Public user As String
Sub DropBoxPath()

    'Get user Name
    user = Environ$("Username")
        
        ''''''''''''''''''''''''''''''''''''Get dropbox name''''''''''''''''''''''''''''''''
    
    ChDir "C:\Users\" & user

    If Dir("Dropbox*", vbDirectory) <> "" Then
        user = "C:\Users\" & user & "\" & Dir("Dropbox*", vbDirectory)
    End If


End Sub

Function RunInConsole(pyScriptPath As String)    'Runs Executable Files in the console and python files in the console

    Dim objShell As Object
    Set objShell = VBA.CreateObject("Wscript.Shell")
    Dim waitOnReturn As Boolean: waitOnReturn = True
    Dim windowStyle As Integer: windowStyle = 1
    Dim fileExtension As String
    Dim PythonExePath As String

    Call DropBoxPath
    
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    'Python Exce Path
    PythonExePath = "\Valuation\Templates\Model Sheets (add-ins)\TestEnv\python.exe"
    PythonExePath = user & PythonExePath
    
    
    'Check if it is a python file or exe file and run accordinly
    fileExtension = GetFileExtension(pyScriptPath)
    
    Set objShell = VBA.CreateObject("Wscript.Shell")
    
    If fileExtension = "exe" Then
        objShell.Run """" & pyScriptPath & """", windowStyle, waitOnReturn

    ElseIf fileExtension = "py" Then
        objShell.Run """" & PythonExePath & """" & " " & """" & pyScriptPath & """", windowStyle, waitOnReturn
    End If
    
End Function


Function GetFileExtension(filePath As String) As String
    Dim lastDot As Integer
    lastDot = InStrRev(filePath, ".")
    If lastDot > 0 Then
        GetFileExtension = Right(filePath, Len(filePath) - lastDot)
    Else
        GetFileExtension = "No extension found"
    End If
End Function

Sub ExemptRates()

    Dim PythonScriptPath As String
    Application.ScreenUpdating = False
    
    PythonScriptPath = "\Valuation\Templates\Model Sheets (add-ins)\Python Scripts\ExemptRates.py"
    
    Call DropBoxPath
    
    PythonScriptPath = user & PythonScriptPath
    
    RunInConsole (PythonScriptPath)
     
    Application.ScreenUpdating = True
    
End Sub

