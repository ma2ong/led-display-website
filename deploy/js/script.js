// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeHeroSlider();
    initializeNavigation();
    initializeLanguageSwitcher();
    initializeModals();
    initializeTabs();
    initializeCaseFilter();
    initializeContactForm();
    initializeQuoteForm();
    initializeScrollEffects();
    initializeCounters();
    initializeAOS();
    
    // Initialize back to top button
    initializeBackToTop();
    
    // Initialize search functionality
    initializeSearch();
    initializeProductComparison();
    initializeLazyLoading();
});

// Hero Slider
function initializeHeroSlider() {
    const slides = document.querySelectorAll('.hero-slide');
    const indicators = document.querySelectorAll('.indicator');
    const prevBtn = document.querySelector('.hero-prev');
    const nextBtn = document.querySelector('.hero-next');
    
    // Check if elements exist before proceeding
    if (slides.length === 0) return;
    
    let currentSlide = 0;
    let slideInterval;

    function showSlide(index) {
        // Remove active class from all slides and indicators
        slides.forEach(slide => slide.classList.remove('active'));
        indicators.forEach(indicator => indicator.classList.remove('active'));
        
        // Add active class to current slide and indicator
        slides[index].classList.add('active');
        indicators[index].classList.add('active');
        
        currentSlide = index;
    }

    function nextSlide() {
        const next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }

    function prevSlide() {
        const prev = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(prev);
    }

    function startSlideshow() {
        slideInterval = setInterval(nextSlide, 5000);
    }

    function stopSlideshow() {
        clearInterval(slideInterval);
    }

    // Event listeners
    if (nextBtn) nextBtn.addEventListener('click', () => {
        nextSlide();
        stopSlideshow();
        startSlideshow();
    });

    if (prevBtn) prevBtn.addEventListener('click', () => {
        prevSlide();
        stopSlideshow();
        startSlideshow();
    });

    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            showSlide(index);
            stopSlideshow();
            startSlideshow();
        });
    });

    // Start automatic slideshow
    startSlideshow();

    // Pause on hover
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroSection.addEventListener('mouseenter', stopSlideshow);
        heroSection.addEventListener('mouseleave', startSlideshow);
    }
}

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');
    const header = document.querySelector('.header');

    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const headerHeight = header ? header.offsetHeight : 0;
                    const targetPosition = target.offsetTop - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Mobile menu toggle
    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }

    // Active navigation highlighting
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        if (sections.length === 0) return;
        
        const scrollPos = window.scrollY + 150;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);

            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                navLinks.forEach(link => link.classList.remove('active'));
                if (navLink) navLink.classList.add('active');
            }
        });
    });
}

// Language Switcher
function initializeLanguageSwitcher() {
    const langButtons = document.querySelectorAll('.lang-btn');
    if (langButtons.length === 0) return;
    
    let currentLang = 'en';

    langButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            if (lang !== currentLang) {
                switchLanguage(lang);
                currentLang = lang;
                
                // Update active button
                langButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    function switchLanguage(lang) {
        const elements = document.querySelectorAll('[data-en][data-zh]');
        
        elements.forEach(element => {
            const text = element.getAttribute(`data-${lang}`);
            if (text) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = text;
                } else {
                    element.textContent = text;
                }
            }
        });

        // Update placeholders
        const placeholderElements = document.querySelectorAll('[data-placeholder-zh]');
        placeholderElements.forEach(element => {
            if (lang === 'zh') {
                element.placeholder = element.getAttribute('data-placeholder-zh');
            } else {
                // Reset to original placeholder or use data-en if available
                const originalPlaceholder = element.getAttribute('placeholder');
                element.placeholder = originalPlaceholder;
            }
        });

        // Store language preference
        localStorage.setItem('preferred-language', lang);
    }

    // Load saved language preference
    const savedLang = localStorage.getItem('preferred-language');
    if (savedLang && savedLang !== 'en') {
        const langBtn = document.querySelector(`[data-lang="${savedLang}"]`);
        if (langBtn) {
            langBtn.click();
        }
    }
}

// Modals
function initializeModals() {
    const searchBtn = document.querySelector('.search-btn');
    const quoteBtn = document.querySelector('.quote-btn');
    const searchModal = document.getElementById('searchModal');
    const quoteModal = document.getElementById('quoteModal');
    const searchClose = document.querySelector('.search-close');
    const quoteClose = document.querySelector('.quote-close');

    // Search modal
    if (searchBtn && searchModal) {
        searchBtn.addEventListener('click', () => {
            searchModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    if (searchClose && searchModal) {
        searchClose.addEventListener('click', () => {
            searchModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    // Quote modal
    if (quoteBtn && quoteModal) {
        quoteBtn.addEventListener('click', () => {
            quoteModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    if (quoteClose && quoteModal) {
        quoteClose.addEventListener('click', () => {
            quoteModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    // Close modals on outside click
    [searchModal, quoteModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        }
    });

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            [searchModal, quoteModal].forEach(modal => {
                if (modal && modal.classList.contains('active')) {
                    modal.classList.remove('active');
                    document.body.style.overflow = '';
                }
            });
        }
    });
}

// Tabs (Solutions Section)
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    if (tabButtons.length === 0 || tabPanels.length === 0) return;

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            if (!targetTab) return;
            
            // Remove active class from all buttons and panels
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button and corresponding panel
            this.classList.add('active');
            const targetPanel = document.getElementById(targetTab);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// Case Filter
function initializeCaseFilter() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const caseItems = document.querySelectorAll('.case-item');
    
    if (filterButtons.length === 0 || caseItems.length === 0) return;

    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            if (!filter) return;
            
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Filter case items
            caseItems.forEach(item => {
                const category = item.getAttribute('data-category');
                if (filter === 'all' || category === filter) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

// Contact Form
function initializeContactForm() {
    const contactForm = document.querySelector('.contact-form');
    
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        
        // Basic validation
        if (!data.name || !data.email || !data.company) {
            showNotification('Please fill in all required fields.', 'error');
            return;
        }
        
        if (!isValidEmail(data.email)) {
            showNotification('Please enter a valid email address.', 'error');
            return;
        }
        
        // Simulate form submission
        const submitBtn = this.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Sending...';
        submitBtn.disabled = true;
        
        // Send to admin API
        const contactData = {
            name: data.name,
            email: data.email,
            company: data.company,
            phone: data.phone || '',
            product: data.product || '',
            message: data.message || ''
        };

        fetch('/admin/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(contactData)
        })
        .then(response => response.json())
        .then(result => {
            showNotification('Thank you for your message! We will get back to you soon.', 'success');
            this.reset();
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Message sent successfully! We will contact you soon.', 'success');
            this.reset();
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    });
}

// Quote Form (Multi-step)
function initializeQuoteForm() {
    const quoteForm = document.querySelector('.quote-form');
    const formSteps = document.querySelectorAll('.form-step');
    const nextBtns = document.querySelectorAll('.next-step');
    const prevBtns = document.querySelectorAll('.prev-step');
    
    if (!quoteForm || formSteps.length === 0) return;
    
    let currentStep = 1;

    // Next step buttons
    nextBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (validateStep(currentStep)) {
                if (currentStep < formSteps.length) {
                    showStep(currentStep + 1);
                }
            }
        });
    });

    // Previous step buttons
    prevBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (currentStep > 1) {
                showStep(currentStep - 1);
            }
        });
    });

    // Form submission
    quoteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateStep(currentStep)) {
            // Get form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Simulate form submission
            const submitBtn = this.querySelector('button[type="submit"]');
            if (!submitBtn) return;
            
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
            
            // Send to admin API
            fetch('/admin/api/quote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                showNotification('Quote request submitted successfully! We will contact you within 24 hours.', 'success');
                this.reset();
                showStep(1);
                const quoteModal = document.getElementById('quoteModal');
                if (quoteModal) {
                    quoteModal.classList.remove('active');
                    document.body.style.overflow = '';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Quote request submitted successfully! We will contact you within 24 hours.', 'success');
                this.reset();
                showStep(1);
                const quoteModal = document.getElementById('quoteModal');
                if (quoteModal) {
                    quoteModal.classList.remove('active');
                    document.body.style.overflow = '';
                }
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        }
    });

    function showStep(step) {
        formSteps.forEach(s => s.classList.remove('active'));
        const targetStep = document.querySelector(`[data-step="${step}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
            currentStep = step;
        }
    }

    function validateStep(step) {
        const currentStepElement = document.querySelector(`[data-step="${step}"]`);
        if (!currentStepElement) return true;
        
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = '#dc3545';
                isValid = false;
            } else {
                field.style.borderColor = '#e9ecef';
            }
        });

        if (!isValid) {
            showNotification('Please fill in all required fields.', 'error');
        }

        return isValid;
    }
}

// Scroll Effects
function initializeScrollEffects() {
    const header = document.querySelector('.header');
    if (!header) return;
    
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        // Header background on scroll
        if (scrollTop > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        // Hide/show header on scroll
        if (scrollTop > lastScrollTop && scrollTop > 200) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }

        lastScrollTop = scrollTop;
    });

    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        const parallax = heroSection.querySelector('.hero-bg');
        if (parallax) {
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const speed = scrolled * 0.5;
                parallax.style.transform = `translateY(${speed}px)`;
            });
        }
    }
}

// Counter Animation
function initializeCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    if (counters.length === 0) return;
    
    const observerOptions = {
        threshold: 0.7
    };

    // Check if IntersectionObserver is available
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            observer.observe(counter);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        counters.forEach(counter => {
            animateCounter(counter);
        });
    }

    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;

        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    }
}

// AOS (Animate On Scroll) Initialization
function initializeAOS() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        });
    }
}

// Back to Top Button
function initializeBackToTop() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (!backToTopBtn) return;
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });

    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Utility Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;

    // Add styles if not already added
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(100%);
                transition: transform 0.3s ease;
            }
            .notification-success { background-color: #28a745; }
            .notification-error { background-color: #dc3545; }
            .notification-info { background-color: #17a2b8; }
            .notification-warning { background-color: #ffc107; color: #212529; }
            .notification.show { transform: translateX(0); }
            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .notification-close {
                background: none;
                border: none;
                color: inherit;
                font-size: 20px;
                cursor: pointer;
                margin-left: 15px;
                opacity: 0.8;
            }
            .notification-close:hover { opacity: 1; }
        `;
        document.head.appendChild(styles);
    }

    // Add to DOM
    document.body.appendChild(notification);

    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);

    // Auto remove after 5 seconds
    const autoRemove = setTimeout(() => {
        removeNotification(notification);
    }, 5000);

    // Manual close
    const closeBtn = notification.querySelector('.notification-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            clearTimeout(autoRemove);
            removeNotification(notification);
        });
    }

    function removeNotification(element) {
        element.classList.remove('show');
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 300);
    }
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    
    if (!searchInput || !searchResults) return;

    // Sample search data (in a real application, this would come from an API)
    const searchData = [
        { title: 'P1.56 Fine Pitch LED Display', category: 'Fine Pitch', url: '#fine-pitch' },
        { title: 'P1.25 Fine Pitch LED Display', category: 'Fine Pitch', url: '#fine-pitch' },
        { title: 'P0.9 Fine Pitch LED Display', category: 'Fine Pitch', url: '#fine-pitch' },
        { title: 'Outdoor LED Billboard', category: 'Outdoor', url: '#outdoor-led' },
        { title: 'Indoor LED Video Wall', category: 'Indoor', url: '#indoor-led' },
        { title: 'Transparent LED Display', category: 'Transparent', url: '#transparent-led' },
        { title: 'Creative LED Display', category: 'Creative', url: '#creative-led' },
        { title: 'Rental LED Display', category: 'Rental', url: '#rental-led' }
    ];

    let searchTimeout;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                performSearch(query);
            } else {
                searchResults.innerHTML = '';
            }
        }, 300);
    });

    function performSearch(query) {
        const results = searchData.filter(item => 
            item.title.toLowerCase().includes(query) || 
            item.category.toLowerCase().includes(query)
        );

        if (results.length > 0) {
            searchResults.innerHTML = `
                <div class="search-results-header">
                    <h4>Search Results (${results.length})</h4>
                </div>
                <div class="search-results-list">
                    ${results.map(item => `
                        <a href="${item.url}" class="search-result-item">
                            <div class="search-result-title">${item.title}</div>
                            <div class="search-result-category">${item.category}</div>
                        </a>
                    `).join('')}
                </div>
            `;
        } else {
            searchResults.innerHTML = `
                <div class="search-no-results">
                    <p>No results found for "${query}"</p>
                    <p>Try searching for: LED display, fine pitch, outdoor, indoor, transparent</p>
                </div>
            `;
        }

        // Add click handlers to search results
        const resultItems = searchResults.querySelectorAll('.search-result-item');
        resultItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('href');
                const searchModal = document.getElementById('searchModal');
                if (searchModal) {
                    searchModal.classList.remove('active');
                    document.body.style.overflow = '';
                }
                
                // Navigate to the section
                if (url && url.startsWith('#')) {
                    const target = document.querySelector(url);
                    if (target) {
                        const header = document.querySelector('.header');
                        const headerHeight = header ? header.offsetHeight : 0;
                        const targetPosition = target.offsetTop - headerHeight;
                        
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                }
            });
        });
    }
}

// Product Comparison (if needed)
function initializeProductComparison() {
    const compareButtons = document.querySelectorAll('.compare-btn');
    const comparisonPanel = document.querySelector('.comparison-panel');
    
    if (compareButtons.length === 0) return;
    
    let comparedProducts = [];

    compareButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productName = this.getAttribute('data-product-name');
            
            if (!productId || !productName) return;
            
            if (comparedProducts.length < 3 && !comparedProducts.find(p => p.id === productId)) {
                comparedProducts.push({ id: productId, name: productName });
                updateComparisonPanel();
                this.textContent = 'Remove from Compare';
                this.classList.add('active');
            } else if (comparedProducts.find(p => p.id === productId)) {
                comparedProducts = comparedProducts.filter(p => p.id !== productId);
                updateComparisonPanel();
                this.textContent = 'Compare';
                this.classList.remove('active');
            } else {
                showNotification('You can compare up to 3 products only.', 'warning');
            }
        });
    });

    function updateComparisonPanel() {
        if (!comparisonPanel) return;
        
        if (comparedProducts.length > 0) {
            comparisonPanel.style.display = 'block';
            comparisonPanel.innerHTML = `
                <div class="comparison-header">
                    <h4>Product Comparison (${comparedProducts.length}/3)</h4>
                    <button class="clear-comparison">Clear All</button>
                </div>
                <div class="comparison-products">
                    ${comparedProducts.map(product => `
                        <div class="comparison-product">
                            <span>${product.name}</span>
                            <button class="remove-product" data-product-id="${product.id}">&times;</button>
                        </div>
                    `).join('')}
                </div>
                ${comparedProducts.length >= 2 ? '<button class="btn btn-primary compare-now">Compare Now</button>' : ''}
            `;

            // Add event listeners for remove buttons
            const removeButtons = comparisonPanel.querySelectorAll('.remove-product');
            removeButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    const productId = this.getAttribute('data-product-id');
                    const compareBtn = document.querySelector(`[data-product-id="${productId}"]`);
                    if (compareBtn) {
                        compareBtn.click();
                    }
                });
            });

            // Clear all button
            const clearBtn = comparisonPanel.querySelector('.clear-comparison');
            if (clearBtn) {
                clearBtn.addEventListener('click', function() {
                    comparedProducts = [];
                    compareButtons.forEach(btn => {
                        btn.textContent = 'Compare';
                        btn.classList.remove('active');
                    });
                    comparisonPanel.style.display = 'none';
                });
            }
        } else {
            comparisonPanel.style.display = 'none';
        }
    }
}

// Lazy Loading for Images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    if (images.length === 0) return;
    
    // Check if IntersectionObserver is available
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

// Performance optimization: Debounce function
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Add CSS for search results if not already present
if (!document.querySelector('#search-styles')) {
    const searchStyles = document.createElement('style');
    searchStyles.id = 'search-styles';
    searchStyles.textContent = `
        .search-results-header h4 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        .search-result-item {
            display: block;
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
            text-decoration: none;
            color: inherit;
            transition: background-color 0.3s ease;
        }
        .search-result-item:hover {
            background-color: #f8f9fa;
        }
        .search-result-title {
            font-weight: 500;
            color: var(--primary-color);
            margin-bottom: 5px;
        }
        .search-result-category {
            font-size: 0.9rem;
            color: var(--medium-gray);
        }
        .search-no-results {
            text-align: center;
            padding: 30px 20px;
            color: var(--medium-gray);
        }
        .comparison-panel {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            padding: 20px;
            max-width: 300px;
            z-index: 1000;
            display: none;
        }
        .comparison-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .comparison-product {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .remove-product {
            background: none;
            border: none;
            color: #dc3545;
            cursor: pointer;
            font-size: 18px;
        }
        .compare-now {
            width: 100%;
            margin-top: 15px;
        }
    `;
    document.head.appendChild(searchStyles);
}

// Frontend-Backend Synchronization
class AdminSync {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.lastSync = localStorage.getItem('lastSync');
        this.syncInterval = 30000; // 30 seconds
        this.init();
    }

    init() {
        // Check if we're on a page that needs syncing
        if (!document.querySelector('.product-grid')) {
            return;
        }
        
        // Sync data on page load
        this.syncData();
        
        // Periodically sync data
        setInterval(() => {
            this.syncData();
        }, this.syncInterval);
        
        // Sync when page becomes visible
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.syncData();
            }
        });
    }

    async syncData() {
        try {
            console.log('Syncing data with backend...');
            
            // Sync product data
            await this.syncProducts();
            
            // Update sync time
            this.lastSync = new Date().toISOString();
            localStorage.setItem('lastSync', this.lastSync);
            
            console.log('Data sync completed');
            this.updateSyncStatus('success');
            
        } catch (error) {
            console.error('Sync failed:', error);
            this.updateSyncStatus('error');
        }
    }

    async syncProducts() {
        try {
            const response = await fetch(`${this.apiBase}/products`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            
            if (data.success) {
                // Update product page content
                this.updateProductsDisplay(data.products);
                console.log(`Synced ${data.products.length} products`);
            }
        } catch (error) {
            console.error('Failed to sync products:', error);
        }
    }

    updateProductsDisplay(products) {
        // Update product list on product page
        const productGrid = document.querySelector('.product-grid');
        if (productGrid && products && products.length > 0) {
            productGrid.innerHTML = products.map(product => `
                <div class="col-lg-4 col-md-6 mb-4" data-aos="fade-up">
                    <div class="card product-card h-100">
                        <div class="card-img-container">
                            <img src="${product.images || 'assets/products/placeholder.jpg'}" 
                                 class="card-img-top" alt="${product.name_en || 'Product'}">
                            <div class="card-overlay">
                                <a href="${this.getCategoryPage(product.category)}" class="btn btn-primary">
                                    <i class="fas fa-eye me-2"></i>View Details
                                </a>
                            </div>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">${product.name_en || 'Product'}</h5>
                            <p class="card-text">${product.description_en || ''}</p>
                            <div class="product-features">
                                ${product.features ? product.features.split(',').map(feature => 
                                    `<span class="badge bg-primary me-1">${feature.trim()}</span>`
                                ).join('') : ''}
                            </div>
                        </div>
                        <div class="card-footer">
                            <small class="text-muted">Category: ${product.category || 'General'}</small>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    getCategoryPage(category) {
        if (!category) return 'products.html';
        
        const categoryPages = {
            'fine-pitch': 'fine-pitch.html',
            'outdoor': 'outdoor.html',
            'indoor': 'products.html',
            'transparent': 'transparent.html',
            'creative': 'creative.html',
            'rental': 'rental.html'
        };
        return categoryPages[category.toLowerCase()] || 'products.html';
    }

    updateSyncStatus(status) {
        // Create sync status indicator
        let statusIndicator = document.querySelector('.sync-status');
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.className = 'sync-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                z-index: 9999;
                transition: all 0.3s ease;
            `;
            document.body.appendChild(statusIndicator);
        }

        if (status === 'success') {
            statusIndicator.style.backgroundColor = '#10b981';
            statusIndicator.style.color = 'white';
            statusIndicator.innerHTML = '<i class="fas fa-check me-1"></i>Synced';
            
            // Hide after 3 seconds
            setTimeout(() => {
                statusIndicator.style.opacity = '0';
            }, 3000);
        } else if (status === 'error') {
            statusIndicator.style.backgroundColor = '#ef4444';
            statusIndicator.style.color = 'white';
            statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Sync Error';
        }

        // Reset opacity
        statusIndicator.style.opacity = '1';
    }
}

// Initialize sync system only if needed
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on a page that needs it
    if (document.querySelector('.product-grid')) {
        window.adminSync = new AdminSync();
    }
});
