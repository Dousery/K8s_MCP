# MCP Server Kurulum Scripti (PowerShell)

Write-Host "K8s MCP Server kurulumu başlatılıyor..." -ForegroundColor Green

# Python kontrolü
Write-Host "Python kontrol ediliyor..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python bulunamadı! Lütfen Python'u kurun." -ForegroundColor Red
    exit 1
}
Write-Host "$pythonVersion bulundu" -ForegroundColor Green

# pip kontrolü
Write-Host "pip kontrol ediliyor..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip bulunamadı! Lütfen pip'i kurun." -ForegroundColor Red
    exit 1
}
Write-Host "$pipVersion bulundu" -ForegroundColor Green

# Bağımlılıkları kur
Write-Host "Bağımlılıklar kuruluyor..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Bağımlılıklar kurulamadı!" -ForegroundColor Red
    exit 1
}
Write-Host "Bağımlılıklar başarıyla kuruldu" -ForegroundColor Green

# kubectl kontrolü
Write-Host "kubectl kontrol ediliyor..." -ForegroundColor Yellow
$kubectlVersion = kubectl version --client 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "kubectl bulunamadı! Kubernetes işlemleri çalışmayabilir." -ForegroundColor Yellow
} else {
    Write-Host "kubectl bulundu" -ForegroundColor Green
}

# MCP yapılandırma dosyası oluştur
Write-Host "MCP yapılandırma dosyası oluşturuluyor..." -ForegroundColor Yellow
$currentPath = (Get-Location).Path
$mcpConfig = @{
    mcpServers = @{
        "k8s-mcp-server" = @{
            command = "python"
            args = @("server.py")
            cwd = $currentPath
            env = @{
                KUBECONFIG = ""
            }
        }
    }
} | ConvertTo-Json -Depth 10

$mcpConfig | Out-File -FilePath "mcp.json" -Encoding UTF8
Write-Host "mcp.json dosyası oluşturuldu" -ForegroundColor Green

# Claude Desktop config yolu göster
Write-Host ""
Write-Host "Sonraki Adımlar:" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "1. Claude Desktop config dosyasını açın:" -ForegroundColor White
Write-Host "   %APPDATA%\Claude\claude_desktop_config.json" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. mcp.json dosyasındaki içeriği Claude Desktop config'ine ekleyin" -ForegroundColor White
Write-Host ""
Write-Host "3. Claude Desktop'u yeniden başlatın" -ForegroundColor White
Write-Host ""
Write-Host "4. AI'a 'Kubernetes podlarini listele' gibi komutlar sorabilirsiniz!" -ForegroundColor White
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Kurulum tamamlandı!" -ForegroundColor Green

