"""
案例 23: DeerFlow 2.0 容器化部署
完整代码示例 - Kubernetes、Helm、服务网格
"""

"""
================== k8s/deployment.yaml ==================
"""

K8S_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deerflow-api
  labels:
    app: deerflow-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: deerflow-api
  template:
    metadata:
      labels:
        app: deerflow-api
    spec:
      containers:
      - name: deerflow-api
        image: deerflow:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEERFLOW_CONFIG_PATH
          value: "/app/config/config.yaml"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: deerflow-secrets
              key: redis-url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: deerflow-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: config
        configMap:
          name: deerflow-config
      - name: logs
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - deerflow-api
              topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: deerflow-api
spec:
  selector:
    app: deerflow-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: deerflow-ingress
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.deerflow.io
    secretName: deerflow-tls
  rules:
  - host: api.deerflow.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: deerflow-api
            port:
              number: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: deerflow-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: deerflow-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
"""

"""
================== helm/Chart.yaml ==================
"""

HELM_CHART = """
apiVersion: v2
name: deerflow
description: A Helm chart for DeerFlow
type: application
version: 0.1.0
appVersion: "2.0.0"
dependencies:
- name: redis
  version: "17.x.x"
  repository: "https://charts.bitnami.com/bitnami"
  condition: redis.enabled
- name: postgresql
  version: "12.x.x"
  repository: "https://charts.bitnami.com/bitnami"
  condition: postgresql.enabled
"""

"""
================== helm/values.yaml ==================
"""

HELM_VALUES = """
replicaCount: 3

image:
  repository: deerflow
  pullPolicy: IfNotPresent
  tag: ""

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
  hosts:
    - host: api.deerflow.io
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: deerflow-tls
      hosts:
        - api.deerflow.io

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

config:
  model_name: "gpt-4"
  thinking_enabled: true
  subagent_enabled: true

redis:
  enabled: true
  auth:
    enabled: true
    password: redis-password

postgresql:
  enabled: true
  auth:
    username: deerflow
    password: postgres-password
    database: deerflow
"""

"""
================== istio/virtual-service.yaml ==================
"""

ISTIO_CONFIG = """
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: deerflow
spec:
  hosts:
  - api.deerflow.io
  gateways:
  - deerflow-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/
    route:
    - destination:
        host: deerflow-api
        port:
          number: 80
      weight: 100
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
    fault:
      delay:
        percentage:
          value: 0.1
        fixedDelay: 5s
  - match:
    - uri:
        prefix: /health
    route:
    - destination:
        host: deerflow-api
        port:
          number: 80
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: deerflow
spec:
  host: deerflow-api
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
---
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: deerflow
spec:
  selector:
    matchLabels:
      app: deerflow-api
  mtls:
    mode: STRICT
"""


class KubernetesManager:
    """Kubernetes 管理器"""
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
    
    def apply(self, manifest: str):
        """应用 Kubernetes 配置"""
        import subprocess
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(manifest)
            temp_file = f.name
        
        try:
            subprocess.run([
                'kubectl', 'apply', '-f', temp_file, '-n', self.namespace
            ], check=True)
        finally:
            import os
            os.unlink(temp_file)
    
    def deploy(self):
        """部署应用"""
        self.apply(K8S_DEPLOYMENT)
        print(f"Deployed to namespace: {self.namespace}")
    
    def get_pods(self) -> List[str]:
        """获取 Pod 列表"""
        import subprocess
        
        result = subprocess.run([
            'kubectl', 'get', 'pods', '-n', self.namespace,
            '-l', 'app=deerflow-api', '-o', 'jsonpath={.items[*].metadata.name}'
        ], capture_output=True, text=True)
        
        return result.stdout.split()
    
    def logs(self, pod_name: str, follow: bool = False):
        """查看日志"""
        import subprocess
        
        cmd = ['kubectl', 'logs', '-n', self.namespace, pod_name]
        if follow:
            cmd.append('-f')
        
        subprocess.run(cmd)
    
    def scale(self, replicas: int):
        """扩缩容"""
        import subprocess
        
        subprocess.run([
            'kubectl', 'scale', 'deployment', 'deerflow-api',
            '--replicas', str(replicas), '-n', self.namespace
        ], check=True)
        
        print(f"Scaled to {replicas} replicas")


class HelmManager:
    """Helm 管理器"""
    
    def __init__(self, release_name: str = "deerflow", namespace: str = "default"):
        self.release_name = release_name
        self.namespace = namespace
    
    def install(self, chart_path: str = "./helm", values_file: str = None):
        """安装 Helm Chart"""
        import subprocess
        
        cmd = [
            'helm', 'install', self.release_name, chart_path,
            '-n', self.namespace, '--create-namespace'
        ]
        
        if values_file:
            cmd.extend(['-f', values_file])
        
        subprocess.run(cmd, check=True)
        print(f"Installed {self.release_name} in {self.namespace}")
    
    def upgrade(self, chart_path: str = "./helm", values_file: str = None):
        """升级 Helm Chart"""
        import subprocess
        
        cmd = [
            'helm', 'upgrade', self.release_name, chart_path,
            '-n', self.namespace
        ]
        
        if values_file:
            cmd.extend(['-f', values_file])
        
        subprocess.run(cmd, check=True)
        print(f"Upgraded {self.release_name}")
    
    def uninstall(self):
        """卸载 Helm Chart"""
        import subprocess
        
        subprocess.run([
            'helm', 'uninstall', self.release_name, '-n', self.namespace
        ], check=True)
        
        print(f"Uninstalled {self.release_name}")


# 生成 K8s 配置文件
def generate_k8s_files():
    """生成 Kubernetes 配置文件"""
    import os
    
    # 创建目录
    os.makedirs('k8s/base', exist_ok=True)
    os.makedirs('k8s/overlays/staging', exist_ok=True)
    os.makedirs('k8s/overlays/production', exist_ok=True)
    os.makedirs('helm/templates', exist_ok=True)
    os.makedirs('istio', exist_ok=True)
    
    # 写入 K8s 配置
    with open('k8s/base/deployment.yaml', 'w') as f:
        f.write(K8S_DEPLOYMENT)
    
    # 写入 Helm Chart
    with open('helm/Chart.yaml', 'w') as f:
        f.write(HELM_CHART)
    
    with open('helm/values.yaml', 'w') as f:
        f.write(HELM_VALUES)
    
    # 写入 Istio 配置
    with open('istio/virtual-service.yaml', 'w') as f:
        f.write(ISTIO_CONFIG)
    
    print("Kubernetes files generated:")
    print("  - k8s/base/deployment.yaml")
    print("  - helm/Chart.yaml")
    print("  - helm/values.yaml")
    print("  - istio/virtual-service.yaml")


if __name__ == "__main__":
    generate_k8s_files()
    
    # 演示 K8s 管理
    print("\n" + "=" * 60)
    print("Kubernetes 管理演示")
    print("=" * 60)
    
    k8s = KubernetesManager(namespace="deerflow")
    
    # 显示命令
    print("\n部署命令:")
    print("  kubectl apply -f k8s/base/")
    
    print("\n查看 Pod:")
    print("  kubectl get pods -n deerflow")
    
    print("\n扩缩容:")
    print("  kubectl scale deployment deerflow-api --replicas=5 -n deerflow")
