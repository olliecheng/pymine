Add-Type -assembly "system.io.compression.filesystem"
[System.Environment]::CurrentDirectory = (Get-Location)

(poetry export -f requirements.txt) -replace "^Warning:.*$","" -replace "^--index-url.*$","" > requirements.txt