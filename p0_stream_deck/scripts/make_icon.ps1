$path = $args[0]

if (-Not $path -or -Not (Test-Path $path)) {
    Write-Error("$path is not a valid path")
    exit
}

$icon_dir = "com.thibault.p0.sdPlugin/icon"

$base_name = [System.IO.Path]::GetFileNameWithoutExtension($path)

New-Item -ItemType Directory -Force -Path "$icon_dir/$base_name"

$action_path =  "$icon_dir/$base_name/action.png"
$action_pathx2 =  "$icon_dir/$base_name/action@2x.png"
$state_path =  "$icon_dir/$base_name/state.png"
$state_pathx2 =  "$icon_dir/$base_name/state@2x.png"

Copy-Item $path $action_path
Copy-Item $path $action_pathx2
Copy-Item $path $state_path
Copy-Item $path $state_pathx2

magick mogrify -resize 20x20 -monochrome $action_path
magick mogrify -resize 40x40 -monochrome $action_pathx2
magick mogrify -resize 72x72 $state_path
magick mogrify -resize 144x144 $state_pathx2

Remove-Item $path

Write-Host "icons generated"