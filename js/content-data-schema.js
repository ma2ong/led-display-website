/**
 * 网站内容数据结构定义
 * 用于后台编辑和前端显示的统一数据格式
 */

// 默认首页数据
const defaultIndexPageData = {
    page: 'index',
    lastModified: new Date().toISOString(),

    // Hero 轮播图区域
    hero: {
        slides: [
            {
                id: 'hero-1',
                image: 'assets/hero/slide-1.jpg',
                title: 'Professional LED Display Solutions',
                subtitle: 'Leading provider of high-quality LED displays for indoor, outdoor, and rental applications worldwide',
                buttonText: 'View Products',
                buttonLink: 'products.html',
                order: 1
            },
            {
                id: 'hero-2',
                image: 'assets/hero/slide-2.jpg',
                title: 'Innovative Display Technology',
                subtitle: 'Cutting-edge LED solutions for your business needs',
                buttonText: 'Learn More',
                buttonLink: 'about.html',
                order: 2
            },
            {
                id: 'hero-3',
                image: 'assets/hero/slide-3.jpg',
                title: 'Global LED Display Partner',
                subtitle: '17 years of excellence in LED display manufacturing',
                buttonText: 'Contact Us',
                buttonLink: 'contact.html',
                order: 3
            }
        ]
    },

    // 产品展示区域
    products: {
        sectionTitle: 'Our LED Display Solutions',
        sectionSubtitle: 'Comprehensive range of professional LED displays for every application',
        showMore: true,
        items: [
            {
                id: 'indoor-p25',
                name: 'Indoor LED Display P2.5',
                image: 'assets/products/indoor-p2.5.jpg',
                category: 'indoor',
                description: 'High-resolution indoor LED displays perfect for retail stores, corporate offices, conference rooms, and entertainment venues.',
                features: [
                    'Ultra-fine pixel pitch',
                    'Seamless splicing technology',
                    'Front and rear service access',
                    'High refresh rate'
                ],
                link: 'products.html#indoor',
                order: 1
            },
            {
                id: 'outdoor-p10',
                name: 'Outdoor LED Display P10',
                image: 'assets/products/outdoor-p10.jpg',
                category: 'outdoor',
                description: 'Weather-resistant outdoor LED displays designed for advertising billboards, sports stadiums, and public information systems.',
                features: [
                    'High brightness up to 10,000 nits',
                    'IP65/IP67 waterproof rating',
                    'Anti-UV and corrosion resistant',
                    'Temperature range: -40°C to +60°C'
                ],
                link: 'products.html#outdoor',
                order: 2
            },
            {
                id: 'rental-p391',
                name: 'Rental LED Display P3.91',
                image: 'assets/products/rental-p3.91.jpg',
                category: 'rental',
                description: 'Flexible and portable rental LED displays perfect for events, concerts, conferences, and temporary installations.',
                features: [
                    'Lightweight aluminum cabinet design',
                    'Quick lock system for fast setup',
                    'Flight case packaging included',
                    'Tool-free assembly'
                ],
                link: 'products.html#rental',
                order: 3
            },
            {
                id: 'transparent',
                name: 'Transparent LED Display',
                image: 'assets/products/transparent-led.jpg',
                category: 'transparent',
                description: 'Innovative transparent LED displays that maintain visibility while displaying content, perfect for retail windows and glass facades.',
                features: [
                    '70-90% transparency rate',
                    'Ultra-lightweight design (12kg/m²)',
                    'Easy maintenance from front/back',
                    'Energy-efficient LED technology'
                ],
                link: 'products.html#transparent',
                order: 4
            },
            {
                id: 'creative',
                name: 'Creative LED Display',
                image: 'assets/products/creative-led.jpg',
                category: 'creative',
                description: 'Custom-shaped LED displays including curved, spherical, and irregular shapes for unique architectural applications.',
                features: [
                    '360° cylindrical displays',
                    'Flexible and bendable modules',
                    'Custom shapes and sizes',
                    'Interactive touch capabilities'
                ],
                link: 'products.html#creative',
                order: 5
            },
            {
                id: 'fine-pitch',
                name: 'Fine Pitch LED Display',
                image: 'assets/products/fine-pitch.jpg',
                category: 'fine-pitch',
                description: 'Ultra-high resolution fine pitch LED displays for close viewing applications such as broadcast studios and command centers.',
                features: [
                    'P0.9, P1.2, P1.5 pixel pitch options',
                    'Ultra-high resolution and clarity',
                    'Flicker-free technology',
                    'Wide color gamut support'
                ],
                link: 'products.html#fine-pitch',
                order: 6
            }
        ]
    },

    // 公司优势区域
    advantages: {
        sectionTitle: 'Why Choose Us',
        items: [
            {
                icon: 'fa-trophy',
                title: '17+ Years Experience',
                description: 'Industry-leading expertise in LED display manufacturing'
            },
            {
                icon: 'fa-globe',
                title: 'Global Presence',
                description: 'Serving clients in over 50 countries worldwide'
            },
            {
                icon: 'fa-certificate',
                title: 'Quality Certified',
                description: 'ISO9001, CE, RoHS, FCC certified products'
            },
            {
                icon: 'fa-headset',
                title: '24/7 Support',
                description: 'Dedicated technical support team always ready to help'
            }
        ]
    },

    // CTA 区域
    cta: {
        title: 'Ready to Transform Your Space?',
        subtitle: 'Contact us today for a free consultation and quote',
        buttonText: 'Get Started',
        buttonLink: 'contact.html',
        backgroundImage: 'assets/cta-bg.jpg'
    }
}

// 默认产品中心数据
const defaultProductsPageData = {
    page: 'products',
    lastModified: new Date().toISOString(),

    hero: {
        title: 'LED Display Products',
        subtitle: 'Professional display solutions for every need',
        backgroundImage: 'assets/products-hero.jpg'
    },

    categories: [
        {
            id: 'indoor',
            name: 'Indoor LED Displays',
            description: 'High-resolution displays for indoor environments',
            icon: 'fas fa-tv',
            order: 1,
            products: [
                {
                    id: 'indoor-p25',
                    name: 'Indoor P2.5',
                    mainImage: 'assets/products/indoor-p25-main.jpg',
                    gallery: [
                        'assets/products/indoor-p25-detail-1.jpg',
                        'assets/products/indoor-p25-detail-2.jpg',
                        'assets/products/indoor-p25-detail-3.jpg'
                    ],
                    description: 'High-resolution indoor LED displays perfect for retail stores, corporate offices, conference rooms, and entertainment venues. Features ultra-fine pixel pitch and seamless splicing technology.',
                    specifications: {
                        pixelPitch: '2.5mm',
                        brightness: '800cd/㎡',
                        refreshRate: '3840Hz',
                        viewingAngle: '140°/140°',
                        lifespan: '100,000 hours',
                        powerConsumption: '350W/㎡'
                    },
                    features: [
                        'Ultra-fine pixel pitch for sharp images',
                        'Seamless splicing technology',
                        'Front and rear service access',
                        'High refresh rate 3840Hz'
                    ],
                    applications: ['Retail', 'Corporate', 'Conference', 'Entertainment'],
                    order: 1
                }
            ]
        },
        {
            id: 'outdoor',
            name: 'Outdoor LED Displays',
            description: 'Weather-resistant displays for outdoor advertising',
            icon: 'fas fa-sun',
            order: 2,
            products: [
                {
                    id: 'outdoor-p10',
                    name: 'Outdoor P10',
                    mainImage: 'assets/products/outdoor-p10-main.jpg',
                    gallery: [
                        'assets/products/outdoor-p10-detail-1.jpg',
                        'assets/products/outdoor-p10-detail-2.jpg'
                    ],
                    description: 'Weather-resistant outdoor LED displays designed for advertising billboards, sports stadiums, and public information systems. IP65/IP67 waterproof rating.',
                    specifications: {
                        pixelPitch: '10mm',
                        brightness: '10,000cd/㎡',
                        refreshRate: '1920Hz',
                        viewingAngle: '120°/120°',
                        ipRating: 'IP65/IP67',
                        temperatureRange: '-40°C to +60°C'
                    },
                    features: [
                        'High brightness up to 10,000 nits',
                        'IP65/IP67 waterproof rating',
                        'Anti-UV and corrosion resistant',
                        'Temperature range: -40°C to +60°C'
                    ],
                    applications: ['Advertising', 'Sports Stadiums', 'Public Information', 'Transportation'],
                    order: 1
                }
            ]
        },
        {
            id: 'rental',
            name: 'Rental LED Displays',
            description: 'Portable displays for events and temporary installations',
            icon: 'fas fa-magic',
            order: 3,
            products: [
                {
                    id: 'rental-p391',
                    name: 'Rental P3.91',
                    mainImage: 'assets/products/rental-p391-main.jpg',
                    gallery: [
                        'assets/products/rental-p391-detail-1.jpg',
                        'assets/products/rental-p391-detail-2.jpg'
                    ],
                    description: 'Flexible and portable rental LED displays perfect for events, concerts, conferences, and temporary installations. Lightweight aluminum cabinet with quick lock system.',
                    specifications: {
                        pixelPitch: '3.91mm',
                        brightness: '5000cd/㎡',
                        refreshRate: '3840Hz',
                        viewingAngle: '140°/140°',
                        weight: '8kg/cabinet',
                        cabinetSize: '500x500mm'
                    },
                    features: [
                        'Lightweight aluminum cabinet design',
                        'Quick lock system for fast setup',
                        'Flight case packaging included',
                        'Tool-free assembly'
                    ],
                    applications: ['Concerts', 'Events', 'Conferences', 'Stage Performances'],
                    order: 1
                }
            ]
        },
        {
            id: 'transparent',
            name: 'Transparent LED Displays',
            description: 'Innovative transparent displays for retail and architecture',
            icon: 'fas fa-eye',
            order: 4,
            products: [
                {
                    id: 'transparent-led',
                    name: 'Transparent LED Display',
                    mainImage: 'assets/products/transparent-led-main.jpg',
                    gallery: [
                        'assets/products/transparent-led-detail-1.jpg',
                        'assets/products/transparent-led-detail-2.jpg'
                    ],
                    description: 'Innovative transparent LED displays that maintain visibility while displaying content, perfect for retail windows and glass facades. 70-90% transparency rate.',
                    specifications: {
                        transparency: '70-90%',
                        brightness: '5000cd/㎡',
                        pixelPitch: '10-20mm',
                        weight: '12kg/㎡',
                        viewingAngle: '140°/140°'
                    },
                    features: [
                        '70-90% transparency rate',
                        'Ultra-lightweight design (12kg/m²)',
                        'Easy maintenance from front/back',
                        'Energy-efficient LED technology'
                    ],
                    applications: ['Retail Windows', 'Glass Facades', 'Shopping Malls', 'Museums'],
                    order: 1
                }
            ]
        },
        {
            id: 'creative',
            name: 'Creative LED Displays',
            description: 'Custom-shaped displays for unique applications',
            icon: 'fas fa-palette',
            order: 5,
            products: [
                {
                    id: 'creative-led',
                    name: 'Creative LED Display',
                    mainImage: 'assets/products/creative-led-main.jpg',
                    gallery: [
                        'assets/products/creative-led-detail-1.jpg',
                        'assets/products/creative-led-detail-2.jpg'
                    ],
                    description: 'Custom-shaped LED displays including curved, spherical, and irregular shapes for unique architectural applications. Flexible and bendable modules.',
                    specifications: {
                        pixelPitch: '3-10mm',
                        brightness: '5000cd/㎡',
                        flexibility: '360° bending',
                        customization: 'Any shape possible'
                    },
                    features: [
                        '360° cylindrical displays',
                        'Flexible and bendable modules',
                        'Custom shapes and sizes',
                        'Interactive touch capabilities'
                    ],
                    applications: ['Architecture', 'Art Installations', 'Museums', 'Brand Experiences'],
                    order: 1
                }
            ]
        },
        {
            id: 'fine-pitch',
            name: 'Fine Pitch LED Displays',
            description: 'Ultra-high resolution displays for close viewing',
            icon: 'fas fa-microscope',
            order: 6,
            products: [
                {
                    id: 'fine-pitch-p09',
                    name: 'Fine Pitch P0.9',
                    mainImage: 'assets/products/fine-pitch-p09-main.jpg',
                    gallery: [
                        'assets/products/fine-pitch-p09-detail-1.jpg',
                        'assets/products/fine-pitch-p09-detail-2.jpg'
                    ],
                    description: 'Ultra-high resolution fine pitch LED displays for close viewing applications such as broadcast studios and command centers. P0.9, P1.2, P1.5 pixel pitch options.',
                    specifications: {
                        pixelPitch: '0.9mm / 1.2mm / 1.5mm',
                        brightness: '600cd/㎡',
                        refreshRate: '3840Hz',
                        viewingAngle: '160°/160°',
                        colorGamut: '110% NTSC'
                    },
                    features: [
                        'P0.9, P1.2, P1.5 pixel pitch options',
                        'Ultra-high resolution and clarity',
                        'Flicker-free technology',
                        'Wide color gamut support'
                    ],
                    applications: ['Broadcast Studios', 'Command Centers', 'Control Rooms', 'High-end Retail'],
                    order: 1
                }
            ]
        }
    ]
}

// 默认关于我们数据
const defaultAboutPageData = {
    page: 'about',
    lastModified: new Date().toISOString(),

    hero: {
        title: 'About Lianjin LED',
        subtitle: '17 Years of Excellence in LED Display Manufacturing',
        image: 'assets/about-hero.jpg'
    },

    company: {
        introduction: 'Company introduction text...',
        images: [
            { id: 'building', url: 'assets/about/building.jpg', caption: 'Our Headquarters' },
            { id: 'factory', url: 'assets/about/factory.jpg', caption: 'Production Facility' }
        ]
    },

    team: {
        sectionTitle: 'Our Leadership Team',
        members: [
            {
                id: 'ceo',
                name: 'John Doe',
                position: 'CEO & Founder',
                image: 'assets/team/ceo.jpg',
                bio: 'Brief bio...'
            }
        ]
    },

    certificates: {
        sectionTitle: 'Certifications & Awards',
        items: [
            { id: 'iso', name: 'ISO 9001', image: 'assets/certificates/iso.jpg' },
            { id: 'ce', name: 'CE Certification', image: 'assets/certificates/ce.jpg' }
        ]
    }
}

// 工具函数：保存页面数据
function savePageData(pageId, data) {
    const key = `page_data_${pageId}`
    data.lastModified = new Date().toISOString()
    localStorage.setItem(key, JSON.stringify(data))
    console.log(`✅ 保存页面数据: ${pageId}`, data)
    return true
}

// 工具函数：加载页面数据
function loadPageData(pageId) {
    const key = `page_data_${pageId}`
    const stored = localStorage.getItem(key)

    if (stored) {
        try {
            const data = JSON.parse(stored)
            console.log(`✅ 加载页面数据: ${pageId}`, data)
            return data
        } catch (error) {
            console.error(`❌ 解析页面数据失败: ${pageId}`, error)
        }
    }

    // 返回默认数据
    console.log(`📋 使用默认数据: ${pageId}`)
    switch(pageId) {
        case 'index':
            return defaultIndexPageData
        case 'products':
            return defaultProductsPageData
        case 'about':
            return defaultAboutPageData
        default:
            return {}
    }
}

// 工具函数：初始化默认数据
function initializeDefaultData() {
    if (!localStorage.getItem('page_data_index')) {
        savePageData('index', defaultIndexPageData)
    }
    if (!localStorage.getItem('page_data_products')) {
        savePageData('products', defaultProductsPageData)
    }
    if (!localStorage.getItem('page_data_about')) {
        savePageData('about', defaultAboutPageData)
    }
    console.log('✅ 默认数据初始化完成')
}

// 如果在浏览器环境，初始化
if (typeof window !== 'undefined') {
    window.savePageData = savePageData
    window.loadPageData = loadPageData
    window.initializeDefaultData = initializeDefaultData
}
