Add-Type -AssemblyName PresentationCore, PresentationFramework

$Result = [System.Windows.MessageBox]::Show("Start Auto IG?", "Scheduled Auto IG", "OKCancel", "Question")

if ($Result -eq "OK") {
    # Invoke-Command -FilePath "$(Resolve-Path .\run.ps1)"
    Set-Location -Path $PSScriptRoot
    & .\run.ps1
}
else {
    "Cancelled"   
}

Read-Host -Prompt “Press Enter to exit”