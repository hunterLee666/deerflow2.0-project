"""
案例 22: DeerFlow 2.0 CI/CD 集成
完整代码示例 - GitHub Actions、Docker、自动化部署
"""

# 这个文件包含 CI/CD 配置和部署脚本
# 实际使用时需要拆分到不同文件中

"""
================== .github/workflows/ci.yml ==================
"""

GITHUB_ACTIONS_CONFIG = """
name: DeerFlow CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: |
        mypy deerflow/ --ignore-missing-imports
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=deerflow --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/deerflow:latest
          ${{ secrets.DOCKER_USERNAME }}/deerflow:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Deploy to Staging
      run: |
        echo "Deploying to staging environment"
        # kubectl set image deployment/deerflow deerflow=${{ secrets.DOCKER_USERNAME }}/deerflow:${{ github.sha }}
    
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Deploy to Production
      run: |
        echo "Deploying to production environment"
        # kubectl set image deployment/deerflow deerflow=${{ secrets.DOCKER_USERNAME }}/deerflow:${{ github.sha }}
"""

"""
================== Dockerfile ==================
"""

DOCKERFILE = """
# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 生产镜像
FROM python:3.11-slim

WORKDIR /app

# 创建非 root 用户
RUN groupadd -r deerflow && useradd -r -g deerflow deerflow

# 从构建阶段复制依赖
COPY --from=builder /root/.local /home/deerflow/.local
ENV PATH=/home/deerflow/.local/bin:$PATH

# 复制应用代码
COPY --chown=deerflow:deerflow . .

# 切换到非 root 用户
USER deerflow

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""

"""
================== docker-compose.yml ==================
"""

DOCKER_COMPOSE = """
version: '3.8'

services:
  deerflow-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEERFLOW_CONFIG_PATH=/app/config.yaml
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:password@db:5432/deerflow
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - redis
      - db
    networks:
      - deerflow-network
    restart: unless-stopped

  deerflow-worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:password@db:5432/deerflow
    depends_on:
      - redis
      - db
    networks:
      - deerflow-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - deerflow-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=deerflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - deerflow-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - deerflow-api
    networks:
      - deerflow-network
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:

networks:
  deerflow-network:
    driver: bridge
"""

"""
================== deploy.py ==================
"""

DEPLOY_SCRIPT = """
#!/usr/bin/env python3
\"\"\"
DeerFlow 部署脚本
\"\"\"


import argparse
import subprocess
import sys
import os
import json
from typing import Dict, List


class Deployer:
    \"\"\"部署器\"\"\"
    
    def __init__(self, environment: str):
        self.environment = environment
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        \"\"\"加载配置\"\"\"
        config_file = f"config/deploy.{self.environment}.json"
        if os.path.exists(config_file):
            with open(config_file) as f:
                return json.load(f)
        return {}
    
    def run_command(self, command: List[str], check: bool = True):
        \"\"\"运行命令\"\"\"
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(command, check=check)
        return result.returncode == 0
    
    def build(self):
        \"\"\"构建 Docker 镜像\"\"\"
        tag = self.config.get('image_tag', 'latest')
        image_name = f"deerflow:{tag}"
        
        self.run_command([
            'docker', 'build',
            '-t', image_name,
            '-f', 'Dockerfile',
            '.'
        ])
        
        print(f"Built image: {image_name}")
        return image_name
    
    def push(self, image_name: str):
        \"\"\"推送镜像到仓库\"\"\"
        registry = self.config.get('docker_registry')
        if registry:
            remote_name = f"{registry}/{image_name}"
            self.run_command(['docker', 'tag', image_name, remote_name])
            self.run_command(['docker', 'push', remote_name])
            print(f"Pushed to: {remote_name}")
    
    def deploy_k8s(self):
        \"\"\"部署到 Kubernetes\"\"\"
        namespace = self.config.get('k8s_namespace', 'default')
        
        # 应用配置
        self.run_command([
            'kubectl', 'apply',
            '-f', f'k8s/{self.environment}/',
            '-n', namespace
        ])
        
        # 更新镜像
        image = self.config.get('image_tag', 'latest')
        self.run_command([
            'kubectl', 'set', 'image',
            'deployment/deerflow-api',
            f'deerflow-api=deerflow:{image}',
            '-n', namespace
        ])
        
        # 等待部署完成
        self.run_command([
            'kubectl', 'rollout', 'status',
            'deployment/deerflow-api',
            '-n', namespace
        ])
        
        print(f"Deployed to Kubernetes namespace: {namespace}")
    
    def deploy_docker_compose(self):
        \"\"\"使用 Docker Compose 部署\"\"\"
        self.run_command([
            'docker-compose',
            '-f', 'docker-compose.yml',
            'up', '-d', '--build'
        ])
        
        print("Deployed with Docker Compose")
    
    def rollback(self):
        \"\"\"回滚部署\"\"\"
        if self.config.get('deployment_type') == 'k8s':
            namespace = self.config.get('k8s_namespace', 'default')
            self.run_command([
                'kubectl', 'rollout', 'undo',
                'deployment/deerflow-api',
                '-n', namespace
            ])
        else:
            # Docker Compose 回滚
            self.run_command(['docker-compose', 'down'])
            self.run_command(['docker-compose', 'up', '-d'])
        
        print("Rollback completed")
    
    def health_check(self) -> bool:
        \"\"\"健康检查\"\"\"
        url = self.config.get('health_check_url', 'http://localhost:8000/health')
        
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.status == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='DeerFlow Deployment Tool')
    parser.add_argument('action', choices=[
        'build', 'push', 'deploy', 'rollback', 'health'
    ])
    parser.add_argument('--env', default='staging', choices=['staging', 'production'])
    parser.add_argument('--type', default='docker', choices=['docker', 'k8s'])
    
    args = parser.parse_args()
    
    deployer = Deployer(args.env)
    
    if args.action == 'build':
        deployer.build()
    
    elif args.action == 'push':
        image = deployer.build()
        deployer.push(image)
    
    elif args.action == 'deploy':
        if args.type == 'k8s':
            deployer.deploy_k8s()
        else:
            deployer.deploy_docker_compose()
        
        # 部署后健康检查
        if deployer.health_check():
            print("Deployment successful!")
        else:
            print("Deployment failed health check!")
            sys.exit(1)
    
    elif args.action == 'rollback':
        deployer.rollback()
    
    elif args.action == 'health':
        if deployer.health_check():
            print("Health check passed!")
        else:
            print("Health check failed!")
            sys.exit(1)


if __name__ == '__main__':
    main()
"""


def generate_cicd_files():
    """生成 CI/CD 文件"""
    import os
    
    # 创建目录
    os.makedirs('.github/workflows', exist_ok=True)
    
    # 写入 GitHub Actions 配置
    with open('.github/workflows/ci.yml', 'w') as f:
        f.write(GITHUB_ACTIONS_CONFIG)
    
    # 写入 Dockerfile
    with open('Dockerfile', 'w') as f:
        f.write(DOCKERFILE)
    
    # 写入 docker-compose.yml
    with open('docker-compose.yml', 'w') as f:
        f.write(DOCKER_COMPOSE)
    
    # 写入部署脚本
    with open('deploy.py', 'w') as f:
        f.write(DEPLOY_SCRIPT)
    
    print("CI/CD files generated:")
    print("  - .github/workflows/ci.yml")
    print("  - Dockerfile")
    print("  - docker-compose.yml")
    print("  - deploy.py")


if __name__ == "__main__":
    generate_cicd_files()
