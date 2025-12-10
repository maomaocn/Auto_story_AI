# 配置模块
class Config:
    """基础配置类"""
    SECRET_KEY = 'a_very_secret_key_for_session'  # 用于会话安全
    # 在实际项目中，这里通常是数据库连接、外部API密钥等
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 启用调试模式，代码更改后自动重启
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 关闭调试模式，提升安全性和性能
# 字典映射，方便 app.py 根据环境名称选择配置
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}