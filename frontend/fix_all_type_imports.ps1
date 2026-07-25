$files = Get-ChildItem -Path "src" -Recurse -Include *.ts,*.tsx
foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Fix I*Repository imports
    $newContent = $content -replace 'import \{ (I[A-Z][a-zA-Z]*Repository) \}', 'import type { $1 }'
    
    # Fix DTO imports (in case previous script missed some multi-line or something, though it shouldn't have)
    $newContent = $newContent -replace 'import \{ ([a-zA-Z]*DTO) \}', 'import type { $1 }'

    # Fix Entities
    $newContent = $newContent -replace 'import \{ (DashboardMetrics|CustomerProfile|QueueItem|InvestigationResult|Evidence|ExecutionStep|PlannerEvent|PlannerState) \}', 'import type { $1 }'
    
    if ($content -ne $newContent) {
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        Write-Host "Fixed imports in $($file.Name)"
    }
}
