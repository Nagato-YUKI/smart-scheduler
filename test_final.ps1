# Final comprehensive test for API connectivity between frontend and backend
Write-Host "=== CORS Test: Frontend domain -> Backend API ==="

# Simulate what the browser would do: fronted calls backend API
# Since frontend is on GitHub Pages, it needs VITE_API_BASE_URL set
# Without that env var, it would use relative /api which won't work on github.io

# Test the actual backend API endpoints with full URLs
$baseUrl = "https://smart-scheduler-0q2w.onrender.com/api"
$endpoints = @(
    @{Name="Health"; Path="/health"},
    @{Name="Rooms"; Path="/rooms"},
    @{Name="Teachers"; Path="/teachers"},
    @{Name="Classes"; Path="/classes"},
    @{Name="Courses"; Path="/courses"},
    @{Name="Holidays"; Path="/holidays"},
    @{Name="Schedule Results"; Path="/schedule/results"}
)

foreach ($ep in $endpoints) {
    try {
        $url = "$baseUrl$($ep.Path)"
        $resp = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 30
        $contentPreview = $resp.Content.Substring(0, [Math]::Min(100, $resp.Content.Length))
        Write-Host "[$($ep.Name)] Status: $($resp.StatusCode) - $contentPreview"
    } catch {
        Write-Host "[$($ep.Name)] ERROR: $_"
    }
}

# Test CORS headers
Write-Host ""
Write-Host "=== CORS Headers Check ==="
try {
    $resp = Invoke-WebRequest -Uri "https://smart-scheduler-0q2w.onrender.com/api/health" -Method OPTIONS -UseBasicParsing -TimeoutSec 30
    Write-Host "OPTIONS response status: $($resp.StatusCode)"
    Write-Host "Headers: $($resp.Headers | Out-String)"
} catch {
    Write-Host "OPTIONS request failed: $_"
}
