# Deeper analysis of JS bundle
$url = "https://nagato-yuki.github.io/smart-scheduler/assets/index-BPBzAIdl.js"
$response = Invoke-WebRequest -Uri $url -UseBasicParsing
$content = $response.Content

# Convert to raw bytes to check encoding
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)

# Check for Unicode escape sequences for Chinese nav items
Write-Host "--- Checking for Unicode escaped Chinese characters ---"
$navUnicode = @{
    "教室管理" = "\u6559\u5ba4\u7ba1\u7406"
    "教师管理" = "\u6559\u5e08\u7ba1\u7406"
    "班级管理" = "\u73ed\u7ea7\u7ba1\u7406"
    "课程管理" = "\u8bfe\u7a0b\u7ba1\u7406"
    "假期管理" = "\u5047\u671f\u7ba1\u7406"
    "数据导入" = "\u6570\u636e\u5bfc\u5165"
    "排课管理" = "\u6392\u8bfe\u7ba1\u7406"
    "统计查看" = "\u7edf\u8ba1\u67e5\u770b"
    "我的课表" = "\u6211\u7684\u8bfe\u8868"
}

foreach ($entry in $navUnicode.GetEnumerator()) {
    $label = $entry.Key
    $unicode = $entry.Value
    if ($content.Contains($unicode)) {
        Write-Host "FOUND: $label (unicode escaped)"
    } else {
        Write-Host "NOT FOUND: $label"
    }
}

# Check for route definitions
Write-Host ""
Write-Host "--- Route path patterns ---"
$routePatterns = @("path:.*?rooms", "path:.*?teachers", "path:.*?classes", "path:.*?courses", "path:.*?holidays", "path:.*?import", "path:.*?schedule", "path:.*?stats", "path:.*?my")
foreach ($pattern in $routePatterns) {
    if ($content -match $pattern) {
        Write-Host "FOUND route pattern: $pattern"
    }
}

# Check for API URL patterns
Write-Host ""
Write-Host "--- API URL patterns ---"
$apiPatterns = @("api/rooms", "api/teachers", "api/classes", "api/courses", "api/holidays", "api/courses", "BASE_URL", "API_URL", "VITE_API", "/api/")
foreach ($pattern in $apiPatterns) {
    $count = 0
    $index = 0
    while (($index = $content.IndexOf($pattern, $index)) -ne -1) {
        $count++
        $index++
    }
    if ($count -gt 0) {
        Write-Host "FOUND '$pattern': $count occurrences"
    }
}

# Check the first occurrence of "schedule" context
Write-Host ""
Write-Host "--- Context around 'schedule' (first 500 chars) ---"
$idx = $content.IndexOf("schedule")
if ($idx -gt 0) {
    $start = [Math]::Max(0, $idx - 100)
    $end = [Math]::Min($content.Length, $idx + 400)
    Write-Host $content.Substring($start, $end - $start)
}
