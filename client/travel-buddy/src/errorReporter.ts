import { reportMetric } from './metricsReporter';

/**
 * Initializes JS error and unhandled rejection metrics.
 */
export function initErrorMetrics(): void {
    // Track uncaught JS errors
    window.addEventListener('error', (event: ErrorEvent) => {
        reportMetric({
            name: 'frontend_js_errors_total',
            labels: { message: event.message, filename: event.filename },
            value: 1,
        });
    });

    // Track unhandled promise rejections
    window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
        const reason = event.reason instanceof Error ? event.reason.message : String(event.reason);
        reportMetric({
            name: 'frontend_unhandled_rejections_total',
            labels: { reason },
            value: 1,
        });
    });
}