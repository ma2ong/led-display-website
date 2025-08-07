// Supabase Frontend Integration for LED Website
// This file connects the frontend to Supabase backend

// Supabase configuration
const SUPABASE_URL = 'https://jirudzbqcxviytcmxegf.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcnVkemJxY3h2aXl0Y214ZWdmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTExOTUsImV4cCI6MjA3MDAyNzE5NX0.qi0YhrxQmbRa6YsbVA13IpddImIjJKJyd1fgz5jIlt4'

// Initialize Supabase client
let supabaseClient = null;

// Initialize Supabase when page loads
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Check if Supabase is available
        if (typeof window.supabase !== 'undefined') {
            supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
            console.log('✅ Supabase connected successfully');
            
            // Test connection
            await testSupabaseConnection();
            
            // Load dynamic content
            await loadDynamicContent();
            
        } else {
            console.warn('⚠️ Supabase library not loaded, using fallback');
        }
    } catch (error) {
        console.error('❌ Supabase initialization failed:', error);
    }
});

// Test Supabase connection
async function testSupabaseConnection() {
    try {
        const { data, error } = await supabaseClient
            .from('products')
            .select('count')
            .limit(1);
        
        if (error) throw error;
        
        console.log('✅ Supabase database connection verified');
        
        // Update UI to show connection status
        updateConnectionStatus(true);
        
    } catch (error) {
        console.error('❌ Supabase connection test failed:', error);
        updateConnectionStatus(false);
    }
}

// Update connection status in UI
function updateConnectionStatus(connected) {
    // Add a small indicator to show backend status
    const indicator = document.createElement('div');
    indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        z-index: 9999;
        color: white;
        ${connected ? 'background: #28a745;' : 'background: #dc3545;'}
    `;
    indicator.textContent = connected ? '🟢 Backend Connected' : '🔴 Backend Offline';
    document.body.appendChild(indicator);
    
    // Remove indicator after 3 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.parentNode.removeChild(indicator);
        }
    }, 3000);
}

// Load dynamic content from Supabase
async function loadDynamicContent() {
    if (!supabaseClient) return;
    
    try {
        // Load latest products for homepage
        await loadLatestProducts();
        
        // Load latest news
        await loadLatestNews();
        
        // Update stats
        await updateStats();
        
    } catch (error) {
        console.error('Error loading dynamic content:', error);
    }
}

// Load latest products
async function loadLatestProducts() {
    try {
        const { data: products, error } = await supabaseClient
            .from('products')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(6);
        
        if (error) throw error;
        
        if (products && products.length > 0) {
            console.log(`✅ Loaded ${products.length} products from Supabase`);
            // You can update the product cards here if needed
        }
        
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Load latest news
async function loadLatestNews() {
    try {
        const { data: news, error } = await supabaseClient
            .from('news')
            .select('*')
            .eq('status', 'published')
            .order('created_at', { ascending: false })
            .limit(3);
        
        if (error) throw error;
        
        if (news && news.length > 0) {
            console.log(`✅ Loaded ${news.length} news articles from Supabase`);
        }
        
    } catch (error) {
        console.error('Error loading news:', error);
    }
}

// Update statistics
async function updateStats() {
    try {
        // Get product count
        const { count: productCount } = await supabaseClient
            .from('products')
            .select('*', { count: 'exact', head: true });
        
        // Get inquiry count
        const { count: inquiryCount } = await supabaseClient
            .from('inquiries')
            .select('*', { count: 'exact', head: true });
        
        console.log(`📊 Stats: ${productCount} products, ${inquiryCount} inquiries`);
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Contact form submission to Supabase
async function submitContactForm(formData) {
    if (!supabaseClient) {
        throw new Error('Supabase not initialized');
    }
    
    try {
        const { data, error } = await supabaseClient
            .from('inquiries')
            .insert([{
                name: formData.name,
                email: formData.email,
                phone: formData.phone || null,
                company: formData.company || null,
                message: formData.message,
                status: 'new',
                created_at: new Date().toISOString()
            }])
            .select();
        
        if (error) throw error;
        
        console.log('✅ Contact form submitted to Supabase:', data);
        return { success: true, data };
        
    } catch (error) {
        console.error('❌ Contact form submission failed:', error);
        throw error;
    }
}

// Export functions for global use
window.supabaseFrontend = {
    submitContactForm,
    testConnection: testSupabaseConnection,
    client: () => supabaseClient
};

console.log('🚀 Supabase Frontend Integration loaded');