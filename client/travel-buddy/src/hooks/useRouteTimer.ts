import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { reportMetric } from '../metricsReporter';

export function useRouteTimer(): void {
    const location = useLocation();

    useEffect(() => {
        const start = performance.now();
        return () => {
            const durationMs = performance.now() - start;
            reportMetric({
                name: 'frontend_route_change_seconds',
                labels: { path: location.pathname },
                value: durationMs / 1000
            });
        };
    }, [location.pathname]);
}
