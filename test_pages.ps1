# Check individual page routes on GitHub Pages
$baseUrl = "https://nagato-yuki.github.io/smart-scheduler/"
$routes = @(
    "#/",
    "#/rooms",
    "#/teachers", 
    "#/classes",
    "#/courses",
    "#/holidays",
    "#/import",
    "#/schedule",
    "#/stats",
    "#/my-schedule"
)

Write-Host "=== Checking GitHub Pages HTML response for all routes ==="
Write-Host "Note: SPA routes all return the same index.html"
Write-Host ""

$response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing
Write-Host "Status Code: $($response.StatusCode)"
Write-Host "Has 'id=app': $($response.Content.Contains('id=`"app`"'))"
Write-Host "Has index-BPBzAIdl.js: $($response.Content.Contains('index-BPBzAIdl.js'))"
Write-Host "Has index-oH24NreO.css: $($response.Content.Contains('index-oH24NreO.css'))"

# Check JS bundle size and chunk count
$jsUrl = "https://nagato-yuki.github.io/smart-scheduler/assets/index-BPBzAIdl.js"
$jsResponse = Invoke-WebRequest -Uri $jsUrl -UseBasicParsing
Write-Host ""
Write-Host "JS Bundle Size: $($jsResponse.Content.Length) bytes"

# Count CSS references
$cssRefs = [regex]::Matches($jsResponse.Content, '\.css["'']')
Write-Host "CSS file references in JS: $($cssRefs.Count)"

# Check for page component references
$pageComponents = @("RoomManagement", "TeacherManagement", "ClassManagement", "CourseManagement", "HolidayManagement", "DataImport", "ScheduleManagement", "StatisticsView", "MySchedule", "ClassSchedule", "TeacherSchedule", "RoomSchedule")
Write-Host ""
Write-Host "--- Page Component References in JS Bundle ---"
foreach ($comp in $pageComponents) {
    if ($jsResponse.Content.Contains($comp)) {
        Write-Host "FOUND: $comp"
    }
}

# Check for API endpoints
Write-Host ""
Write-Host "--- API Endpoint References ---"
$apiEndpoints = @("/api/rooms", "/api/teachers", "/api/classes", "/api/courses", "/api/holidays", "/api/schedule", "/api/import")
foreach ($ep in $apiEndpoints) {
    $count = 0
    $idx = 0
    while (($idx = $jsResponse.Content.IndexOf($ep, $idx)) -ne -1) {
        $count++
        $idx++
    }
    if ($count -gt 0) {
        Write-Host "FOUND '$ep': $count occurrences"
    }
}

# Check for VITE environment variable pattern
Write-Host ""
Write-Host "--- Environment Config ---"
if ($jsResponse.Content.Contains("VITE_API")) {
    Write-Host "FOUND: VITE_API env var reference"
}
if ($jsResponse.Content.Contains("import.meta.env")) {
    Write-Host "FOUND: import.meta.env usage"
}
if ($jsResponse.Content.Contains("localhost")) {
    Write-Host "FOUND: localhost reference (dev config?)"
}
if ($jsResponse.Content.Contains("onrender")) {
    Write-Host "FOUND: onrender.com reference"
}
