# Download latest denosawr/pymine release from github

<#
$repo = "denosawr/pymine"
$file = "pymine-client-dist.zip"

$releases = "https://api.github.com/repos/$repo/releases"

Write-Host Determining latest release
$tag = (Invoke-WebRequest $releases | ConvertFrom-Json)[0].tag_name

$download = "https://github.com/$repo/releases/download/$tag/$file"
$name = $file.Split(".")[0]
$zip = "$name-$tag.zip"
$dir = "$name-$tag"

Write-Host Dowloading latest release
Invoke-WebRequest $download -Out $zip

Write-Host Extracting release files
Expand-Archive $zip -Force
##>

$dir = "pymine-client-dist-v0.1b"

cd $dir
Get-ChildItem -Filter *.whl | ForEach {
    Invoke-Expression $($env:APPDATA + 
        "\..\local\Programs\Thonny\python.exe -m pip install --force-reinstall --no-index --no-deps $_"
    )
}
cd ../

#Remove-Item $zip -Force
#Remove-Item $dir -Recurse -Force