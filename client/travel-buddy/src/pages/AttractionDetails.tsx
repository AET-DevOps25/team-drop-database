import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  CardMedia,
  CardContent,
  Typography,
  CircularProgress,
} from '@mui/material';
import { getAttractionById } from '../api/attrac';
import {Attraction} from "../dto/attraction/Attraction";
import AttractionMap from "../component/attraction/AttractionMap";

const AttractionDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [attraction, setAttraction] = useState<Attraction | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const data = await getAttractionById(Number(id));

        const transformed: Attraction = {
          id: data.id,
          name: data.name,
          description: data.description,
          location: data.location,
          city: data.city,
          photos: data.photos,
          openingHours: data.openingHours,
          website: data.website,
        };

        setAttraction(transformed);
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

  if (error || !attraction)
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
        image={attraction.photos[0]}
        alt={attraction.name}
        style={{ objectFit: 'cover' }}
      />
      <CardContent>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          {attraction.name}
        </Typography>

        {attraction.description && (
          <Typography
            variant="body1"
            color="text.secondary"
            gutterBottom
            style={{ marginTop: 16 }}
          >
            {attraction.description}
          </Typography>
        )}
        <div style={{ marginTop: 24 }}>
          {Array.isArray(attraction.openingHours) && attraction.openingHours.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Opening Hours:</strong>
              </Typography>
              {attraction.openingHours.map((line, idx) => (
                <Typography
                  key={idx}
                  variant="body2"
                  color="text.secondary"
                  style={{ marginLeft: 12 }}
                >
                  {line.day + "- from: " + line.fromTime + " to: " + line.toTime}
                </Typography>
              ))}
            </div>
          )}
          {attraction.location && (
            <Typography variant="body2" color="text.secondary">
              <strong>Location: </strong> {attraction.location.address}
            </Typography>
          )}
          {attraction.website && (
            <Typography variant="body2" color="text.secondary">
              <strong>Website: </strong>{' '}
              <a href={attraction.website} target="_blank" rel="noopener noreferrer">
                {attraction.website}
              </a>
            </Typography>
          )}

          {attraction.location && (
              <AttractionMap
                  lat={Number(attraction.location.latitude)}
                  lng={Number(attraction.location.longitude)}
                  name={attraction.name}
              />
          )}

        </div>
      </CardContent>
    </Card>
  );
};

export default AttractionDetails;
