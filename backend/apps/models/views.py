from asgiref.sync import async_to_sync
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ModelUsageLog,ModelProvider
from rest_framework.decorators import action
from django.db.models import Value, CharField, IntegerField
from .serializers import (
    ModelProviderListSerializer,
    ModelProviderDetailSerializer,
    ModelProviderCreateSerializer,
    ModelProviderUpdateSerializer,
    ModelUsageLogSerializer,
    ModelProviderTestSerializer,
    ModelProviderSimpleSerializer,
)
from .services import ModelProviderService
class ModelProviderViewSet(viewsets.ModelViewSet):
    
    """
    模型使用日志视图集
    提供模型使用日志的增删改查接口
    """

    def get_queryset(self):
        """获取所有模型提供商"""
        return ModelProvider.objects.all().prefetch_related('usage_logs')
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if(self.action=='list'):
            return ModelProviderListSerializer
        elif self.action=='retrieve':
            return ModelProviderDetailSerializer
        elif self.action=='create':
            return ModelProviderCreateSerializer
        elif self.action in ['update','partial_update']:
            return ModelProviderUpdateSerializer
        return ModelProviderDetailSerializer

    def create(self, request, *args, **kwargs):
        """创建模型提供商"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        provider=ModelProviderService.create_provider(serializer.validated_data)
        print(provider)
        response_serializer=ModelProviderDetailSerializer(provider)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    def list(self, request, *args, **kwargs):
    # 1. 调用你原来的 get_queryset 获取数据
        queryset = self.get_queryset()
    # 2. 序列化数据
        serializer = self.get_serializer(queryset, many=True)
    # 3. 返回你自定义的结构
        return Response({
            "code": "200",
            "success": True,
            "message": "获取模型提供商成功",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        测试模型提供商连接
        POST /api/v1/models/providers/{id}/test-connection/
        Body: {"test_prompt": "Hello, this is a test."}
        """
        instance = self.get_object()
        serializer = ModelProviderTestSerializer(
            data=request.data,
            context={'provider_id': str(instance.id)}
        )
        serializer.is_valid(raise_exception=True)

        test_prompt = serializer.validated_data.get(
            'test_prompt',
            'Hello, this is a test.'
        )

        # 异步测试转同步执行
        result = async_to_sync(ModelProviderService.test_provider_connection)(
            str(instance.id),
            test_prompt
        )

        if result['success']:
            return Response({
                'success': True,
                'message': '连接测试成功',
                'latency_ms': result['latency_ms'],
                'response': result.get('response'),
                'data': result.get('data', {})
            })
        else:
            return Response({
                'success': False,
                'message': '连接测试失败',
                'error': result.get('error'),
                'latency_ms': result.get('latency_ms', 0)
            }, status=status.HTTP_400_BAD_REQUEST)

    

class ModelUsageLogViewSet(viewsets.ModelViewSet):
    """
    模型使用日志视图集
    提供模型使用日志的增删改查接口
    """
    queryset = ModelUsageLog.objects.all()
    serializer_class = ModelUsageLogSerializer

    def get_queryset(self):
        """
        根据请求参数过滤查询集
        支持按模型提供商ID和项目ID过滤
        """
        queryset = super().get_queryset()
        provider_id = self.request.query_params.get('provider_id')
        project_id = self.request.query_params.get('project_id')
        if provider_id:
            queryset = queryset.filter(model_provider_id=provider_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset