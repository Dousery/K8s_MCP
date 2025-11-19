# K8s_MCP
An AI-powered Model Context Protocol server that lets language models directly manage and visualize Kubernetes clusters through safe, high-level operational tools.

## 🚀 AI'da Kullanım (Kurulum)

MCP server'ınızı Claude Desktop, Cursor veya diğer MCP destekleyen AI araçlarında kullanabilirsiniz.

> 📖 **Hızlı Başlangıç için:** [QUICKSTART.md](QUICKSTART.md) dosyasına bakın!

### 1. Bağımlılıkları Kurun

```powershell
# Python bağımlılıklarını kurun
pip install -r requirements.txt

# kubectl'in kurulu olduğundan emin olun
kubectl version --client
```

### 2. MCP Yapılandırması

#### Claude Desktop için:

1. Claude Desktop'u açın
2. MCP ayarları dosyasını bulun:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. Yapılandırma dosyasını düzenleyin:

```json
{
  "mcpServers": {
    "k8s-mcp-server": {
      "command": "python",
      "args": [
        "server.py"
      ],
      "cwd": "C:\\Users\\dogus\\OneDrive\\Masaüstü\\k8s_mcp",
      "env": {
        "KUBECONFIG": ""
      }
    }
  }
}
```

**Önemli:** `cwd` yolunu kendi proje dizininize göre güncelleyin!

#### Cursor için:

Cursor zaten MCP desteğine sahip. Eğer Cursor kullanıyorsanız, MCP server otomatik olarak algılanabilir veya manuel olarak yapılandırmanız gerekebilir.

1. Cursor ayarlarını açın
2. MCP bölümüne gidin
3. Yeni MCP server ekleyin:
   - **Name**: `k8s-mcp-server`
   - **Command**: `python`
   - **Args**: `["server.py"]`
   - **Working Directory**: Proje dizininizin tam yolu

### 3. Test Edin

Claude Desktop veya Cursor'u yeniden başlatın ve AI'a şunu sorun:

```
"Kubernetes cluster'ımdaki pod'ları listele"
```

veya

```
"default namespace'indeki deployment'ları göster"
```

### 4. Kullanılabilir Komutlar

MCP server'ınız aşağıdaki komutları destekler:

- **Pod İşlemleri**: `list_pods`, `get_pod_logs`, `describe_pod`
- **Deployment İşlemleri**: `list_deployments`, `scale_deployment`, `restart_deployment`
- **YAML İşlemleri**: `apply_yaml`, `get_yaml`
- **Event İzleme**: `list_events`
- **Service İşlemleri**: `list_services`, `describe_service`
- **Namespace İşlemleri**: `list_namespaces`, `create_namespace`, `delete_namespace`
- **Node İşlemleri**: `list_nodes`, `describe_node`, `cluster_info`, `list_pods_by_node`

### Sorun Giderme

**Problem**: MCP server bağlanmıyor
- Python'un PATH'te olduğundan emin olun
- `cwd` yolunun doğru olduğunu kontrol edin
- `pip install -r requirements.txt` komutunu çalıştırdığınızdan emin olun

**Problem**: Kubernetes bağlantı hatası
- `kubectl` komutunun çalıştığını kontrol edin: `kubectl cluster-info`
- KUBECONFIG ortam değişkeninin doğru ayarlandığından emin olun

## Pod'ları Canlı Görüntüleme Platformları

Deployment'larınızı kurduktan sonra pod'ları canlı görmek için aşağıdaki platformları kullanabilirsiniz:

### 1. Kubernetes Dashboard (Resmi Web UI) ⭐ Önerilen

Kubernetes'in resmi web arayüzü. Pod'ları, deployment'ları, servisleri ve diğer kaynakları görsel olarak yönetebilirsiniz.

**Kurulum (Otomatik Script):**
```powershell
# Windows PowerShell
.\open-dashboard.ps1
```

**Kurulum (Manuel):**
```bash
# Dashboard'u kurun
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Service Account ve ClusterRoleBinding oluşturun
kubectl create serviceaccount dashboard-admin-sa -n kubernetes-dashboard
kubectl create clusterrolebinding dashboard-admin-sa --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:dashboard-admin-sa

# Token'ı alın
kubectl -n kubernetes-dashboard create token dashboard-admin-sa

# Dashboard'a erişim için port-forward
kubectl port-forward -n kubernetes-dashboard service/kubernetes-dashboard 8443:443
```

Tarayıcıda `https://localhost:8443` adresine gidin ve token ile giriş yapın.

### 2. Lens (Desktop Uygulaması) 🚀 En Popüler

Güçlü bir desktop uygulaması. Gerçek zamanlı pod durumları, log görüntüleme ve kaynak kullanımı grafikleri.

**Kurulum:**
- [Lens'i indirin](https://k8slens.dev/) ve kurun
- Kubernetes cluster'ınıza bağlanın (kubeconfig dosyanızı seçin)
- Tüm pod'ları, deployment'ları ve servisleri canlı görebilirsiniz

### 3. k9s (Terminal Tabanlı)

Terminal üzerinden hızlı ve etkili bir arayüz.

**Kurulum:**
```bash
# Windows (Chocolatey)
choco install k9s

# veya Scoop
scoop install k9s

# Kullanım
k9s
```

### 4. Octant (VMware)

Açık kaynak web tabanlı arayüz.

**Kurulum:**
```bash
# Windows için indirin
# https://github.com/vmware-tanzu/octant/releases

# Çalıştırın
octant
```

Tarayıcıda `http://127.0.0.1:7777` adresine gidin.

### 5. Rancher (Enterprise Platform)

Kubernetes yönetimi için kapsamlı bir platform.

**Kurulum:**
```bash
kubectl apply -f https://github.com/rancher/rancher/releases/download/v2.8.0/rancher.yaml
```

### Hızlı Başlangıç

En hızlı yol için **Lens** veya **k9s** kullanmanızı öneririz. Kubernetes Dashboard da iyi bir seçenektir ancak kurulumu biraz daha karmaşıktır.