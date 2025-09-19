; AI Document Analyzer Installer Script
!define APPNAME "AI Document Analyzer"
!define COMPANYNAME "Your Company"
!define DESCRIPTION "AI-powered document analysis tool"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://your-website.com"
!define UPDATEURL "https://your-website.com"
!define ABOUTURL "https://your-website.com"
!define INSTALLSIZE 50000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\${APPNAME}"
Name "${APPNAME}"
outFile "AI_Document_Analyzer_Setup.exe"

!include LogicLib.nsh

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    file /r "dist\AI Document Analyzer\*"
    
    writeUninstaller "$INSTDIR\uninstall.exe"
    
    createDirectory "$SMPROGRAMS\${APPNAME}"
    createShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\AI Document Analyzer.exe" "" "$INSTDIR\assets\logo.ico"
    createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe"
    
    createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\AI Document Analyzer.exe" "" "$INSTDIR\assets\logo.ico"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\assets\logo.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
    delete "$INSTDIR\uninstall.exe"
    rmDir /r "$INSTDIR"
    
    delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    rmDir "$SMPROGRAMS\${APPNAME}"
    
    delete "$DESKTOP\${APPNAME}.lnk"
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
sectionEnd
