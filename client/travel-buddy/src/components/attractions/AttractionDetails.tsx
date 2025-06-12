import React from 'react';
import { Card, CardMedia, CardContent, Typography, Rating } from '@mui/material';

type AttractionId = '1' | '2';

interface AttractionDetail {
  name: string;
  image: string;
  description: string;
  rating: number;
  details: string;
}

const mockDetails: Record<AttractionId, AttractionDetail> = {
  '1': {
    name: '故宫',
    image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80',
    description: '中国最著名的皇家宫殿，位于北京中心。',
    rating: 4.8,
    details: '故宫是明清两代的皇家宫殿，现为故宫博物院。'
  },
  '2': {
    name: '长城',
    image: 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=600&q=80',
    description: '世界七大奇迹之一，壮观的古代防御工程。',
    rating: 4.7,
    details: '长城全长约2万公里，是中国古代伟大的防御工程。'
  }
};

interface AttractionDetailsProps {
  attractionId: AttractionId;
}

const AttractionDetails: React.FC<AttractionDetailsProps> = ({ attractionId }) => {
  const detail = mockDetails[attractionId];

  if (!detail) return <div>未找到景点信息</div>;

  return (
    <Card style={{ maxWidth: 600, margin: '32px auto' }}>
      <CardMedia
        component="img"
        height="300"
        image={detail.image}
        alt={detail.name}
      />
      <CardContent>
        <Typography variant="h4">{detail.name}</Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          {detail.description}
        </Typography>
        <Rating value={detail.rating} precision={0.1} readOnly />
        <Typography variant="body2" style={{ marginTop: 16 }}>
          {detail.details}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default AttractionDetails;