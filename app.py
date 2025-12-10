# app.py

from flask import Flask
from config import config_map # 导入配置字典
from todo.routes import todo_bp # 导入蓝图

def create_app(config_name='default'):
    """
    应用工厂函数：创建和配置 Flask 实例。
    
    知识点：函数的默认参数 (config_name='default')。
    """
    app = Flask(__name__)
    
    # 知识点：app.config.from_object() 从对象加载配置
    # 获取配置类并加载配置
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 注册蓝图
    # url_prefix='/todo' 可以设置蓝图的基 URL，这里我们让它从根目录开始
    app.register_blueprint(todo_bp) 

    return app

# 应用启动入口
if __name__ == '__main__':
    # 调用工厂函数创建应用，默认使用开发环境配置
    app = create_app('development') 
    app.run()