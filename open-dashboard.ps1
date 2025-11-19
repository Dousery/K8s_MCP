# Kubernetes Dashboard Açma Scripti

Write-Host "🔍 Kubernetes cluster kontrol ediliyor..." -ForegroundColor Yellow

# Cluster kontrolü
$clusterCheck = kubectl cluster-info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Kubernetes cluster'a bağlanılamıyor!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Çözüm seçenekleri:" -ForegroundColor Cyan
    Write-Host "1. Eğer bir cluster'ınız varsa:" -ForegroundColor White
    Write-Host "   - kubeconfig dosyanızı kontrol edin" -ForegroundColor Gray
    Write-Host "   - KUBECONFIG ortam değişkenini ayarlayın" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Yerel cluster kurmak için:" -ForegroundColor White
    Write-Host "   - Docker Desktop (Kubernetes'i etkinleştirin)" -ForegroundColor Gray
    Write-Host "   - Minikube: minikube start" -ForegroundColor Gray
    Write-Host "   - Kind: kind create cluster" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "✅ Cluster'a bağlanıldı" -ForegroundColor Green
Write-Host ""

# Dashboard'un kurulu olup olmadığını kontrol et
Write-Host "Dashboard kontrol ediliyor..." -ForegroundColor Yellow
$dashboardCheck = kubectl get deployment kubernetes-dashboard -n kubernetes-dashboard 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Dashboard kurulu degil. Kurulum baslatiliyor..." -ForegroundColor Yellow
    Write-Host ""
    
    # Dashboard'u kur
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
    
    # Service Account oluştur
    kubectl create serviceaccount dashboard-admin-sa -n kubernetes-dashboard 2>$null
    
    # ClusterRoleBinding oluştur
    kubectl create clusterrolebinding dashboard-admin-sa --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:dashboard-admin-sa 2>$null
    
    Write-Host "Dashboard'un hazir olmasi bekleniyor (bu birkac dakika surebilir)..." -ForegroundColor Yellow
    kubectl wait --for=condition=available --timeout=300s deployment/kubernetes-dashboard -n kubernetes-dashboard
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Dashboard kurulumu başarısız oldu" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Dashboard başarıyla kuruldu" -ForegroundColor Green
} else {
    Write-Host "✅ Dashboard zaten kurulu" -ForegroundColor Green
}

Write-Host ""

# Token'ı al
Write-Host "Dashboard erisim token'i olusturuluyor..." -ForegroundColor Yellow
$token = kubectl -n kubernetes-dashboard create token dashboard-admin-sa

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Token oluşturulamadı, alternatif yöntem deneniyor..." -ForegroundColor Yellow
    # Alternatif token alma yöntemi
    $token = kubectl get secret -n kubernetes-dashboard $(kubectl get serviceaccount dashboard-admin-sa -n kubernetes-dashboard -o jsonpath='{.secrets[0].name}') -o jsonpath='{.data.token}' | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DASHBOARD ERISIM TOKEN'i:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host $token -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Port-forward başlat
Write-Host "🌐 Dashboard'a erişim için port-forward başlatılıyor..." -ForegroundColor Green
Write-Host ""
Write-Host "📌 TARAYICINIZDA ŞU ADRESE GİDİN:" -ForegroundColor Yellow
Write-Host "   https://localhost:8443" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""
Write-Host "YUKARIDAKI TOKEN'I KULLANARAK GIRIS YAPIN" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Port-forward'u durdurmak için Ctrl+C tuşlarına basın" -ForegroundColor Red
Write-Host ""

# Port-forward'u başlat (arka planda)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443"

Write-Host "✅ Port-forward başlatıldı (yeni bir pencere açıldı)" -ForegroundColor Green
Write-Host ""
Write-Host "Ipucu: Tarayicinizda https://localhost:8443 adresine gidin" -ForegroundColor Cyan

