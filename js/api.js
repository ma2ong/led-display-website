import supabase from '../lib/supabase.js';

/**
 * 产品API服务
 */
export const productApi = {
  /**
   * 获取所有产品
   * @returns {Promise} 包含产品数据的Promise
   */
  getAllProducts: async () => {
    try {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .order('id');
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('获取产品列表失败:', error);
      throw error;
    }
  },

  /**
   * 按类别获取产品
   * @param {string} category - 产品类别
   * @returns {Promise} 包含产品数据的Promise
   */
  getProductsByCategory: async (category) => {
    try {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('category', category)
        .order('id');
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error(`获取${category}类别产品失败:`, error);
      throw error;
    }
  },

  /**
   * 获取单个产品详情
   * @param {number} id - 产品ID
   * @returns {Promise} 包含产品数据的Promise
   */
  getProductById: async (id) => {
    try {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('id', id)
        .single();
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error(`获取产品ID=${id}详情失败:`, error);
      throw error;
    }
  }
};

/**
 * 新闻API服务
 */
export const newsApi = {
  /**
   * 获取所有新闻
   * @returns {Promise} 包含新闻数据的Promise
   */
  getAllNews: async () => {
    try {
      const { data, error } = await supabase
        .from('news')
        .select('*')
        .eq('status', 'published')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('获取新闻列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取单个新闻详情
   * @param {number} id - 新闻ID
   * @returns {Promise} 包含新闻数据的Promise
   */
  getNewsById: async (id) => {
    try {
      const { data, error } = await supabase
        .from('news')
        .select('*')
        .eq('id', id)
        .single();
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error(`获取新闻ID=${id}详情失败:`, error);
      throw error;
    }
  }
};

/**
 * 联系表单API服务
 */
export const contactApi = {
  /**
   * 提交联系表单
   * @param {Object} formData - 表单数据
   * @returns {Promise} 包含提交结果的Promise
   */
  submitInquiry: async (formData) => {
    try {
      const { data, error } = await supabase
        .from('inquiries')
        .insert([formData])
        .select();
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('提交联系表单失败:', error);
      throw error;
    }
  }
};

/**
 * 认证API服务
 */
export const authApi = {
  /**
   * 用户登录
   * @param {string} email - 用户邮箱
   * @param {string} password - 用户密码
   * @returns {Promise} 包含登录结果的Promise
   */
  signIn: async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('登录失败:', error);
      throw error;
    }
  },

  /**
   * 用户注册
   * @param {string} email - 用户邮箱
   * @param {string} password - 用户密码
   * @returns {Promise} 包含注册结果的Promise
   */
  signUp: async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password
      });
      
      if (error) throw error;
      return data;
    } catch (error) {
      console.error('注册失败:', error);
      throw error;
    }
  },

  /**
   * 用户登出
   * @returns {Promise} 包含登出结果的Promise
   */
  signOut: async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      return true;
    } catch (error) {
      console.error('登出失败:', error);
      throw error;
    }
  },

  /**
   * 获取当前用户
   * @returns {Promise} 包含用户数据的Promise
   */
  getCurrentUser: async () => {
    try {
      const { data, error } = await supabase.auth.getUser();
      if (error) throw error;
      return data.user;
    } catch (error) {
      console.error('获取当前用户失败:', error);
      return null;
    }
  }
};