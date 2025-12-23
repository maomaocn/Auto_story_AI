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
        """隐藏API Key的完整内容"""
        data = super().to_representation(instance)

        # api_key = data.get('api_key')
        # if api_key:
        #     data['api_key'] = f"{api_key[:4]}****{api_key[-4:]}"
        return data

