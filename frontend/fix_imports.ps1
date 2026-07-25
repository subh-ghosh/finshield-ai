$files = Get-ChildItem -Path "src" -Recurse -Include *.ts,*.tsx
foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Fix DTO imports
    $newContent = $content -replace 'import \{ (.*DTO) \}', 'import type { $1 }'
    
    # Fix domain entity imports
    $newContent = $newContent -replace 'import \{ (DashboardMetrics|CustomerProfile|QueueItem|InvestigationResult|Evidence|ExecutionStep|PlannerEvent|PlannerState) \}', 'import type { $1 }'
    
    if ($content -ne $newContent) {
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        Write-Host "Fixed imports in $($file.Name)"
    }
}
