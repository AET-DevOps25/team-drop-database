import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  CardMedia,
  CardContent,
  Typography,
  Rating,
  CircularProgress,
} from '@mui/material';
import { getAttractionById } from '../api/attrac';

interface AttractionDetail {
  name: string;
  image: string;
  description: string;
  openingHours?: string;
  location?: string;
  website?: string;
}

const AttractionDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [detail, setDetail] = useState<AttractionDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const data = await getAttractionById(Number(id));

        const transformed: AttractionDetail = {
          name: data.name,
          image: data.photos?.[0] ?? '',
          description: data.description,
          openingHours: Array.isArray(data.openingHours)
            ? data.openingHours
              .map((h: any) => `${h.dayOfWeek} ${h.open}–${h.close}`)
              .join(', ')
            : '',
          location: data.location?.address ?? '',
          website: data.website,
        };

        setDetail(transformed);
      } catch (err: any) {
        console.error(err);
        setError(err?.message ?? 'Loading attraction failed');
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  if (loading)
    return (
      <div style={{ textAlign: 'center', marginTop: 40 }}>
        <CircularProgress />
      </div>
    );

  if (error || !detail)
    return (
      <div style={{ textAlign: 'center', marginTop: 40 }}>
        {error || 'Attraction not found'}
      </div>
    );
  return (
    <Card style={{ maxWidth: 600, margin: '32px auto', borderRadius: 12, boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
      <CardMedia
        component="img"
        height="300"
        image={detail.image}
        alt={detail.name}
        style={{ objectFit: 'cover' }}
      />
      <CardContent>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          {detail.name}
        </Typography>

        {/* <Rating value={detail.rating} precision={0.1} readOnly />
        <Typography variant="body1" color="text.secondary" gutterBottom style={{ marginTop: 8 }}>
          {detail.description}
        </Typography>

        <Typography variant="body2" style={{ marginTop: 16, lineHeight: 1.7 }}>
          {detail.details}
        </Typography> */}

        <div style={{ marginTop: 24 }}>
          {detail.openingHours && (
            <Typography variant="body2" color="text.secondary">
              <strong>Openning Hours: </strong> {detail.openingHours}
            </Typography>
          )}
          {detail.location && (
            <Typography variant="body2" color="text.secondary">
              <strong>Location: </strong> {detail.location}
            </Typography>
          )}
          {detail.website && (
            <Typography variant="body2" color="text.secondary">
              <strong>Website: </strong>{' '}
              <a href={detail.website} target="_blank" rel="noopener noreferrer">
                {detail.website}
              </a>
            </Typography>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default AttractionDetails;
