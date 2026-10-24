param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8786,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$Url = "http://${HostAddress}:${Port}/"
Write-Host "Starting FAULTLINE joint-failure laboratory at $Url" -ForegroundColor Cyan

if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($TargetUrl)
        Start-Sleep -Milliseconds 900
        Start-Process $TargetUrl
    } -ArgumentList $Url | Out-Null
}

python -m faultline serve --host $HostAddress --port $Port
