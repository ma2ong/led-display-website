// Vercel API路由 - Supabase集成
import { SupabaseAPI } from '../lib/supabase.js'

// 产品API
export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const endpoint = searchParams.get('endpoint')
  
  try {
    switch (endpoint) {
      case 'products':
        const products = await SupabaseAPI.getProducts()
        return Response.json({ status: 'success', data: products })
      
      case 'products/featured':
        const featured = await SupabaseAPI.getFeaturedProducts()
        return Response.json({ status: 'success', data: featured })
      
      case 'news/latest':
        const news = await SupabaseAPI.getPublishedNews(3)
        return Response.json({ status: 'success', data: news })
      
      case 'stats':
        const stats = await SupabaseAPI.getStats()
        return Response.json({ status: 'success', data: stats })
      
      case 'health':
        return Response.json({ 
          status: 'success', 
          message: 'Supabase API is running',
          timestamp: new Date().toISOString()
        })
      
      default:
        return Response.json({ status: 'error', message: 'Endpoint not found' }, { status: 404 })
    }
  } catch (error) {
    console.error('API Error:', error)
    return Response.json({ 
      status: 'error', 
      message: error.message 
    }, { status: 500 })
  }
}

export async function POST(request) {
  const { searchParams } = new URL(request.url)
  const endpoint = searchParams.get('endpoint')
  
  try {
    const body = await request.json()
    
    switch (endpoint) {
      case 'contact':
        const inquiry = await SupabaseAPI.createInquiry({
          name: body.name,
          email: body.email,
          phone: body.phone || '',
          company: body.company || '',
          message: body.message
        })
        return Response.json({ 
          status: 'success', 
          message: '询盘提交成功！',
          data: inquiry
        })
      
      case 'newsletter':
        // 这里可以集成邮件服务
        return Response.json({ 
          status: 'success', 
          message: 'Successfully subscribed to newsletter'
        })
      
      case 'products':
        const product = await SupabaseAPI.createProduct(body)
        return Response.json({ 
          status: 'success', 
          message: '产品创建成功！',
          data: product
        })
      
      case 'news':
        const newsItem = await SupabaseAPI.createNews(body)
        return Response.json({ 
          status: 'success', 
          message: '新闻发布成功！',
          data: newsItem
        })
      
      default:
        return Response.json({ status: 'error', message: 'Endpoint not found' }, { status: 404 })
    }
  } catch (error) {
    console.error('API Error:', error)
    return Response.json({ 
      status: 'error', 
      message: error.message 
    }, { status: 500 })
  }
}

export async function PUT(request) {
  const { searchParams } = new URL(request.url)
  const endpoint = searchParams.get('endpoint')
  const id = searchParams.get('id')
  
  try {
    const body = await request.json()
    
    switch (endpoint) {
      case 'products':
        const product = await SupabaseAPI.updateProduct(id, body)
        return Response.json({ 
          status: 'success', 
          message: '产品更新成功！',
          data: product
        })
      
      case 'news':
        const newsItem = await SupabaseAPI.updateNews(id, body)
        return Response.json({ 
          status: 'success', 
          message: '新闻更新成功！',
          data: newsItem
        })
      
      case 'inquiries/status':
        const inquiry = await SupabaseAPI.updateInquiryStatus(id, body.status)
        return Response.json({ 
          status: 'success', 
          message: '询盘状态更新成功！',
          data: inquiry
        })
      
      default:
        return Response.json({ status: 'error', message: 'Endpoint not found' }, { status: 404 })
    }
  } catch (error) {
    console.error('API Error:', error)
    return Response.json({ 
      status: 'error', 
      message: error.message 
    }, { status: 500 })
  }
}

export async function DELETE(request) {
  const { searchParams } = new URL(request.url)
  const endpoint = searchParams.get('endpoint')
  const id = searchParams.get('id')
  
  try {
    switch (endpoint) {
      case 'products':
        await SupabaseAPI.deleteProduct(id)
        return Response.json({ 
          status: 'success', 
          message: '产品删除成功！'
        })
      
      case 'news':
        await SupabaseAPI.deleteNews(id)
        return Response.json({ 
          status: 'success', 
          message: '新闻删除成功！'
        })
      
      default:
        return Response.json({ status: 'error', message: 'Endpoint not found' }, { status: 404 })
    }
  } catch (error) {
    console.error('API Error:', error)
    return Response.json({ 
      status: 'error', 
      message: error.message 
    }, { status: 500 })
  }
}