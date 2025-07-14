import express, { Request, Response } from 'express';
import client from 'prom-client';
import cors from 'cors';

const app = express();
app.use(cors({
    origin: '*'
}));
app.use(express.json());

// 1) Registry & defaults
const registry = new client.Registry();
client.collectDefaultMetrics({ register: registry });

// 2) Dynamic histograms map
const histograms: Record<string, client.Histogram<string>> = {};

/**
 * POST /metrics/import
 * { name: string, labels?: Record<string,string>, value: number }
 */
app.post('/metrics/import', (req: Request, res: Response) => {
    const { name, labels = {}, value } = req.body as {
        name: string;
        labels?: Record<string, string>;
        value: number;
    };
    if (!histograms[name]) {
        histograms[name] = new client.Histogram({
            name,
            help: `${name} (from front-end)`,
            labelNames: Object.keys(labels),
            buckets: [0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5],
        });
        registry.registerMetric(histograms[name]);
    }
    histograms[name].labels(labels).observe(value);
    res.sendStatus(200);
});

// 3) Scrape endpoint
app.get('/metrics', async (_: Request, res: Response) => {
    res.setHeader('Content-Type', registry.contentType);
    res.end(await registry.metrics());
});

const port = parseInt(process.env.PORT || '9300', 10);
app.listen(port, () => {
    console.log('Metrics server listening on http://localhost:${port}');
});
