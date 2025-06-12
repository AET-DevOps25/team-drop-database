import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardMedia, CardContent, Typography, Rating, Button, Grid } from '@mui/material';
// 其他 MUI 组件也建议单独导入
const attractions = [
  {
    id: '1',
    name: '故宫',
    image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
    description: '中国最著名的皇家宫殿，历史悠久。',
    rating: 4.8,
  },
  {
    id: '2',
    name: '长城',
    image: 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=400&q=80',
    description: '世界七大奇迹之一，壮观的古代防御工程。',
    rating: 4.7,
  },
];

const AttractionList: React.FC = () => (
  <div style={{ padding: 32 }}>
    <Typography variant="h4" gutterBottom>热门景点</Typography>
    <Grid container spacing={4}>
      {attractions.map(a => (
        <Grid key={a.id}>
          <Card>
            <CardMedia
              component="img"
              height="180"
              image={a.image}
              alt={a.name}
            />
            <CardContent>
              <Typography variant="h6">{a.name}</Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {a.description}
              </Typography>
              <Rating value={a.rating} precision={0.1} readOnly size="small" />
              <div style={{ marginTop: 12 }}>
                <Button
                  component={Link}
                  to={`/attractions/${a.id}`}
                  variant="contained"
                  color="primary"
                  size="small"
                >
                  查看详情
                </Button>
              </div>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  </div>
);

export default AttractionList;