export default function handler(req, res) {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  if (req.method === 'GET') {
    res.status(200).json({
      status: 'ok',
      message: 'API服务正常运行',
      timestamp: new Date().toISOString(),
      version: '2.0.0'
    });
  } else {
    res.setHeader('Allow', ['GET', 'OPTIONS']);
    res.status(405).json({ 
      error: 'Method not allowed',
      message: '仅支持GET请求'
    });
  }
}
