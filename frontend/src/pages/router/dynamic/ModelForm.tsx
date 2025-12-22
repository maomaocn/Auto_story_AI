import React, { useEffect, useState } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Typography,
  Divider,
  Row,
  Col,
  message,
} from 'antd';

interface ModelFormModalProps {
  open: boolean;
  editingData: any; // 如果为 null 则为添加模式
  onCancel: () => void;
  onSuccess: () => void;
}

const ModelFormModal: React.FC<ModelFormModalProps> = ({ open, editingData, onCancel, onSuccess }) => {
  const [form] = Form.useForm();
  const { Text } = Typography; // 必须进行解构
  const [submitting, setSubmitting] = useState(false);
  const [providerType, setProviderType] = useState<string>('');

  const isEdit = !!editingData;

  // 监听打开和数据变化
  useEffect(() => {
    if (open) {
      if (editingData) {
        setProviderType(editingData.provider_type);
        form.setFieldsValue({
          ...editingData,
          ...editingData.extra_config,
        });
      } else {
        form.resetFields();
        setProviderType('');
      }
    }
  }, [open, editingData, form]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      
      // 数据结构转换：组装 extra_config
      const { width, height, fps, duration, ...baseData } = values;
      const submitData = {
        ...baseData,
        extra_config: { width, height, fps, duration },
      };

      // 模拟 API 调用
      console.log('Submitting data:', submitData);
      message.success(isEdit ? '更新成功' : '创建成功');
      
      onSuccess(); // 通知父组件刷新
    } catch (error) {
      // 校验失败
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={isEdit ? "编辑模型" : "添加模型"}
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      confirmLoading={submitting}
      width={800}
      maskClosable={false}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          max_tokens: 2000,
          temperature: 0.7,
          top_p: 1.0,
          timeout: 60,
          is_active: true,
          priority: 0,
        }}
        style={{ marginTop: 16 }}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item label="模型名称" name="name" rules={[{ required: true }]}>
              <Input placeholder="例如: GPT-4" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="模型类型" name="provider_type" rules={[{ required: true }]}>
              <Select
                disabled={isEdit}
                onChange={(val) => setProviderType(val)}
                options={[
                  { label: 'LLM模型', value: 'llm' },
                  { label: '文生图', value: 'text2image' },
                  { label: '图生视频', value: 'image2video' },
                ]}
              />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item label="API地址" name="api_url" rules={[{ required: true, type: 'url' }]}>
          <Input placeholder="https://api.example.com" />
        </Form.Item>

        <Form.Item label="API密钥" name="api_key" rules={[{ required: true }]}>
          <Input.Password placeholder="sk-..." />
        </Form.Item>

        {/* 动态参数部分 */}
        {providerType === 'llm' && (
          <div style={{ background: '#f5f5f5', padding: '12px', marginBottom: '16px', borderRadius: '8px' }}>
            <Text type="secondary">LLM 参数</Text>
            <Row gutter={12} style={{ marginTop: 8 }}>
              <Col span={8}><Form.Item label="Tokens" name="max_tokens"><InputNumber style={{ width: '100%' }} /></Form.Item></Col>
              <Col span={8}><Form.Item label="温度" name="temperature"><InputNumber step={0.1} style={{ width: '100%' }} /></Form.Item></Col>
              <Col span={8}><Form.Item label="Top P" name="top_p"><InputNumber step={0.1} style={{ width: '100%' }} /></Form.Item></Col>
            </Row>
          </div>
        )}

        {/* 通用配置 */}
        <Divider plain>高级配置</Divider>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item label="优先级" name="priority">
              <InputNumber style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="状态" name="is_active" valuePropName="checked">
              <Switch checkedChildren="开" unCheckedChildren="关" />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="超时(秒)" name="timeout">
              <InputNumber style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default ModelFormModal;