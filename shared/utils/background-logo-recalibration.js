/**
 * BACKGROUND LOGO RECALIBRATION SYSTEM
 * 
 * Adds Stark-tech HUD recalibration animations to background logos
 * during viewport resizing and orientation changes.
 */

let recalibrationTimeout;
let lastOrientation = window.matchMedia('(orientation: portrait)').matches ? 'portrait' : 'landscape';

/**
 * Trigger HUD recalibration animation on a logo element
 * @param {boolean} isTablet - Whether device is tablet-sized for enhanced animation
 */
function recalibrateBackgroundLogo(logo, isTablet = false) {
    if (!logo) return;
    
    // Add recalibrating state
    logo.setAttribute('data-state', 'recalibrating');
    
    // Enhanced animation for tablet orientation changes
    const duration = isTablet ? 450 : 350;
    const scaleAmount = isTablet ? 0.96 : 0.98;
    const blurAmount = isTablet ? 3 : 2;
    const brightness = isTablet ? 1.2 : 1.15;
    
    logo.style.transition = `transform ${duration}ms cubic-bezier(0.4, 0.0, 0.2, 1), filter ${duration}ms cubic-bezier(0.4, 0.0, 0.2, 1)`;
    
    // Brief scale pulse and glow effect
    logo.style.transform = `translateZ(0) scale(${scaleAmount})`;
    logo.style.filter = `blur(${blurAmount}px) brightness(${brightness})`;
    
    // Return to stable state
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            logo.style.transform = 'translateZ(0) scale(1)';
            logo.style.filter = 'none';
            
            // Remove state after animation completes
            setTimeout(() => {
                logo.removeAttribute('data-state');
            }, duration);
        });
    });
}

/**
 * Handle viewport resize events
 */
function handleViewportChange() {
    // Debounce rapid resize events
    clearTimeout(recalibrationTimeout);
    
    recalibrationTimeout = setTimeout(() => {
        const currentOrientation = window.matchMedia('(orientation: portrait)').matches ? 'portrait' : 'landscape';
        
        // Only animate on orientation change
        if (currentOrientation !== lastOrientation) {
            lastOrientation = currentOrientation;
            
            // Check if device is tablet-sized (744px to 1200px width)
            const isTablet = window.matchMedia('(min-width: 744px) and (max-width: 1200px)').matches;
            
            // Trigger recalibration on all background logos with enhanced animation for tablets
            const logos = document.querySelectorAll('[data-role="background-logo"]');
            logos.forEach(logo => recalibrateBackgroundLogo(logo, isTablet));
        }
    }, 100); // Debounce delay
}

/**
 * Initialize the recalibration system
 */
export function initBackgroundLogoRecalibration() {
    // Skip if reduced motion is preferred
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    
    // Listen for viewport changes
    window.addEventListener('resize', handleViewportChange);
    
    // Listen for orientation changes (more reliable on mobile)
    window.addEventListener('orientationchange', () => {
        // Give device time to update viewport dimensions
        setTimeout(handleViewportChange, 100);
    });
    
    // Cleanup function
    return () => {
        window.removeEventListener('resize', handleViewportChange);
        window.removeEventListener('orientationchange', handleViewportChange);
        clearTimeout(recalibrationTimeout);
    };
}

/**
 * Manual trigger for custom transitions
 */
export function triggerLogoRecalibration(selector = '[data-role="background-logo"]') {
    const logos = document.querySelectorAll(selector);
    logos.forEach(recalibrateBackgroundLogo);
}
