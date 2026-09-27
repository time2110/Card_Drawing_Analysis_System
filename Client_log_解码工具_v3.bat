@echo off
setlocal

set "BASE=%~dp0"

if "%~1"=="" (
    if exist "%BASE%Client.log" (
        set "SRC=%BASE%Client.log"
    ) else if exist "C:\software\Wuthering Waves\Wuthering Waves Game\Client\Saved\Logs\Client.log" (
        set "SRC=C:\software\Wuthering Waves\Wuthering Waves Game\Client\Saved\Logs\Client.log"
    ) else (
        set "SRC=%BASE%Client.log"
    )
) else (
    set "SRC=%~1"
)

if not exist "%SRC%" (
    echo ERROR: Client.log was not found.
    echo Expected: "%SRC%"
    pause
    exit /b 1
)

set "TARGET=%BASE%Client.log"

if /I not "%SRC%"=="%TARGET%" (
    echo Copying Client.log to local workspace...
    copy /Y "%SRC%" "%TARGET%" >nul
    if errorlevel 1 (
        echo ERROR: Failed to copy Client.log.
        pause
        exit /b 1
    )
)

set "SRC=%TARGET%"
set "OUT=%BASE%Client_decoded.log"

echo.
echo Source: "%SRC%"
echo Output: "%OUT%"
echo.
echo Decoding...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$src=$env:SRC; $out=$env:OUT; $data=[IO.File]::ReadAllBytes($src); if($data.Length -lt 3){throw 'File is too small.'}; $result=New-Object byte[] ($data.Length-3); for($i=3;$i -lt $data.Length;$i++){ $b=$data[$i]; if(($b -band 1) -eq 1){$result[$i-3]=$b -bxor 0xA5}else{$result[$i-3]=$b -bxor 0xEF} }; [IO.File]::WriteAllBytes($out,$result); [Text.Encoding]::UTF8.GetString($result) | Out-Null; Write-Host 'SUCCESS: UTF-8 validation passed.'; Write-Host ('Output size: ' + $result.Length + ' bytes')"

if errorlevel 1 (
    echo.
    echo ERROR: Decode failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Latest aki-gm-resources URL
echo ========================================

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=$env:OUT; $lines=[IO.File]::ReadAllLines($p,[Text.Encoding]::UTF8); $url=$null; for($i=$lines.Length-1;$i -ge 0;$i--){ if($lines[$i] -match 'https?://[^\s\x22\x27\x3c\x3e]*aki-gm-resources[^\s\x22\x27\x3c\x3e]*'){ $url=$Matches[0]; break } }; if($url){ Write-Host $url; Set-Clipboard -Value $url; Write-Host '(URL has been copied to clipboard)' } else { Write-Host 'No URL containing aki-gm-resources was found.' }"

echo.
echo Done.
echo File: "%OUT%"
echo.
pause
endlocal
