# Test script for frontend validation - show raw HTML
$url = "https://nagato-yuki.github.io/smart-scheduler/"
$response = Invoke-WebRequest -Uri $url -UseBasicParsing

Write-Host "StatusCode: $($response.StatusCode)"
Write-Host "ContentLength: $($response.Content.Length)"
Write-Host "ContentType: $($response.ContentType)"
Write-Host ""
Write-Host "=== RAW HTML CONTENT ==="
Write-Host $response.Content
Write-Host "=== END HTML ==="

Write-Host ""
Write-Host "=== Links ==="
foreach ($link in $response.Links) {
    Write-Host "  $($link.href)"
}

Write-Host ""
Write-Host "=== Images ==="
foreach ($img in $response.Images) {
    Write-Host "  $($img.src)"
}
