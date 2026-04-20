@echo off
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ==================================================
    echo ✅ Administrative permissions confirmed.
    echo ==================================================
    echo.
    echo Opening Port 5000 in Windows Firewall...
    
    netsh advfirewall firewall delete rule name="FaceWave App" >nul 2>&1
    netsh advfirewall firewall add rule name="FaceWave App" dir=in action=allow protocol=TCP localport=5000 profile=any
    
    netsh advfirewall firewall delete rule name="FaceWave App UDP" >nul 2>&1
    netsh advfirewall firewall add rule name="FaceWave App UDP" dir=in action=allow protocol=UDP localport=5000 profile=any
    
    echo.
    echo ✅ Firewall rules updated for ALL network profiles (Public/Private).
    echo 📱 You should now be able to access the app from your mobile device.
    echo.
    pause
) else (
    echo ==================================================
    echo ⚠️  Requesting administrative privileges...
    echo ==================================================
    echo Please click "Yes" in the popup window to allow this script to run.
    powershell -Command "Start-Process '%~0' -Verb RunAs"
    exit
)
