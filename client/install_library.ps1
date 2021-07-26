# Download & install latest denosawr/pymine release from github

#<#
$repo = "denosawr/pymine"
$file = "pymine_client-0.1.0-py3-none-any.whl"

$releases = "https://api.github.com/repos/$repo/releases"

Write-Host Determining latest release
$tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name

$download = "https://github.com/$repo/releases/download/$tag/$file"

Write-Host Dowloading latest library wheel
Invoke-WebRequest $download -Out $file
##>

Invoke-Expression $($env:APPDATA + 
    "\..\local\Programs\Thonny\python.exe -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org $file"
)

Remove-Item $file
#Remove-Item $dir -Recurse -Force