import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.VITE_SUPABASE_URL || 'https://jirudzbqcxviytcmxegf.supabase.co';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4';
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method === 'POST') {
    try {
      const formData = req.body;
      
      // 数据验证
      if (!formData.email || !formData.message) {
        return res.status(400).json({
          success: false,
          error: 'Missing required fields',
          message: '邮箱和消息内容是必填项'
        });
      }
      
      // 准备插入数据库的数据
      const inquiryData = {
        name: `${formData.first_name || ''} ${formData.last_name || ''}`.trim(),
        email: formData.email,
        phone: formData.phone || null,
        company: formData.company || null,
        subject: formData.subject || '一般咨询',
        message: formData.message,
        product_interest: formData.product || null,
        country: formData.country || null,
        newsletter: formData.newsletter || false,
        status: 'new',
        created_at: new Date().toISOString()
      };
      
      // 插入到Supabase
      const { data, error } = await supabase
        .from('inquiries')
        .insert([inquiryData])
        .select();
      
      if (error) {
        console.error('Supabase error:', error);
        return res.status(500).json({
          success: false,
          error: 'Database error',
          message: '保存询盘信息时出错，请稍后重试'
        });
      }
      
      res.status(200).json({
        success: true,
        message: '感谢您的咨询！我们会在24小时内回复您。',
        data: data[0]
      });
      
    } catch (error) {
      console.error('Contact form error:', error);
      res.status(500).json({
        success: false,
        error: 'Server error',
        message: '服务器内部错误，请稍后重试'
      });
    }
  } else {
    res.setHeader('Allow', ['POST', 'OPTIONS']);
    res.status(405).json({ 
      success: false,
      error: 'Method not allowed',
      message: '仅支持POST请求'
    });
  }
}
