# Проверка, сборка приложения и установщика. Только Windows.
# Запуск: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_windows.ps1
param(
    [switch]$SkipTests,
    [switch]$NoInstaller
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if ($env:OS -ne "Windows_NT") { throw "Сборка предназначена для Windows." }
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -m venv .venv
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -m venv .venv
} else {
    throw "Установи Python 3.11 или новее."
}
if ($LASTEXITCODE -ne 0) { throw "Ошибка создания виртуального окружения." }
$pythonExe = Join-Path $root ".venv\Scripts\python.exe"
& $pythonExe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Ошибка обновления pip." }
& $pythonExe -m pip install -r requirements.txt "pyinstaller>=6.11,<7" "Pillow>=10,<13"
if ($LASTEXITCODE -ne 0) { throw "Не удалось установить зависимости." }
if (-not $SkipTests) {
    & $pythonExe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Тесты не пройдены, сборка остановлена." }
}
New-Item -ItemType Directory -Force -Path build | Out-Null
& $pythonExe scripts\make_icon.py
if ($LASTEXITCODE -ne 0) { throw "Не удалось создать значок." }
$pyinstallerArgs = @(
    "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
    "--windowed", "--name", "CodeRise", "--icon", "build\coderise.ico",
    "--add-data", "coderise\data;coderise\data",
    "--distpath", "dist", "--workpath", "build\pyinstaller", "main.py"
)
& $pythonExe @pyinstallerArgs
if ($LASTEXITCODE -ne 0) { throw "Ошибка сборки приложения." }
Write-Host "Приложение: dist\CodeRise\CodeRise.exe" -ForegroundColor Green
if (-not $NoInstaller) {
    $iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    $compiler = $null
    if ($iscc) { $compiler = $iscc.Source }
    if (-not $compiler) {
        $programFilesX86 = [Environment]::GetFolderPath("ProgramFilesX86")
        $programFiles = [Environment]::GetFolderPath("ProgramFiles")
        $candidates = @(
            (Join-Path $programFilesX86 "Inno Setup 6\ISCC.exe"),
            (Join-Path $programFiles "Inno Setup 6\ISCC.exe"),
            (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
        )
        $compiler = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    }
    if ($compiler) {
        & $compiler "installer\CodeRise.iss"
        if ($LASTEXITCODE -ne 0) { throw "Ошибка сборки установщика." }
        Write-Host "Установщик: release\CodeRise-Setup-0.3.0.exe" -ForegroundColor Green
    } else {
        Write-Warning "Inno Setup 6 не найден. EXE собран, для установщика нужен Inno Setup 6."
    }
}
