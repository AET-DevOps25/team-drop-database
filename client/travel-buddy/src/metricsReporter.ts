export type MetricsLabels = Record<string, string>;

export interface MetricPayload {
    /**
     * Name of the metric (e.g., 'frontend_route_change_seconds')
     */
    name: string;

    /**
     * Labels as key/value pairs (e.g., { path: '/home' })
     */
    labels: MetricsLabels;

    /**
     * Numeric value to report (timing in seconds, count, etc.)
     */
    value: number;
}

/**
 * Sends a metric to the backend collector for Prometheus scraping.
 *
 * @param payload - Metric data including name, labels, and value
 */
export async function reportMetric(
    payload: MetricPayload
): Promise<void> {
    try {
        await fetch('http://localhost:9300/metrics/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
    } catch (err) {
        // Silently ignore network or serialization errors
        console.warn('Metric reporting failed:', err);
    }
}
