#!/bin/bash
# Ubuntu部署脚本

# 1. 系统依赖
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip git

# 2. 克隆仓库
git clone https://github.com/laohong0505/okxbot_pro.git
cd okx_bot

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 证书修复
sudo apt install -y ca-certificates
sudo update-ca-certificates
pip install --upgrade certifi

# 5. 安装依赖
pip install -r requirements.txt || pip install requests python-dotenv cryptography

# 6. 配置.env
if [ ! -f ".env" ]; then
    cat > .env <<EOF
OKX_API_KEY="your_api_key"
OKX_SECRET_KEY="your_secret_key"
OKX_PASSPHRASE="your_passphrase"
SANDBOX_MODE="true"
EOF
    chmod 600 .env
fi

# 7. 启动测试
python3 okxbot_pro.py --test
