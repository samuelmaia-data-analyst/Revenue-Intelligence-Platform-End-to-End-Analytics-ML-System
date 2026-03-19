param(
    [string]$Url = "http://127.0.0.1:8510",
    [string]$OutputPath = "docs/assets/dashboard/overview.png",
    [int]$DebugPort = 9222,
    [int]$Width = 1600,
    [int]$Height = 2200,
    [int]$TimeoutSeconds = 45
)

$ErrorActionPreference = "Stop"

function Get-BrowserPath {
    $candidates = @(
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }
    throw "No supported browser binary found."
}

function Invoke-CdpCommand {
    param(
        [System.Net.WebSockets.ClientWebSocket]$Socket,
        [int]$Id,
        [string]$Method,
        [hashtable]$Params = @{}
    )

    $payload = @{
        id = $Id
        method = $Method
        params = $Params
    } | ConvertTo-Json -Compress -Depth 10

    $buffer = [System.Text.Encoding]::UTF8.GetBytes($payload)
    $segment = [ArraySegment[byte]]::new($buffer)
    $Socket.SendAsync(
        $segment,
        [System.Net.WebSockets.WebSocketMessageType]::Text,
        $true,
        [Threading.CancellationToken]::None
    ).GetAwaiter().GetResult()

    $receiveBuffer = New-Object byte[] 65536
    while ($true) {
        $segment = [ArraySegment[byte]]::new($receiveBuffer)
        $result = $Socket.ReceiveAsync(
            $segment,
            [Threading.CancellationToken]::None
        ).GetAwaiter().GetResult()
        if ($result.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) {
            throw "Chrome DevTools connection closed unexpectedly."
        }
        $message = [System.Text.Encoding]::UTF8.GetString($receiveBuffer, 0, $result.Count)
        $response = $message | ConvertFrom-Json
        if ($null -ne $response.id -and [int]$response.id -eq $Id) {
            return $response
        }
    }
}

$browserPath = Get-BrowserPath
$outputFullPath = Join-Path (Get-Location) $OutputPath
$outputDirectory = Split-Path -Parent $outputFullPath
if (-not (Test-Path $outputDirectory)) {
    New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}

$browser = Start-Process -FilePath $browserPath -ArgumentList @(
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--remote-debugging-port=$DebugPort",
    "about:blank"
) -PassThru

try {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $target = $null
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        try {
            $targets = Invoke-RestMethod -Uri "http://127.0.0.1:$DebugPort/json" -TimeoutSec 2
            if ($targets) {
                $target = $targets | Select-Object -First 1
                break
            }
        }
        catch {
        }
    }

    if ($null -eq $target) {
        throw "Chrome DevTools target was not available."
    }

    $socket = [System.Net.WebSockets.ClientWebSocket]::new()
    $socket.ConnectAsync(
        [Uri]$target.webSocketDebuggerUrl,
        [Threading.CancellationToken]::None
    ).GetAwaiter().GetResult()

    try {
        Invoke-CdpCommand -Socket $socket -Id 1 -Method "Page.enable" | Out-Null
        Invoke-CdpCommand -Socket $socket -Id 2 -Method "Runtime.enable" | Out-Null
        Invoke-CdpCommand -Socket $socket -Id 3 -Method "Emulation.setDeviceMetricsOverride" -Params @{
            width = $Width
            height = $Height
            deviceScaleFactor = 1
            mobile = $false
        } | Out-Null
        Invoke-CdpCommand -Socket $socket -Id 4 -Method "Page.navigate" -Params @{
            url = $Url
        } | Out-Null

        $renderDeadline = (Get-Date).AddSeconds($TimeoutSeconds)
        $isReady = $false
        while ((Get-Date) -lt $renderDeadline) {
            Start-Sleep -Seconds 1
            $readyResponse = Invoke-CdpCommand -Socket $socket -Id 5 -Method "Runtime.evaluate" -Params @{
                expression = @"
(() => {
  const bodyText = document.body ? document.body.innerText : "";
  const hasTitle = bodyText.includes("Revenue Intelligence Data Platform")
    || bodyText.includes("Revenue Command Center")
    || bodyText.includes("Executive Overview");
  const appContainer = document.querySelector('[data-testid="stAppViewContainer"]');
  return Boolean(hasTitle && appContainer);
})()
"@
                returnByValue = $true
            }
            if ($readyResponse.result.result.value -eq $true) {
                $isReady = $true
                break
            }
        }

        if (-not $isReady) {
            throw "Dashboard content did not hydrate before timeout."
        }

        Start-Sleep -Seconds 2
        $screenshot = Invoke-CdpCommand -Socket $socket -Id 6 -Method "Page.captureScreenshot" -Params @{
            format = "png"
            captureBeyondViewport = $true
        }
        [System.IO.File]::WriteAllBytes(
            $outputFullPath,
            [Convert]::FromBase64String($screenshot.result.data)
        )
        Write-Output $outputFullPath
    }
    finally {
        if ($socket.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
            $socket.CloseAsync(
                [System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure,
                "done",
                [Threading.CancellationToken]::None
            ).GetAwaiter().GetResult()
        }
        $socket.Dispose()
    }
}
finally {
    if (-not $browser.HasExited) {
        Stop-Process -Id $browser.Id -Force
    }
}
