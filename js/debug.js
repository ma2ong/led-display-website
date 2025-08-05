/**
 * Debug script to identify and fix getBoundingClientRect errors
 */

// Execute when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Debug script loaded');
    
    // Find all scripts on the page
    const scripts = document.querySelectorAll('script');
    console.log(`Found ${scripts.length} script tags on the page`);
    
    // Override getBoundingClientRect to catch errors
    const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
    
    Element.prototype.getBoundingClientRect = function() {
        try {
            return originalGetBoundingClientRect.apply(this);
        } catch (error) {
            console.error('Error in getBoundingClientRect for element:', this);
            console.error('Element details:', {
                tagName: this.tagName,
                id: this.id,
                className: this.className,
                innerHTML: this.innerHTML.substring(0, 100) + (this.innerHTML.length > 100 ? '...' : '')
            });
            console.error('Original error:', error);
            
            // Return a dummy rectangle to prevent errors
            return {
                top: 0,
                right: 0,
                bottom: 0,
                left: 0,
                width: 0,
                height: 0,
                x: 0,
                y: 0
            };
        }
    };
    
    // Check for common elements that might use getBoundingClientRect
    const elementsToCheck = [
        '.hero', '.hero-slide', '.header', 
        '.nav-menu', '.tab-panel', '.case-item',
        '.product-card', '.comparison-panel',
        '#backToTop', '.search-results'
    ];
    
    console.log('Checking for elements that might use getBoundingClientRect:');
    elementsToCheck.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        console.log(`${selector}: ${elements.length} elements found`);
        
        if (elements.length === 0) {
            console.warn(`Warning: No elements found for selector "${selector}"`);
        }
    });
    
    // Add a global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error caught:', event.error);
        
        // If it's a getBoundingClientRect error, provide more details
        if (event.error && event.error.message && event.error.message.includes('getBoundingClientRect')) {
            console.error('This is a getBoundingClientRect error. Check the elements above.');
        }
        
        // Prevent the error from bubbling up
        event.preventDefault();
    });
    
    console.log('Debug script initialization complete');
});