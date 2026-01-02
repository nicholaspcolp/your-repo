$base = 'C:\JARVISBRAINSURGERY\trash'
if (!(Test-Path $base)) { Write-Output "MISSING"; exit }
$sum = Get-ChildItem -LiteralPath $base -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
Write-Output "TOTAL_BYTES,$($sum.Sum)"
Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $s = Get-ChildItem -LiteralPath $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
    Write-Output "SUB,$($_.Name),$($s.Sum)"
}
# compute size of GOV/TRASH/duplicates
$dup = Join-Path (Get-Location) 'GOV\TRASH\duplicates'
if (Test-Path $dup) {
    $s2 = Get-ChildItem -LiteralPath $dup -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
    Write-Output "DUPLICATES_BYTES,$($s2.Sum)"
} else { Write-Output "DUPLICATES_MISSING" }
