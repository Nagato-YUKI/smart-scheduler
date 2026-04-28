# Check localhost context to understand API config
$jsUrl = "https://nagato-yuki.github.io/smart-scheduler/assets/index-BPBzAIdl.js"
$jsResponse = Invoke-WebRequest -Uri $jsUrl -UseBasicParsing
$content = $jsResponse.Content

Write-Host "=== localhost references context ==="
$idx = 0
$count = 0
while (($idx = $content.IndexOf("localhost", $idx)) -ne -1) {
    $start = [Math]::Max(0, $idx - 80)
    $end = [Math]::Min($content.Length, $idx + 120)
    $count++
    Write-Host "[$count] $($content.Substring($start, $end - $start))"
    Write-Host ""
    $idx++
    if ($count -ge 5) { break }
}

Write-Host ""
Write-Host "=== Check for 'import.meta.env' context ==="
$idx = 0
$count = 0
while (($idx = $content.IndexOf("import.meta", $idx)) -ne -1) {
    $start = [Math]::Max(0, $idx - 50)
    $end = [Math]::Min($content.Length, $idx + 150)
    $count++
    Write-Host "[$count] $($content.Substring($start, $end - $start))"
    Write-Host ""
    $idx++
    if ($count -ge 5) { break }
}

Write-Host ""
Write-Host "=== Check for fetch/axios/request context ==="
$patterns = @("axios.create", "fetch(", "request(", "axios(")
foreach ($p in $patterns) {
    $idx = $content.IndexOf($p)
    if ($idx -gt 0) {
        $start = [Math]::Max(0, $idx - 100)
        $end = [Math]::Min($content.Length, $idx + 200)
        Write-Host "FOUND '$p': $($content.Substring($start, $end - $start))"
        Write-Host ""
    }
}
