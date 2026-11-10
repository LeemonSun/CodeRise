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
    & $pythonExe scripts\check_course.py --solutions
    if ($LASTEXITCODE -ne 0) { throw "Проверка учебных материалов не пройдена." }
    & $pythonExe scripts\ui_visual_check.py
    if ($LASTEXITCODE -ne 0) { throw "Проверка интерфейса не пройдена." }
}
New-Item -ItemType Directory -Force -Path build | Out-Null
& $pythonExe scripts\make_icon.py
if ($LASTEXITCODE -ne 0) { throw "Не удалось создать значок." }
$pyinstallerArgs = @(
    "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
    "--windowed", "--name", "CodeRise", "--icon", "build\coderise.ico",
    "--add-data", "coderise\data:coderise\data",
    "--distpath", "dist", "--workpath", "build\pyinstaller", "main.py"
)
& $pythonExe @pyinstallerArgs
if ($LASTEXITCODE -ne 0) { throw "Ошибка сборки приложения." }
# Ученический код выполняет отдельный python.exe. В отличие от CodeRise.exe,
# это настоящий интерпретатор, поэтому собранная программа не требует Python на ПК.
$runtimePath = Join-Path $root "dist\CodeRise\runtime"
New-Item -ItemType Directory -Path $runtimePath -Force | Out-Null
$runtimeVersion = & $pythonExe -c "import platform; print(platform.python_version())"
$architecture = & $pythonExe -c "import struct; print(struct.calcsize('P') * 8)"
if ($architecture.Trim() -ne "64") {
    throw "Для Windows-сборки нужен 64-битный Python."
}
$zipPath = Join-Path $root "build\python-embed.zip"
$downloadVersions = @($runtimeVersion, "3.13.5") | Select-Object -Unique
$downloaded = $false
foreach ($candidate in $downloadVersions) {
    $url = "https://www.python.org/ftp/python/$candidate/python-$candidate-embed-amd64.zip"
    try {
        Write-Host "Скачиваю встроенный Python $candidate с python.org..."
        Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
        $downloaded = $true
        break
    } catch {
        Write-Warning "Нет готового embedded-пакета Python $candidate."
    }
}
if (-not $downloaded) {
    throw "Не удалось скачать встроенный Python. Без него установщик работать не будет."
}
Expand-Archive -LiteralPath $zipPath -DestinationPath $runtimePath -Force
if (-not (Test-Path (Join-Path $runtimePath "python.exe"))) {
    throw "Внутри скачанного пакета нет python.exe."
}
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
