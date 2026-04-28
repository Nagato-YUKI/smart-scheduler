# Check JS bundle for navigation items - simpler approach
$url = "https://nagato-yuki.github.io/smart-scheduler/assets/index-BPBzAIdl.js"
$response = Invoke-WebRequest -Uri $url -UseBasicParsing
$content = $response.Content

Write-Host "JS File Size: $($content.Length) bytes"
Write-Host ""

# Check for nav items directly (they should be in the bundle as plain text in React)
$navItems = @("教室管理", "教师管理", "班级管理", "课程管理", "假期管理", "数据导入", "排课管理", "统计查看", "我的课表")
Write-Host "--- Navigation Items in JS Bundle ---"
foreach ($item in $navItems) {
    if ($content.Contains($item)) {
        Write-Host "FOUND: $item"
    } else {
        Write-Host "NOT FOUND: $item"
    }
}

Write-Host ""
Write-Host "--- Check for key route paths ---"
$routePaths = @("rooms", "teachers", "classes", "courses", "holidays", "import", "schedule", "stats", "my-schedule")
foreach ($path in $routePaths) {
    if ($content.Contains($path)) {
        Write-Host "FOUND path: $path"
    } else {
        Write-Host "NOT FOUND path: $path"
    }
}

Write-Host ""
Write-Host "--- Check for API base URL ---"
if ($content.Contains("onrender.com")) {
    Write-Host "FOUND: backend URL (onrender.com)"
} else {
    Write-Host "NOT FOUND: backend URL"
}

# Check for React Router
Write-Host ""
Write-Host "--- Framework checks ---"
if ($content.Contains("react-router") -or $content.Contains("BrowserRouter") -or $content.Contains("HashRouter")) {
    Write-Host "FOUND: React Router"
} else {
    Write-Host "NOT FOUND: React Router"
}
if ($content.Contains("antd") -or $content.Contains("ant-design")) {
    Write-Host "FOUND: Ant Design"
} else {
    Write-Host "NOT FOUND: Ant Design"
}
