; AI Document Analyzer testing installer
; This prototype does not represent final Milestone 3 acceptance.

Unicode True

!define APPNAME "AI Document Analyzer"
!define DISPLAYNAME "AI Document Analyzer (Testing Build)"
!define PUBLISHER "SSMA"
!define WEBSITE "https://ssma.sa"
!define DISPLAYVERSION "1.0.0-test"
!define PRODUCTVERSION "1.0.0.0"
!define EXENAME "AI Document Analyzer.exe"
!define UNINSTALLKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
!define INSTALLMARKER ".ai-document-analyzer-prototype"

Name "${DISPLAYNAME}"
OutFile "AI_Document_Analyzer_Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\${APPNAME}"
RequestExecutionLevel user
SetCompressor /SOLID lzma
ShowInstDetails show
ShowUninstDetails show
BrandingText "${DISPLAYNAME}"
Icon "assets\logo.ico"
UninstallIcon "assets\logo.ico"

VIProductVersion "${PRODUCTVERSION}"
VIAddVersionKey /LANG=1033 "ProductName" "${APPNAME}"
VIAddVersionKey /LANG=1033 "ProductVersion" "${DISPLAYVERSION}"
VIAddVersionKey /LANG=1033 "FileVersion" "${DISPLAYVERSION}"
VIAddVersionKey /LANG=1033 "FileDescription" "${DISPLAYNAME} Installer"
VIAddVersionKey /LANG=1033 "CompanyName" "${PUBLISHER}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Copyright ${PUBLISHER}"
VIAddVersionKey /LANG=1033 "Comments" "Testing build only; not a final Milestone 3 release."

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Install ${DISPLAYNAME}"
!define MUI_WELCOMEPAGE_TEXT "This setup installs a testing build for size and installation verification.$\r$\n$\r$\nIt is not a final Milestone 3 release."
!define MUI_FINISHPAGE_TITLE "${DISPLAYNAME} installed"
!define MUI_FINISHPAGE_TEXT "The testing build has been installed for the current Windows user."
!define MUI_FINISHPAGE_RUN "$INSTDIR\${EXENAME}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch ${APPNAME}"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Function .onInit
    SetShellVarContext current

    ; Only replace a directory created by this prototype installer.
    IfFileExists "$INSTDIR\${INSTALLMARKER}" owned_install
    IfFileExists "$INSTDIR\*.*" unexpected_install owned_install

unexpected_install:
    MessageBox MB_ICONSTOP|MB_OK "Setup found an existing folder that was not created by this testing installer:$\r$\n$\r$\n$INSTDIR$\r$\n$\r$\nFor safety, no files were changed. Rename or remove that folder and run setup again." /SD IDOK
    Abort

owned_install:
FunctionEnd

Function un.onInit
    SetShellVarContext current
FunctionEnd

Section "!${APPNAME} (required)" SEC_APP
    SectionIn RO

    ; A reinstall replaces the complete prior prototype payload so obsolete
    ; PyInstaller files cannot survive an upgrade.
    IfFileExists "$INSTDIR\${INSTALLMARKER}" 0 payload_clean
    ClearErrors
    RMDir /r "$INSTDIR"
    IfFileExists "$INSTDIR\*.*" 0 payload_clean
        MessageBox MB_ICONSTOP|MB_OK "Could not replace the existing application files. Close ${APPNAME} and run setup again." /SD IDOK
        SetErrorLevel 1
        Abort

payload_clean:
    SetOutPath "$INSTDIR"
    File /r "dist\AI Document Analyzer\*"

    FileOpen $0 "$INSTDIR\${INSTALLMARKER}" w
    FileWrite $0 "${DISPLAYVERSION}$\r$\n"
    FileClose $0

    WriteUninstaller "$INSTDIR\uninstall.exe"

    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${EXENAME}" 0
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

    WriteRegStr HKCU "${UNINSTALLKEY}" "DisplayName" "${DISPLAYNAME}"
    WriteRegStr HKCU "${UNINSTALLKEY}" "DisplayVersion" "${DISPLAYVERSION}"
    WriteRegStr HKCU "${UNINSTALLKEY}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKCU "${UNINSTALLKEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "${UNINSTALLKEY}" "DisplayIcon" "$INSTDIR\${EXENAME},0"
    WriteRegStr HKCU "${UNINSTALLKEY}" "UninstallString" '$\"$INSTDIR\uninstall.exe$\"'
    WriteRegStr HKCU "${UNINSTALLKEY}" "QuietUninstallString" '$\"$INSTDIR\uninstall.exe$\" /S'
    WriteRegStr HKCU "${UNINSTALLKEY}" "HelpLink" "${WEBSITE}"
    WriteRegStr HKCU "${UNINSTALLKEY}" "URLInfoAbout" "${WEBSITE}"
    WriteRegDWORD HKCU "${UNINSTALLKEY}" "VersionMajor" 1
    WriteRegDWORD HKCU "${UNINSTALLKEY}" "VersionMinor" 0
    WriteRegDWORD HKCU "${UNINSTALLKEY}" "NoModify" 1
    WriteRegDWORD HKCU "${UNINSTALLKEY}" "NoRepair" 1

    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    WriteRegDWORD HKCU "${UNINSTALLKEY}" "EstimatedSize" $0
SectionEnd

Section /o "Desktop shortcut" SEC_DESKTOP
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXENAME}" "" "$INSTDIR\${EXENAME}" 0
SectionEnd

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_APP} "Install ${DISPLAYNAME} for the current Windows user."
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} "Create an optional shortcut on the current user's desktop."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
    SetShellVarContext current

    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    DeleteRegKey HKCU "${UNINSTALLKEY}"

    ; User data under %APPDATA%\AI Document Analyzer is intentionally retained.
    RMDir /r "$INSTDIR"
SectionEnd
