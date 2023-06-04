Clear-Host

Get-Process StreamDeck -ErrorAction SilentlyContinue | Stop-Process

$pluginPath = "C:\Users\thiba\AppData\Roaming\Elgato\StreamDeck\Plugins\com.thibault.p0.sdPlugin"

## remove previous plugin
if (Test-Path $pluginPath) {
    Remove-Item $pluginPath -Recurse
}

## we do this to have error logs
$releasePath = "dist/com.thibault.p0.streamDeckPlugin"
if (Test-Path $releasePath) {
    Remove-Item $releasePath
}
DistributionTool.exe -b -i com.thibault.p0.sdPlugin -o dist

Copy-Item "com.thibault.p0.sdPlugin" $pluginPath -Recurse -force

. "C:\Program Files\Elgato\StreamDeck\StreamDeck.exe"
