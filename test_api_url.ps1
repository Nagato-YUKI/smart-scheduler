# Deep API URL check in JS bundle
$jsUrl = "https://nagato-yuki.github.io/smart-scheduler/assets/index-BPBzAIdl.js"
$jsResponse = Invoke-WebRequest -Uri $jsUrl -UseBasicParsing
$content = $jsResponse.Content

# Check for any URL pattern that could be API base
Write-Host "=== Checking for API Base URL patterns ==="

# Check for http:// pattern
$httpMatches = [regex]::Matches($content, 'https?://[^"''` >]+')
if ($httpMatches.Count -gt 0) {
    Write-Host "Found $($httpMatches.Count) URL references"
    $uniqueUrls = @{}
    foreach ($m in $httpMatches) {
        $url = $m.Value
        if ($url -notlike "*localhost*") {
            if (-not $uniqueUrls.ContainsKey($url)) {
                $uniqueUrls[$url] = 1
                Write-Host "  URL: $url"
            }
        }
    }
}

# Check for "api/" references
Write-Host ""
Write-Host "=== API path references ==="
$apiPatterns = @('"/api/', "'/api/", '`/api/', "api/", "BASE_URL", "API_BASE", "VITE_API")
foreach ($pattern in $apiPatterns) {
    if ($content.Contains($pattern)) {
        # Find context
        $idx = $content.IndexOf($pattern)
        $start = [Math]::Max(0, $idx - 50)
        $end = [Math]::Min($content.Length, $idx + 100)
        Write-Host "FOUND '$pattern' at context: $($content.Substring($start, $end - $start))"
        Write-Host ""
    }
}
