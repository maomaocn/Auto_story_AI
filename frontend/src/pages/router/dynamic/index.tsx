import React, { useEffect, useState, useMemo } from 'react';
import { 
  Table, 
  Card, 
  Button, 
  Input, 
  Select, 
  Space, 
  Tag, 
  Tooltip, 
  message, 
  Modal, 
  Typography 
} from 'antd';
import { 
  PlusOutlined, 
  SearchOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SwapOutlined
} from '@ant-design/icons';
import ModelFormModal from './ModelForm';
import {httpGetModels} from './API';
const { Text } = Typography;

const ModelList: React.FC = () => {
  // const dispatch = useAppDispatch();
  
  // 模拟从 Redux 获取状态
  // const { providers, loading } = useAppSelector(state => state.models);
  const [providers, setProviders] = useState<any[]>([]); 
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);

  // 筛选状态
  const [filters, setFilters] = useState({
    search: '',
    provider_type: '',
    is_active: '' as string | boolean
  });
  const [modalVisible, setModalVisible] = useState(false);
  const [editingData, setEditingData] = useState<any>(null);

  // 打开添加弹窗
  const showAddModal = () => {
    setEditingData(null);
    setModalVisible(true);
  };

  // 打开编辑弹窗
  const showEditModal = (record: any) => {
    setEditingData(record);
    setModalVisible(true);
  };

  const handleModalSuccess = () => {
    setModalVisible(false);

    // 重新加载列表数据
    // fetchData(); 
  };
  // 初始化加载
  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async (currentFilters = filters) => {
    setLoading(true);
      const params: any = {};
      if (currentFilters.search) params.search = currentFilters.search;
      if (currentFilters.provider_type) params.provider_type = currentFilters.provider_type;
      if (currentFilters.is_active !== '') params.is_active = currentFilters.is_active === 'true';
      
     const res= await httpGetModels();
     if(res.status===200){
      setLoading(false);
      setProviders(res.data.data || []);
     }else{
      message.error('加载模型列表失败');
      setLoading(false);
     }
  };

  // 处理操作逻辑
  const handleToggleStatus = async (record: any) => {
    try {
      // await dispatch(toggleProviderStatus(record.id));
      message.success(`模型已${record.is_active ? '停用' : '启用'}`);
    } catch (error) {
      message.error('切换状态失败');
    }
  };

  const handleTest = async (record: any) => {
    setTesting(true);
    try {
      // const result = await dispatch(testProviderConnection({ id: record.id, ... }));
      const result = { success: true, latency_ms: 120 }; // 模拟数据
      if (result.success) {
        Modal.success({ title: '测试成功', content: `响应延迟: ${result.latency_ms}ms` });
      }
    } finally {
      setTesting(false);
    }
  };

  const handleDelete = (record: any) => {
    Modal.confirm({
      title: '确定要删除模型吗？',
      content: `模型名称: ${record.name}`,
      okText: '删除',
      okType: 'danger',
      onOk: async () => {
        // await dispatch(deleteProvider(record.id));
        message.success('删除成功');
      }
    });
  };

  // 表格列定义
  const columns = [
    {
      title: '模型名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '类型',
      dataIndex: 'provider_type',
      key: 'provider_type',
      render: (type: string) => {
        const config: any = {
          llm: { label: 'LLM', color: 'blue' },
          text2image: { label: '文生图', color: 'purple' },
          image2video: { label: '图生视频', color: 'cyan' },
        };
        const item = config[type] || { label: type, color: 'default' };
        return <Tag color={item.color}>{item.label}</Tag>;
      },
    },
    {
      title: '模型',
      dataIndex: 'model_name',
      key: 'model_name',
      ellipsis: true,
      render: (text: string) => <Tooltip title={text}>{text}</Tooltip>,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      align: 'center' as const,
      render: (val: number) => <Tag bordered={false}>{val}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? '已激活' : '未激活'}
        </Tag>
      ),
    },
    {
      title: '使用次数',
      key: 'usage',
      render: (_: any, record: any) => (
        <div style={{ fontSize: '12px' }}>
          <div>总计: {record.total_usage_count || 0}</div>
          <Text type="secondary">近7天: {record.recent_usage_count || 0}</Text>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button 
            type="link" 
            size="small" 
            disabled={!record.is_active || testing}
            onClick={() => handleTest(record)}
          >
            测试
          </Button>
          <Button 
            type="link" 
            size="small" 
            icon={<SwapOutlined />} 
            onClick={() => handleToggleStatus(record)}
          >
            {record.is_active ? '停用' : '启用'}
          </Button>
          <Button 
            type="link" 
            size="small" 
            icon={<EditOutlined />} 
            onClick={() => navigate(`/models/edit/${record.id}`)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            size="small" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
     <Card 
        title="模型管理" 
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={showAddModal}>添加模型</Button>}
      >
        {/* 筛选区域 */}
        <div style={{ marginBottom: 24 }}>
          <Space wrap>
            <Input
              placeholder="搜索模型名称"
              prefix={<SearchOutlined />}
              style={{ width: 200 }}
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              onPressEnter={() => loadProviders()}
            />
            <Select
              placeholder="全部类型"
              style={{ width: 150 }}
              allowClear
              onChange={(val) => {
                const newFilters = { ...filters, provider_type: val };
                setFilters(newFilters);
                loadProviders(newFilters);
              }}
            >
              <Select.Option value="llm">LLM模型</Select.Option>
              <Select.Option value="text2image">文生图模型</Select.Option>
              <Select.Option value="image2video">图生视频模型</Select.Option>
            </Select>
            <Select
              placeholder="全部状态"
              style={{ width: 120 }}
              allowClear
              onChange={(val) => {
                const newFilters = { ...filters, is_active: val };
                setFilters(newFilters);
                loadProviders(newFilters);
              }}
            >
              <Select.Option value="true">已激活</Select.Option>
              <Select.Option value="false">未激活</Select.Option>
            </Select>
            <Button type="primary" onClick={() => loadProviders()}>查询</Button>
          </Space>
        </div>

        {/* 表格区域 */}
        <Table
          columns={columns}
          dataSource={providers}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条数据`,
          }}
        />
      </Card>
      <ModelFormModal
        open={modalVisible}
        editingData={editingData}
        onCancel={() => setModalVisible(false)}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
};

export default ModelList;