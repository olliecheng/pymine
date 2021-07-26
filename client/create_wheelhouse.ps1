Add-Type -assembly "system.io.compression.filesystem"
[System.Environment]::CurrentDirectory = (Get-Location)

poetry run pip wheel --wheel-dir=wheelhouse -r requirements.txt pymine
Try {
    Remove-Item "dist.zip" -ErrorAction Stop
} Catch {

}
[io.compression.zipfile]::CreateFromDirectory("wheelhouse", "dist.zip") 
