$files = Get-ChildItem -Path "src" -Recurse -Include *.tsx,*.ts,*.css
foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw
    $newContent = $content -replace 'bg-\[#E1000F\]', 'bg-brand-red'
    $newContent = $newContent -replace 'text-\[#E1000F\]', 'text-brand-red'
    $newContent = $newContent -replace 'border-\[#E1000F\]', 'border-brand-red'
    
    $newContent = $newContent -replace 'bg-\[#1E1E1E\]', 'bg-brand-black'
    $newContent = $newContent -replace 'text-\[#1E1E1E\]', 'text-brand-black'
    $newContent = $newContent -replace 'border-\[#1E1E1E\]', 'border-brand-black'

    $newContent = $newContent -replace 'bg-\[#9CA3AF\]', 'bg-brand-gray'
    $newContent = $newContent -replace 'text-\[#9CA3AF\]', 'text-brand-gray'
    $newContent = $newContent -replace 'border-\[#9CA3AF\]', 'border-brand-gray'
    
    if ($content -ne $newContent) {
        Set-Content -Path $file.FullName -Value $newContent -NoNewline
        Write-Host "Updated $($file.Name)"
    }
}
