import json
import os
import time
from typing import Any, Dict, Optional

import requests

from Core.Logger import Logger
from Core.factory.client_factory import ClientFactory

logging = Logger()


class Config:
    """
    配置管理类，负责加载、保存和验证配置
    """
    
    def __init__(self, file_path="./config.json", is_init=False):
        """
        初始化Config类，指定配置文件路径。
        
        Args:
            file_path: 配置文件的路径，默认为当前目录下的config.json
            is_init: 是否仅初始化配置，不执行登录操作
        """
        self.is_init = is_init
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self.gewechat_client = None
        
        # 设置日志文件
        log_dir = os.path.join(os.path.dirname(file_path), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"wxChatBot_{time.strftime('%Y%m%d')}.log")
        logging.set_log_file(log_file)
        self.load()
        # 初始化配置
        self.init_config()

    def init_config(self):
        """
        初始化配置、设置日志级别和获取token
        """
            
        
        # 检查token是否存在，如果不存在则获取
        if not self.data.get('gewechat_token'):
            self._get_token()
    
    def _get_token(self) -> Optional[str]:
        """
        获取gewechat token
        
        Returns:
            Optional[str]: 获取到的token，如果失败则返回None
        """
        url = f"http://{self.data.get('gewe_server_ip')}:2531/v2/api" + "/tools/getTokenId"
            
        try:
            response = requests.post(url, headers={}, data={})
            response.raise_for_status()  # 检查响应状态
            token = response.json()['data']
            logging.warning(f"Token未设置，已自动获取Token: {token}")
            self.set('gewechat_token', token)
            return token
        except requests.RequestException as e:
            logging.error(f"获取Token失败: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logging.error(f"解析Token响应失败: {e}")
            return None

    def load(self):
        """从文件中加载配置数据"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except json.JSONDecodeError as e:
            logging.error(f"加载配置文件时出错: {e}")
        except Exception as e:
            logging.error(f"读取配置文件时出错: {e}")

    def save(self):
        """将当前配置数据保存到文件中"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件时出错: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项的值
        
        Args:
            key: 配置项的键
            default: 如果键不存在时返回的默认值
            
        Returns:
            Any: 配置项的值或默认值
        """
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项的值
        
        Args:
            key: 配置项的键
            value: 配置项的值
        """
        if self.data.get(key) != value:
            self.data[key] = value
            self.save()
            logging.success(f"设置配置项 {key} = {value} 成功")
        else:
            logging.debug(f"配置项 {key} 的值未变化，跳过保存")

    def delete(self, key: str) -> None:
        """
        删除配置项
        
        Args:
            key: 配置项的键
        """
        if key in self.data:
            del self.data[key]
            self.save()
            logging.info(f"已删除配置项: {key}")

    def get_gewechat_client(self):
        """
        获取GewechatClient实例
        使用ClientFactory确保全局只有一个实例
        
        Returns:
            GewechatClient实例
        """
        # 使用工厂获取客户端实例，不自动登录
        client = ClientFactory.get_client(self)
        return client

    def __str__(self) -> str:
        """返回配置数据的字符串表示"""
        return json.dumps(self.data, indent=4, ensure_ascii=False)