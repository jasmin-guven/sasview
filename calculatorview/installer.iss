; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=SansViewTool
AppVerName=SansViewTool-0.9.2dev
AppPublisher=University of Tennessee
AppPublisherURL=http://danse.chem.utk.edu/
AppSupportURL=http://danse.chem.utk.edu/
AppUpdatesURL=http://danse.chem.utk.edu/
DefaultDirName={pf}\SansViewTool
DefaultGroupName=DANSE\SansViewTool-0.9.2dev
DisableProgramGroupPage=yes
LicenseFile=license.txt
OutputBaseFilename=setupSansViewTool
Compression=lzma
SolidCompression=yes
PrivilegesRequired=none

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SansViewTool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\SansViewTool"; Filename: "{app}\SansViewTool.exe"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,SansViewTool}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\SansViewTool"; Filename: "{app}\SansViewTool.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\SansViewTool.exe"; Description: "{cm:LaunchProgram,SansViewTool}"; Flags: nowait postinstall skipifsilent

