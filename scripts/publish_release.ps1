# Publish the locally built Windows installer as one GitHub release asset.
# Does not use GitHub Actions. Needs authenticated GitHub CLI (gh).
# Run only after building and checking release\CodeRise-Setup-0.3.0.exe.
param([string]$Version = "0.3.0")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$tag = "v$Version"
$setup = Join-Path $root "release\CodeRise-Setup-$Version.exe"
$runtime = Join-Path $root "dist\CodeRise\runtime\python.exe"
$app = Join-Path $root "dist\CodeRise\CodeRise.exe"

if (-not (Test-Path -LiteralPath $setup)) {
    throw "Нет установщика $setup. Сначала запусти build_windows.cmd."
}
if (-not (Test-Path -LiteralPath $runtime) -or -not (Test-Path -LiteralPath $app)) {
    throw "Не найдена собранная программа со встроенным Python runtime."
}
$stream = [System.IO.File]::OpenRead($setup)
try {
    $first = $stream.ReadByte()
    $second = $stream.ReadByte()
} finally {
    $stream.Dispose()
}
if ($first -ne 77 -or $second -ne 90) {
    throw "Установщик не похож на Windows EXE (нет заголовка MZ)."
}
if ((Get-Item $setup).LastWriteTime -lt (Get-Item $app).LastWriteTime) {
    throw "Установщик старше приложения. Пересобери релиз."
}
$hash = (Get-FileHash -LiteralPath $setup -Algorithm SHA256).Hash
Write-Host "Файл: $setup"
Write-Host "SHA256: $hash"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "Не найден GitHub CLI (gh). Установи его: https://cli.github.com/"
}
& gh auth status
if ($LASTEXITCODE -ne 0) { throw "Сначала выполни gh auth login." }

$existing = & gh release view $tag --repo "LeemonSun/CodeRise" 2>$null
if ($LASTEXITCODE -eq 0) {
    throw "Релиз $tag уже существует. Новая версия должна иметь новый номер."
}

$notes = @"
Windows-установщик CodeRise $Version.
140 заданий G–SSS, русский интерфейс, справочник и локальное сохранение прогресса.

Скачай CodeRise-Setup-$Version.exe и запусти установку.
Python отдельно устанавливать не нужно.

SHA256: $hash

Важно: учебный код запускается локально, не вставляй в тренажёр недоверенные скрипты.
"@
& gh release create $tag $setup --repo "LeemonSun/CodeRise" --title "CodeRise $Version" --notes $notes --latest
if ($LASTEXITCODE -ne 0) { throw "Не удалось создать GitHub Release." }

Write-Host "Опубликовано: https://github.com/LeemonSun/CodeRise/releases/tag/$tag" -ForegroundColor Green
