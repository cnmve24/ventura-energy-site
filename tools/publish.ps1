<#
  publish.ps1 - build and publish the Ventura Energy site.

  Usage
    .\tools\publish.ps1 -Title "SGIP Has Closed" -Slug sgip-has-closed
    .\tools\publish.ps1 -Title "Draft check" -DryRun

  Order matters: build and commit first, then rebase onto origin, then push.
  Rebasing before committing fails whenever the working tree is dirty.
  Never force pushes. Stops on anything unexpected.
#>
param(
  [Parameter(Mandatory=$true)][string]$Title,
  [string]$Slug = "",
  [switch]$DryRun
)

$ErrorActionPreference = "Continue"
Set-Location (Split-Path -Parent $PSScriptRoot)

function Fail($m) { Write-Host "`nFAILED: $m" -ForegroundColor Red; exit 1 }
function Step($m) { Write-Host "`n== $m" -ForegroundColor Cyan }

if (-not (Test-Path "tools\buildsite.py")) { Fail "not in the site repo (no tools\buildsite.py)" }
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if ($branch -ne "main") { Fail "on branch '$branch', expected 'main'" }

Step "Checking origin"
git fetch origin main 2>&1 | Out-Null
$behind = (git rev-list --count HEAD..origin/main 2>$null)
Write-Host "  commits behind origin/main: $behind"

Step "Building"
$build = python tools\buildsite.py 2>&1
$build | Write-Host
# $build is an ARRAY of output lines. In PowerShell, -match/-notmatch against an
# array returns the filtered elements, not a boolean, so "-notmatch" on an array
# is almost always truthy. Flatten to one string before testing for the summary.
$buildText = ($build | Out-String)
if ($LASTEXITCODE -ne 0)              { Fail "build failed. Nothing was committed." }
if ($buildText -notmatch "built \d+") { Fail "build did not report building any pages. Nothing was committed." }

Step "Changes to publish"
git add -A
$staged = git diff --cached --name-status
if (-not $staged) { Write-Host "Nothing to commit. Was the post written to content\posts\ ?" -ForegroundColor Yellow; exit 0 }
$staged | Write-Host

# Guardrails from ROUTINE.md
$bad = @()
if ($staged -match "^\w+\s+CNAME")     { $bad += "CNAME" }
if ($staged -match "^D\s+assets/img/") { $bad += "a deletion under assets/img/" }
if (($staged -match "assets/site\.css") -and -not ($staged -match "tools/site\.css")) {
  $bad += "assets/site.css but not tools/site.css (edit tools/site.css instead)"
}
if ($bad.Count -gt 0) { Fail ("staged changes touch " + ($bad -join "; ") + ". Check before publishing.") }

if ($DryRun) { Step "Dry run, stopping before commit"; git reset | Out-Null; exit 0 }

Step "Committing"
git commit -m "Post: $Title"
if ($LASTEXITCODE -ne 0) { Fail "commit failed" }

if ([int]$behind -gt 0) {
  Step "Rebasing onto origin/main ($behind commit(s) behind)"
  git pull --rebase
  if ($LASTEXITCODE -ne 0) { Fail "rebase hit a conflict. Resolve it, then run: git rebase --continue; git push. Do not force push." }
  Step "Rebuilding after rebase"
  python tools\buildsite.py 2>&1 | Write-Host
  if ($LASTEXITCODE -ne 0) { Fail "rebuild after rebase failed" }
  git add -A
  if (git diff --cached --name-status) { git commit -m "Rebuild after rebase" }
}

Step "Pushing"
git push
if ($LASTEXITCODE -ne 0) {
  Write-Host "push rejected; rebasing once and retrying" -ForegroundColor Yellow
  git pull --rebase; if ($LASTEXITCODE -ne 0) { Fail "rebase failed. Resolve by hand. Do not force push." }
  git push;          if ($LASTEXITCODE -ne 0) { Fail "push still failing. Resolve by hand. Do not force push." }
}

if ($Slug) {
  Step "Checking the live page"
  $url = "https://ventura.energy/updates/$Slug.html"
  for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 15
    try { $code = (Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 15).StatusCode } catch { $code = 0 }
    Write-Host "  attempt $i : $code"
    if ($code -eq 200) { Write-Host "`nLive: $url" -ForegroundColor Green; exit 0 }
  }
  Write-Host "`nNot live after ~2.5 min. Pages may still be deploying: $url" -ForegroundColor Yellow
} else {
  Write-Host "`nPushed. Pages redeploys in about a minute." -ForegroundColor Green
}
