"""
模型管理序列化器
"""
from rest_framework import serializers
from .models import ModelProvider,ModelUsageLog

class ModelProviderListSerializer(serializers.ModelSerializer):
    provider_type_display=serializers.CharField(
        source='get_provider_type_display',
        read_only=True
    )
#SerializerMethodField 的规则（非常重要）
# 规则只有一条：
# 字段名 = xxx
# 方法名 = get_xxx(self, obj)
    #统计信息
    total_usage_count=serializers.SerializerMethodField()
    recent_usage_count=serializers.SerializerMethodField()

    class Meta:
        model=ModelProvider
        fields=[
         'id', 'name', 'provider_type', 'provider_type_display',
            'model_name', 'executor_class', 'is_active', 'priority',
            'total_usage_count', 'recent_usage_count',
            'created_at', 'updated_at'   
        ]
        read_only_fields=['id','created_at','updated_at']
    def get_total_usage_count(self,obj):
        """获取总使用次数"""
        return obj.usage_logs.count()
    
    def get_recent_usage_count(self,obj):
        """获取最近7天使用次数"""
        from django.utils import timezone
        from datetime import timedelta
        seven_day_age=timezone.now()-timedelta(days=7)
        return obj.usage_logs.filter(created_at__gte=seven_day_age).count()
    
class ModelProviderDetailSerializer(serializers.ModelSerializer):
    print("进入ModelProviderDetailSerializer")
    """模型提供商详情序列化器 - 完整信息"""
    provider_type_display=serializers.CharField(
        source='get_provider_type_display',
        read_only=True
    )

    #统计信息
    total_usage_count=serializers.SerializerMethodField()
    success_count=serializers.SerializerMethodField()
    failed_count=serializers.SerializerMethodField()
    success_rate=serializers.SerializerMethodField()
    avg_latency_ms=serializers.SerializerMethodField()
    total_tokens_used=serializers.SerializerMethodField()

    class Meta:
        model=ModelProvider
        fields=[
          'id', 'name', 'provider_type', 'provider_type_display',
            'api_url', 'api_key', 'model_name', 'executor_class',
            # LLM专用参数
            'max_tokens', 'temperature', 'top_p',
            # 通用参数
            'timeout', 'is_active', 'priority',
            # 限流配置
            'rate_limit_rpm', 'rate_limit_rpd',
            # 额外配置
            'extra_config',
            # 统计信息
            'total_usage_count', 'success_count', 'failed_count',
            'success_rate', 'avg_latency_ms', 'total_tokens_used',
            'created_at', 'updated_at'  
        ]
        read_only_fields=['id','created_at','updated_at']

        
    def to_representation(self, instance):
        print("进入to_representation方法",self,instance)
        """隐藏API Key的完整内容"""
        data = super().to_representation(instance)

        # api_key = data.get('api_key')
        # if api_key:
        #     data['api_key'] = f"{api_key[:4]}****{api_key[-4:]}"
        return data
    def get_total_usage_count(self,obj):
        """获取总使用次数"""
        return obj.usage_logs.count()
    def get_success_count(self,obj):
        """获取成功调用次数"""
        return obj.usage_logs.filter(status = 'success').count()
# 这是拿到数据库的数据进行计算，给前端展示的
    def get_failed_count(self,obj):
        """获取失败调用次数"""
        return obj.usage_logs.filter(status = 'failed').count()
    def get_success_rate(self,obj):
        """获取成功率"""
        total=obj.usage_logs.count()
        if total==0:
            return 0.0
        success=obj.usage_logs.filter(status = 'success').count()
        return round((success/total)*100,2)
    def get_avg_latency_ms(self, obj):
        """获取平均延迟"""
        from django.db.models import Avg
        result = obj.usage_logs.aggregate(avg_latency=Avg('latency_ms'))
        return 
    def get_total_tokens_used(self,obj):
        """获取总使用的令牌数"""
        from django.db.models import Sum
        result = obj.usage_logs.aggregate(total_tokens=Sum('tokens_used'))
        return result['total_tokens'] or 0

# 创建的时候需要对字段进行校验
class ModelProviderCreateSerializer(serializers.ModelSerializer):
    """模型提供商创建/更新序列化器"""
    class Meta:
        model=ModelProvider
        fields=[
          'id', 'name', 'provider_type',
            'api_url', 'api_key', 'model_name', 'executor_class',
            # LLM专用参数
            'max_tokens', 'temperature', 'top_p',
            # 通用参数
            'timeout', 'is_active', 'priority',
            # 限流配置
            'rate_limit_rpm', 'rate_limit_rpd',
            # 额外配置
            'extra_config',
            'created_at', 'updated_at'  
        ]
        
    # attrs 是“前端传来的数据”,用来进行校验的
    def validate_api_url(self, value):
        """验证 API URL 格式"""
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError

        value = value.strip()
        if not value:
            raise serializers.ValidationError("API URL不能为空")

        validator = URLValidator(schemes=['http', 'https'])
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("无效的API URL格式")

        return value
    def validate_api_key(self, value):
        """验证 API Key 非空"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("API Key不能为空")
        return value
    
    def validate_temperature(self, value):
        """验证温度参数范围"""
        if value is not None and (value < 0.0 or value > 2.0):
            raise serializers.ValidationError("温度必须在0到2.0之间")
        return value
    def validate_top_p(self, value):
        """验证 Top P 参数范围"""
        if value is not None and (value < 0.0 or value > 1.0):
            raise serializers.ValidationError("Top P必须在0到1.0之间")
        return value
    def validate_priority(self, value):
        """验证优先级非负"""
        if value < 0:
            raise serializers.ValidationError("优先级必须是非负整数")
        return value
    def validate(self, attrs):
        """交叉验证"""
        provider_type = attrs.get('provider_type', None)
        if provider_type=='llm':
            if attrs.get('max_tokens', 0) <=0:
                raise serializers.ValidationError({'max_tokens':"LLM模型必须指定最大令牌数"})
        elif provider_type=='text2image':
             # 文生图模型建议配置extra_config中的图片参数
            extra_config = attrs.get('extra_config', {})
            if not extra_config.get('width') or not extra_config.get('height'):
                # 设置默认值
                if not extra_config.get('width'):
                    extra_config['width'] = 1024
                if not extra_config.get('height'):
                    extra_config['height'] = 1024
                attrs['extra_config'] = extra_config
        elif provider_type == 'image2video':
            # 图生视频模型建议配置extra_config中的视频参数
            extra_config = attrs.get('extra_config', {})
            if not extra_config.get('fps'):
                extra_config['fps'] = 24
            if not extra_config.get('duration'):
                extra_config['duration'] = 5
            attrs['extra_config'] = extra_config
        return attrs
class ModelProviderUpdateSerializer(serializers.ModelSerializer):
    """模型提供商更新序列化器"""
    class Meta:
        model=ModelProvider
        fields=[
          'id', 'name', 'is_active', 'priority',
            # 额外配置
            'extra_config',
            'created_at', 'updated_at'  
        ]
        read_only_fields=['id','created_at','updated_at']

    def validate_api_url(self, value):
        """验证 API URL 格式"""
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError

        value = value.strip()
        if not value:
            raise serializers.ValidationError("API URL不能为空")

        validator = URLValidator(schemes=['http', 'https'])
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("无效的API URL格式")

        return value
    def validate_api_key(self, value):
        """验证 API Key 非空"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("API Key不能为空")
        return value
    
    def validate_temperature(self, value):
        """验证温度参数范围"""
        if value is not None and (value < 0.0 or value > 2.0):
            raise serializers.ValidationError("温度必须在0到2.0之间")
        return value
    def validate_top_p(self, value):
        """验证 Top P 参数范围"""
        if value is not None and (value < 0.0 or value > 1.0):
            raise serializers.ValidationError("Top P必须在0到1.0之间")
        return value
    def validate_priority(self, value):
        """验证优先级非负"""
        if value < 0:
            raise serializers.ValidationError("优先级必须是非负整数")
        return value



class ModelProviderSimpleSerializer(serializers.ModelSerializer):
    """模型提供商简化序列化器 - 仅返回id和name,用于下拉选择"""

    class Meta:
        model = ModelProvider
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']
class ModelUsageLogSerializer(serializers.ModelSerializer):
    """模型使用日志序列化器"""

    model_provider_name = serializers.CharField(
        source='model_provider.name',
        read_only=True
    )
    model_provider_type = serializers.CharField(
        source='model_provider.provider_type',
        read_only=True
    )

    class Meta:
        model = ModelUsageLog
        fields = [
            'id', 'model_provider', 'model_provider_name', 'model_provider_type',
            'request_data', 'response_data',
            'tokens_used', 'latency_ms', 'status', 'error_message',
            'project_id', 'stage_type',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ModelProviderTestSerializer(serializers.Serializer):
    """模型提供商测试连接序列化器"""
    test_prompt=serializers.CharField(
        required=False,
        default="Hello, world!",
        help_text="用于测试模型提供商连接的提示语"
    )
    def validate(self, attrs):
        """验证模型提供商配置"""
        provider_id=self.context.get('provider_id')
        if not provider_id:
            raise serializers.ValidationError("缺少模型提供商ID")
        try:
            provider=ModelProvider.objects.get(id=provider_id)
        except ModelProvider.DoesNotExist:
            raise serializers.ValidationError("模型提供商不存在")
        if not provider.is_active:
            raise serializers.ValidationError("模型提供商未激活")
        attrs['provider']=provider
        return attrs