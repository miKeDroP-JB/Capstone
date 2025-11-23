// Traffic tracking for demo_hvac_company
(function() {
    const trackingData = {
        pageUrl: window.location.href,
        referrer: document.referrer,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
    };

    // Get traffic source from URL parameter
    const params = new URLSearchParams(window.location.search);
    const source = params.get('source');

    if (source) {
        trackingData.source = source;
        console.log('Traffic source:', source);
    }

    // Track page view
    console.log('Page view tracked:', trackingData);

    // In production, send to analytics endpoint
    // fetch('/api/track', { method: 'POST', body: JSON.stringify(trackingData) });
})();

// Track clicks
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('cta-button')) {
        console.log('CTA clicked:', e.target.textContent);
    }
});
