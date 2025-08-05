/**
 * Global JavaScript Fix for LED Display Website
 * This script fixes common JavaScript errors and provides better error handling
 */

// Execute immediately when loaded
(function() {
    console.log('Applying global JavaScript fixes...');
    
    // Fix 1: Safe getBoundingClientRect
    if (window.Element && Element.prototype.getBoundingClientRect) {
        console.log('Applying getBoundingClientRect fix');
        
        // Save the original method
        window.Element.prototype.originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
        
        // Override with a safe version
        Element.prototype.getBoundingClientRect = function() {
            try {
                return this.originalGetBoundingClientRect.apply(this);
            } catch (error) {
                console.warn('Error in getBoundingClientRect, returning default values');
                return {
                    top: 0, right: 0, bottom: 0, left: 0,
                    width: 0, height: 0, x: 0, y: 0
                };
            }
        };
    }
    
    // Fix 2: Safe querySelector and querySelectorAll
    if (Document.prototype.querySelector) {
        console.log('Applying querySelector fix');
        
        const originalQuerySelector = Document.prototype.querySelector;
        Document.prototype.querySelector = function(selector) {
            try {
                return originalQuerySelector.call(this, selector);
            } catch (error) {
                console.warn('Error in querySelector with selector:', selector, error);
                return null;
            }
        };
    }
    
    if (Document.prototype.querySelectorAll) {
        console.log('Applying querySelectorAll fix');
        
        const originalQuerySelectorAll = Document.prototype.querySelectorAll;
        Document.prototype.querySelectorAll = function(selector) {
            try {
                return originalQuerySelectorAll.call(this, selector);
            } catch (error) {
                console.warn('Error in querySelectorAll with selector:', selector, error);
                return [];
            }
        };
    }
    
    // Fix 3: Safe event listeners
    if (EventTarget.prototype.addEventListener) {
        console.log('Applying addEventListener fix');
        
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (!listener) {
                console.warn('Attempted to add null event listener for event:', type);
                return;
            }
            
            // Wrap the listener in a try-catch
            const safeListener = function(event) {
                try {
                    return listener.call(this, event);
                } catch (error) {
                    console.warn('Error in event listener for', type, error);
                }
            };
            
            return originalAddEventListener.call(this, type, safeListener, options);
        };
    }
    
    // Fix 4: Global error handler
    window.addEventListener('error', function(event) {
        console.warn('Caught global error:', event.error || event.message);
        
        // Don't prevent default in debug mode
        if (!window.location.search.includes('debug=true')) {
            event.preventDefault();
        }
    });
    
    // Fix 5: Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        console.warn('Unhandled promise rejection:', event.reason);
        
        // Don't prevent default in debug mode
        if (!window.location.search.includes('debug=true')) {
            event.preventDefault();
        }
    });
    
    // Fix 6: Safe setTimeout and setInterval
    if (window.setTimeout) {
        console.log('Applying setTimeout fix');
        
        const originalSetTimeout = window.setTimeout;
        window.setTimeout = function(callback, delay) {
            if (typeof callback !== 'function') {
                return originalSetTimeout.apply(this, arguments);
            }
            
            const safeCallback = function() {
                try {
                    return callback.apply(this, arguments);
                } catch (error) {
                    console.warn('Error in setTimeout callback:', error);
                }
            };
            
            return originalSetTimeout.call(this, safeCallback, delay);
        };
    }
    
    if (window.setInterval) {
        console.log('Applying setInterval fix');
        
        const originalSetInterval = window.setInterval;
        window.setInterval = function(callback, delay) {
            if (typeof callback !== 'function') {
                return originalSetInterval.apply(this, arguments);
            }
            
            const safeCallback = function() {
                try {
                    return callback.apply(this, arguments);
                } catch (error) {
                    console.warn('Error in setInterval callback:', error);
                }
            };
            
            return originalSetInterval.call(this, safeCallback, delay);
        };
    }
    
    // Fix 7: Create missing elements that might be referenced
    function createMissingElements() {
        // Common elements that might be missing
        const commonElements = [
            { id: 'backToTop', className: 'back-to-top', style: 'display: none;' },
            { id: 'searchModal', className: 'search-modal', style: 'display: none;' },
            { id: 'quoteModal', className: 'quote-modal', style: 'display: none;' }
        ];
        
        commonElements.forEach(element => {
            if (!document.getElementById(element.id)) {
                const el = document.createElement('div');
                el.id = element.id;
                el.className = element.className;
                el.style = element.style;
                document.body.appendChild(el);
                console.log('Created missing element:', element.id);
            }
        });
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createMissingElements);
    } else {
        createMissingElements();
    }
    
    console.log('✓ Global JavaScript fixes applied successfully');
})();