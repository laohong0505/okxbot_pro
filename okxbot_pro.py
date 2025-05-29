#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import hashlib
import hmac
import base64
import socket
import ssl
import threading
from datetime import datetime
from urllib.parse import urljoin
import requests
from dotenv import load_dotenv

# ============ 环境初始化 ============
try:
    load_dotenv()
except Exception as e:
    print(f"⚠️ 环境加载失败: {e}")
    sys.exit(1)

# ============ 配置类 ============
class Config:
    # 从环境变量加载
    API_KEY = os.getenv("OKX_API_KEY", "").strip('"\'')
    SECRET_KEY = os.getenv("OKX_SECRET_KEY", "").strip('"\'')
    PASSPHRASE = os.getenv("OKX_PASSPHRASE", "").strip('"\'')
    SANDBOX = os.getenv("SANDBOX_MODE", "true").lower() == "true"
    
    # 网络配置
    API_DOMAIN = "www.okx.cab" if SANDBOX else "www.okx.com"
    BASE_URL = f"https://{API_DOMAIN}"
    API_PREFIX = "/api/v5"
    TIMEOUT = 10
    SSL_VERIFY = True  # 生产环境建议True
    
    # 交易参数
    SPOT_SYMBOL = "GMT-USDT"
    SWAP_SYMBOL = "BTC-USDT-SWAP"
    LEVERAGE = 20
    MAX_DRAWDOWN = 0.05

# ============ SSL证书修复 ============
def fix_ssl_context():
    """修复SSL证书验证问题"""
    try:
        # 加载系统证书
        ctx = ssl.create_default_context()
        if not Config.SSL_VERIFY:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx
    except Exception as e:
        print(f"⚠️ SSL上下文创建失败: {e}")
        return None

ssl_ctx = fix_ssl_context()

# ============ API客户端 ============
class OKXClient:
    @staticmethod
    def _sign(timestamp, method, path, body=""):
        message = timestamp + method.upper() + path + str(body)
        return base64.b64encode(
            hmac.new(
                Config.SECRET_KEY.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

    @staticmethod
    def request(method, endpoint, body=None, retry=3):
        path = f"{Config.API_PREFIX}{endpoint}"
        url = urljoin(Config.BASE_URL, path)
        
        for attempt in range(retry):
            try:
                timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
                signature = OKXClient._sign(timestamp, method, path, body)
                
                headers = {
                    "OK-ACCESS-KEY": Config.API_KEY,
                    "OK-ACCESS-SIGN": signature,
                    "OK-ACCESS-TIMESTAMP": timestamp,
                    "OK-ACCESS-PASSPHRASE": Config.PASSPHRASE,
                    "Content-Type": "application/json"
                }
                
                resp = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body,
                    timeout=Config.TIMEOUT,
                    verify=ssl_ctx
                )
                resp.raise_for_status()
                return resp.json()
                
            except requests.exceptions.SSLError as e:
                print(f"🔒 SSL错误，尝试禁用验证 (测试环境可临时使用)")
                Config.SSL_VERIFY = False
                ssl_ctx = fix_ssl_context()
                if attempt == retry - 1:
                    raise Exception(f"SSL验证失败: {e}")
                
            except requests.exceptions.RequestException as e:
                if attempt == retry - 1:
                    raise Exception(f"API请求失败: {e}")
                time.sleep(2 ** attempt)

# ============ 交易引擎 ============
class TradingEngine:
    def __init__(self):
        self.running = True
        self._check_environment()

    def _check_environment(self):
        """检查环境和API连接"""
        print("\n🔍 环境诊断中...")
        
        # 检查虚拟环境
        if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
            print("⚠️ 警告: 未检测到虚拟环境")
        
        # 检查API连接
        try:
            print(f"测试连接到 {Config.API_DOMAIN}...")
            start = time.time()
            okx_time = OKXClient.request("GET", "/public/time")
            latency = (time.time() - start) * 1000
            print(f"✅ 连接成功! 延迟: {latency:.2f}ms | 服务器时间: {okx_time['data'][0]['ts']}")
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
            print("建议解决方案:")
            print("1. 检查网络连接")
            print("2. 运行: sudo update-ca-certificates")
            print("3. 临时设置 Config.SSL_VERIFY = False")
            sys.exit(1)

    # ... (保留原有的spot_grid和futures_trend方法)

# ============ 主程序 ============
if __name__ == "__main__":
    print("\n" + "="*50)
    print("OKX量化交易系统 v5.0".center(50))
    print("="*50)
    
    try:
        engine = TradingEngine()
        engine.run()  # 需根据实际实现补充run方法
    except KeyboardInterrupt:
        print("\n🛑 用户终止")
    except Exception as e:
        print(f"\n💥 致命错误: {str(e)}")
        sys.exit(1)
