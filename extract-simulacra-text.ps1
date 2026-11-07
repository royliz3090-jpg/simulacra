#!/usr/bin/env pwsh
# extract-simulacra-text.ps1
# Extrae mapeo URI -> datos binarios del archivo en-us.fs descomprimido de SIMULACRA
# Formato: [URI string]\x00\x00[2 bytes binarios][4 bytes offset] [siguiente URI]...

param(
    [string]$InputFile = "C:\IA-Prueba\SIMULACRA\extracted\core_assets_extracted\decompressed\en-us.fs.decompressed",
    [string]$OutputFile = "C:\IA-Prueba\SIMULACRA\extracted\core_assets_extracted\en-us-uri-mapping.json"
)

$bytes = [System.IO.File]::ReadAllBytes($InputFile)
$uriPrefix = [System.Text.Encoding]::ASCII.GetBytes("en-us://")

$entries = @()
$i = 0

while ($i -lt $bytes.Length - $uriPrefix.Length) {
    # Buscar inicio de URI
    $match = $true
    for ($j = 0; $j -lt $uriPrefix.Length; $j++) {
        if ($bytes[$i + $j] -ne $uriPrefix[$j]) { $match = $false; break }
    }

    if (-not $match) { $i++; continue }

    # Extraer URI (hasta byte nulo)
    $uriStart = $i
    $uriEnd = $i
    while ($uriEnd -lt $bytes.Length -and $bytes[$uriEnd] -ne 0) { $uriEnd++ }

    $uriBytes = $bytes[$uriStart..($uriEnd - 1)]
    $uri = [System.Text.Encoding]::ASCII.GetString($uriBytes)

    # Saltar bytes nulos (terminador de string)
    $pos = $uriEnd + 1
    if ($pos -lt $bytes.Length -and $bytes[$pos] -eq 0) { $pos++ }

    # Leer 2 bytes binarios + 4 bytes offset
    if ($pos + 6 -le $bytes.Length) {
        $bin2 = ($bytes[$pos] -bor ($bytes[$pos + 1] -shl 8))
        $offset4 = ($bytes[$pos + 2] -bor ($bytes[$pos + 3] -shl 8) -bor ($bytes[$pos + 4] -shl 16) -bor ($bytes[$pos + 5] -shl 24))
    } else {
        $bin2 = 0
        $offset4 = 0
    }

    $entries += [PSCustomObject]@{
        uri = $uri
        bin2 = $bin2
        bin2_hex = "0x{0:X4}" -f $bin2
        offset4 = $offset4
        offset4_hex = "0x{0:X8}" -f $offset4
        position = $uriStart
    }

    $i = $uriEnd + 1
}

# Ordenar por posición
$entries = $entries | Sort-Object position

# Exportar a JSON
$json = $entries | ConvertTo-Json -Depth 3
[System.IO.File]::WriteAllText($OutputFile, $json)

Write-Host "Extraídas $($entries.Count) entradas URI a $OutputFile"

# Mostrar resumen por categoría
$categories = @{}
foreach ($e in $entries) {
    $cat = "otro"
    if ($e.uri -like "*calls/dialog*") { $cat = "dialogo_llamadas" }
    elseif ($e.uri -like "*chats*") { $cat = "chats" }
    elseif ($e.uri -like "*mail*") { $cat = "correo" }
    elseif ($e.uri -like "*spark*") { $cat = "spark" }
    elseif ($e.uri -like "*subtitles*") { $cat = "subtitulos" }
    elseif ($e.uri -like "*weblayouts*" -or $e.uri -like "*webpages*") { $cat = "web" }
    elseif ($e.uri -like "*restphrase*") { $cat = "frases_restauracion" }
    elseif ($e.uri -like "*restimage*") { $cat = "imagenes_restauracion" }
    elseif ($e.uri -like "*config*") { $cat = "configuracion" }
    if (-not $categories.ContainsKey($cat)) { $categories[$cat] = 0 }
    $categories[$cat]++
}

Write-Host "`nResumen por categoría:"
foreach ($cat in $categories.Keys | Sort-Object) {
    $count = $categories[$cat]; Write-Host ("  {0}: {1}" -f $cat, $count)
}