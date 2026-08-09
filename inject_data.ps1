# TZANiX Edge Node - Script de Inyeccion de Telemetria Real (Default: AI_Model_Optimizer)
Clear-Host
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "         TZANiX DATA SOLUTIONS - INYECTOR DE TELEMETRIA         " -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Iniciando canal de comunicacion con el Nodo Edge local..." -ForegroundColor Gray

$Uri = "http://127.0.0.1:8000/api/v1/purify-stream"
$ApiKey = "ifa_live_btc_trader_99x"  # Cambiado a la llave por defecto de AI_Model_Optimizer

# Cargar datos desde el archivo de muestra si existe
$FilePath = Join-Path $PSScriptRoot "sample_noisy_data.txt"
if (Test-Path $FilePath) {
    $RawData = Get-Content $FilePath
    $Sequences = $RawData.Split(",") | ForEach-Object { [double]$_.Trim() }
    Write-Host "[OK] Archivo 'sample_noisy_data.txt' cargado con exito. ($($Sequences.Count) muestras)" -ForegroundColor Green
} else {
    # Fallback: Generar muestras aleatorias ruidosas
    $Sequences = @(15.4, 23.8, -12.4, 45.2, 33.1, 8.4, -2.5, 67.2, 54.9, 12.1)
    Write-Host "[WARNING] No se encontro 'sample_noisy_data.txt'. Usando datos de telemetria de respaldo." -ForegroundColor Yellow
}

$Headers = @{
    "Content-Type" = "application/json"
    "X-IFA-Key" = $ApiKey
}

Write-Host "`nPresiona Ctrl+C para detener la inyeccion en vivo.`n" -ForegroundColor DarkGray

$Iteration = 1
while ($true) {
    # Agregar un pequeno ruido aleatorio para que los datos varien ligeramente en cada envio
    $NoisySequences = @()
    foreach ($val in $Sequences) {
        $NoisySequences += [Math]::Round($val + (Get-Random -Minimum -2.0 -Maximum 2.0), 4)
    }

    $Body = @{
        "data_stream_id" = "POWERSHELL_EDGE_NODE"
        "stream_type" = "financial"
        "sequences" = $NoisySequences
        "scale_factor" = 1
    } | ConvertTo-Json -Depth 5

    try {
        $Response = Invoke-RestMethod -Uri $Uri -Method Post -Headers $Headers -Body $Body
        
        Write-Host "[ENVIO #$Iteration] ($($NoisySequences.Count) Ticks) -> API de Borde..." -ForegroundColor Cyan
        Write-Host "  >> Atenuacion de Ruido (IFA): $($Response.compute_efficiency_gain)%" -ForegroundColor Green
        Write-Host "  >> Firma Morton 4D: $($Response.spatial_signature_4d)" -ForegroundColor Yellow
        Write-Host "  >> Coordenadas Proyectadas: X:$([Math]::Round($Response.spatial_coordinates[0],3)) Y:$([Math]::Round($Response.spatial_coordinates[1],3)) Z:$([Math]::Round($Response.spatial_coordinates[2],3))" -ForegroundColor Gray
        Write-Host "---------------------------------------------------------" -ForegroundColor DarkGray
    } catch {
        Write-Host "[ERROR] No se pudo establecer conexion con el Nodo de Borde de TZANiX. Asegurate de que la API este corriendo." -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }

    $Iteration++
    Start-Sleep -Seconds 2
}
