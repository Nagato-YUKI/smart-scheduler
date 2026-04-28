# Test script for frontend validation
$url = "https://nagato-yuki.github.io/smart-scheduler/"
$response = Invoke-WebRequest -Uri $url -UseBasicParsing

Write-Host "StatusCode: $($response.StatusCode)"
Write-Host "ContentLength: $($response.Content.Length)"
Write-Host ""

# Check for nav elements
$navItems = @("教室管理", "教师管理", "班级管理", "课程管理", "假期管理", "数据导入", "排课管理", "统计查看", "我的课表")
Write-Host "--- Navigation Elements Check ---"
foreach ($item in $navItems) {
    if ($response.Content -match $item) {
        Write-Host "FOUND: $item"
    } else {
        Write-Host "NOT FOUND: $item"
    }
}

Write-Host ""
Write-Host "--- Check for React App Root ---"
if ($response.Content -match "root") {
    Write-Host "FOUND: root element"
}
if ($response.Content -match "smart-scheduler") {
    Write-Host "FOUND: smart-scheduler reference"
}

Write-Host ""
Write-Host "--- Check for JS/CSS references ---"
$links = $response.Links | Select-Object -First 10
foreach ($link in $links) {
    Write-Host "Link: $($link.href)"
}
