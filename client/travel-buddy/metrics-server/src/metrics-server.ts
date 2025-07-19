import express, { Request, Response } from 'express';
import client from 'prom-client';
import cors from 'cors';

const app = express();
app.use(cors({ origin: '*' }));          // Adjust if needed
app.use(express.json({ limit: '50kb' })); // Avoid large bodies

// Registry & default metrics
const registry = new client.Registry();
client.collectDefaultMetrics({ register: registry });

// Whitelist / constraints
const MAX_LABEL_KEYS = 5;
const MAX_LABEL_VALUE_LEN = 60;
const METRIC_NAME_REGEX = /^[a-zA-Z_:][a-zA-Z0-9_:]*$/;
const histograms: Record<string, client.Histogram<string>> = {};

function sanitizeLabels(src: Record<string, string>): Record<string,string> {
    const entries = Object.entries(src).slice(0, MAX_LABEL_KEYS);
    const out: Record<string,string> = {};
    for (const [k,v] of entries) {
        out[k] = v.toString().slice(0, MAX_LABEL_VALUE_LEN);
    }
    return out;
}

app.post('/metrics/import', (req: Request, res: Response) => {
    const { name, labels = {}, value } = req.body || {};
    if (!name || typeof value !== 'number') {
        return res.status(400).json({ error: 'name (string) and value (number) required' });
    }
    if (!METRIC_NAME_REGEX.test(name)) {
        return res.status(400).json({ error: 'Invalid metric name' });
    }
    const safeLabels = sanitizeLabels(labels);

    let h = histograms[name];
    if (!h) {
        // Single-threaded Node; simple guard is fine
        h = new client.Histogram({
            name,
            help: `${name} (frontend custom)`,
            labelNames: Object.keys(safeLabels),
            buckets: (process.env.HISTOGRAM_BUCKETS || '')
                    .split(',')
                    .map(s => parseFloat(s))
                    .filter(n => !isNaN(n))
                || [0.005,0.01,0.05,0.1,0.5,1,2,5],
        });
        registry.registerMetric(h);
        histograms[name] = h;
    } else {
        // (Optional) verify label keys consistency
        const expected = h.labelNames.sort().join(',');
        const got = Object.keys(safeLabels).sort().join(',');
        if (expected !== got) {
            return res.status(409).json({ error: 'Label set differs from initial histogram definition' });
        }
    }
    h.labels(safeLabels).observe(value);
    res.sendStatus(200);
});

app.get('/metrics', async (_: Request, res: Response) => {
    res.setHeader('Content-Type', registry.contentType);
    res.end(await registry.metrics());
});

app.get('/healthz', (_: Request, res: Response) => res.send('ok'));
app.get('/readyz', (_: Request, res: Response) => res.send('ok'));

const port = parseInt(process.env.METRICS_PORT || process.env.PORT || '9300', 10);
app.listen(port, () => {
    // Backticks for interpolation:
    console.log(`Metrics server listening on http://0.0.0.0:${port}`);
});
