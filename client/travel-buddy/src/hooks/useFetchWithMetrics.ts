import { reportMetric } from '../metricsReporter';

interface FetchWithMetricsOptions extends RequestInit {
    metricName: string;
    labels?: Record<string, string>;
}

export async function fetchWithMetrics(
    input: RequestInfo,
    { metricName, labels = {}, ...init }: FetchWithMetricsOptions
): Promise<Response> {
    const start = performance.now();
    try {
        const response = await fetch(input, init);
        const durationMs = performance.now() - start;
        reportMetric({
            name: metricName + '_duration_seconds',
            labels: { ...labels, status: String(response.status) },
            value: durationMs / 1000
        });
        return response;
    } catch (err) {
        const durationMs = performance.now() - start;
        reportMetric({
            name: metricName + '_errors_total',
            labels,
            value: 1
        });
        // Optionally report duration of failed call
        reportMetric({
            name: metricName + '_duration_seconds',
            labels: { ...labels, error: 'network' },
            value: durationMs / 1000
        });
        throw err;
    }
}