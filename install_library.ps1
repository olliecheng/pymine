# Download & install latest denosawr/pymine release from github
# Run using iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/denosawr/pymine/master/install_library.ps1'))

$originalfg = $host.ui.RawUI.ForegroundColor
$host.ui.RawUI.ForegroundColor = "Cyan"

$repo = "denosawr/pymine"

$releases = "https://api.github.com/repos/$repo/releases"

Write-Host Determining latest release -ForegroundColor Cyan
$requestData = (Invoke-WebRequest $releases | ConvertFrom-Json)[0]
$tag = $requestData.tag_name

ForEach($item in $requestData.assets) {
    Write-Host $item.name
    if ($item.name -match "\.whl$") {
        $file = $item.name
        $download = "https://github.com/$repo/releases/download/$tag/$file"

        break
    }
}

Write-Host "Found file $file at $download" -ForegroundColor DarkGray

Write-Host Downloading latest library wheel
Invoke-WebRequest $download -Out $file
Write-Host Downloaded library wheel
Write-Host Installing library wheel

$host.ui.RawUI.ForegroundColor = "DarkGray"

Invoke-Expression $($env:APPDATA + 
    "\..\local\Programs\Thonny\python.exe -m pip install --trusted-host pypi.org --disable-pip-version-check --no-warn-script-location --trusted-host files.pythonhosted.org $file"
)

$host.ui.RawUI.ForegroundColor = "Cyan"
Write-Host Installed dependencies
Write-Host Cleaning up temporary files

Remove-Item $file

Write-Host "All done! Try `import pymine` in a Thonny console window." -ForegroundColor Yellow

$host.ui.RawUI.ForegroundColor = $originalfg
#Remove-Item $dir -Recurse -Force
#>