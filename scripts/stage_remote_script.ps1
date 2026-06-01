# Prépare le dossier Protocol_0 prêt à copier dans MIDI Remote Scripts.
#
# Sortie : build/stage/Protocol_0/  (consommé par installer/protocol0.iss)
# Copie pure : le remote script est stdlib-only, donc aucun poetry install / vendoring.
#
#   build/stage/Protocol_0/
#     ├─ __init__.py        (= __init__.prod.py, loader minimal)
#     └─ protocol0/         (le paquet source, sans __pycache__ ni tests)

$ErrorActionPreference = "Stop"

$repoRoot  = (Resolve-Path "$PSScriptRoot\..").Path
$scriptSrc = Join-Path $repoRoot "src\script\protocol0"
$prodInit  = Join-Path $repoRoot "src\script\script_templates\Protocol_0\__init__.prod.py"
$stageRoot = Join-Path $repoRoot "build\stage\Protocol_0"

if (-not (Test-Path $scriptSrc)) { throw "Source package not found: $scriptSrc" }
if (-not (Test-Path $prodInit))  { throw "Prod loader not found: $prodInit" }

# Repartir d'un dossier propre.
if (Test-Path $stageRoot) { Remove-Item -Recurse -Force $stageRoot }
New-Item -ItemType Directory -Force -Path $stageRoot | Out-Null

# Copier le paquet protocol0/ puis purger ce qui ne doit pas être distribué.
$stagePkg = Join-Path $stageRoot "protocol0"
Copy-Item -Recurse -Force $scriptSrc $stagePkg

Get-ChildItem -Path $stagePkg -Recurse -Force -Directory |
    Where-Object { $_.Name -eq "__pycache__" -or $_.Name -eq "tests" } |
    Remove-Item -Recurse -Force

# Déposer le loader prod comme __init__.py.
Copy-Item -Force $prodInit (Join-Path $stageRoot "__init__.py")

Write-Host "OK -> $stageRoot"
