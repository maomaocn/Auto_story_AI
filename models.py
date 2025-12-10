# 数据模型
class TodoItem:
    """待办事项的数据模型类"""
    
    # 模拟数据存储，在实际应用中会是数据库
    # 使用类属性存储所有实例，模拟一个简单的数据库表
    _task=[]
    _next_id=1# 使用类属性自动生成 ID
    def __init__(self, content:str, done:bool=False):
        """
        构造函数 (Constructor)，创建 TodoItem 实例时调用。
        
        知识点：类型提示 (Type Hinting)，增加代码可读性。
        """
        self.id = TodoItem._next_id
        TodoItem._next_id += 1
        self.content = content
        self.done = done
        # 将新创建的任务添加到模拟数据库中
        TodoItem._task.append(self)
    @classmethod
    def get_all(cls):
        """获取所有待办事项"""
        return cls._task
    @classmethod
    def add_task(cls, content:str):
        """添加新的待办事项"""
        return cls(content)
    @classmethod
    def get_by_id(cls, task_id:int):
        """根据 ID 获取待办事项"""
        """查找指定ID的任务"""
        # 知识点：列表推导式 (List Comprehension) 和 next() 函数
        try:
            return next(task for task in cls._tasks if task.id == task_id)
        except StopIteration:
            return None
    @classmethod
    def toggle_done(cls, task_id:int):
        """切换待办事项的完成状态"""
        task = cls.get_by_id(task_id)
        if task:
            task.done = not task.done
            return task
        return None
    