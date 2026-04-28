# Detailed CORS and error investigation
$baseUrl = "https://smart-scheduler-0q2w.onrender.com"

# Test CORS with Origin header (simulating GitHub Pages origin)
Write-Host "=== CORS Preflight Test (Origin: github.io) ==="
try {
    $req = [System.Net.WebRequest]::Create("$baseUrl/api/health")
    $req.Method = "OPTIONS"
    $req.Headers.Add("Origin", "https://nagato-yuki.github.io")
    $req.Headers.Add("Access-Control-Request-Method", "GET")
    $req.Headers.Add("Access-Control-Request-Headers", "Content-Type")
    $req.Timeout = 30000
    
    $resp = $req.GetResponse()
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host "Access-Control-Allow-Origin: $($resp.Headers['Access-Control-Allow-Origin'])"
    Write-Host "Access-Control-Allow-Methods: $($resp.Headers['Access-Control-Allow-Methods'])"
    Write-Host "Access-Control-Allow-Headers: $($resp.Headers['Access-Control-Allow-Headers'])"
} catch {
    Write-Host "Error: $_"
}

# Test schedule/results with details
Write-Host ""
Write-Host "=== Schedule Results Error Details ==="
try {
    $resp = Invoke-WebRequest -Uri "$baseUrl/api/schedule/results" -Method GET -UseBasicParsing -TimeoutSec 30
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host "Body: $($resp.Content)"
} catch {
    $resp = $_.Exception.Response
    Write-Host "HTTP Status: $($resp.StatusCode)"
    
    # Read error body
    $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
    $errorBody = $reader.ReadToEnd()
    $reader.Close()
    Write-Host "Error Body: $errorBody"
}

# Test if schedule endpoints exist
Write-Host ""
Write-Host "=== All Schedule Endpoints ==="
$scheduleEndpoints = @("/api/schedule/results", "/api/schedule/run", "/api/schedule/weekly", "/api/schedule/statistics")
foreach ($ep in $scheduleEndpoints) {
    try {
        $resp = Invoke-WebRequest -Uri "$baseUrl$ep" -Method GET -UseBasicParsing -TimeoutSec 30
        Write-Host "$ep => $($resp.StatusCode)"
    } catch {
        $resp = $_.Exception.Response
        Write-Host "$ep => $($resp.StatusCode)"
    }
}
