import React, { useState, useMemo } from 'react';
import {Link} from 'react-router-dom';
import {
    Card,
    CardActionArea,
    CardMedia,
    CardContent,
    Typography,
    Rating,
    Grid,
    Chip,
    Box,
    TextField,
    InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const cities = [
    {
        id: 'c1',
        name: 'Washington, DC',
        image:
            'https://images.unsplash.com/photo-1557160854-e1e89fdd3286?auto=format&fit=crop&w=400&q=80',
    },
    {
        id: 'c2',
        name: 'London',
        image:
            'https://images.unsplash.com/photo-1486299267070-83823f5448dd?auto=format&fit=crop&w=400&q=80',
    },
    {
        id: 'c3',
        name: 'Charleston',
        image:
            'https://images.unsplash.com/photo-1619892127776-08a763bfe34c?auto=format&fit=crop&w=400&q=80',
    },
    {
        id: 'c4',
        name: 'Paris',
        image:
            'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=400&q=80',
    },
    {
        id: 'c5',
        name: 'New York City',
        image:
            'https://images.unsplash.com/photo-1500916434205-0c77489c6cf7?auto=format&fit=crop&w=400&q=80',
    },
    {
        id: 'c6',
        name: 'New Orleans',
        image:
            'https://images.unsplash.com/photo-1471623432079-b009d30b6729?auto=format&fit=crop&w=400&q=80',
    },
];

const attractions = [
    {
        id: '1',
        name: 'The Forbidden City',
        image:
            'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
        description:
            'China’s most famous imperial palace with a long and rich history.',
        rating: 4.8,
        location: 'Beijing',
    },
    {
        id: '2',
        name: 'The Great Wall',
        image:
            'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=400&q=80',
        description:
            'One of the Seven Wonders of the World, an awe-inspiring ancient defense structure.',
        rating: 4.7,
        location: 'Hebei',
    },
];

const AttractionList: React.FC = () => {
    const [query, setQuery] = useState('');

    const filteredCities = useMemo(
        () =>
            cities.filter((c) =>
                c.name.toLowerCase().includes(query.trim().toLowerCase())
            ),
        [query]
    );

    const filteredAttractions = useMemo(
        () =>
            attractions.filter((a) =>
                a.name.toLowerCase().includes(query.trim().toLowerCase())
            ),
        [query]
    );

    return (
        <Box sx={{ p: 4 }}>
            {/* ======= Search Bar ======= */}
            <TextField
                placeholder="Search cities or attractions…"
                variant="outlined"
                fullWidth
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                sx={{ mb: 4 }}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <SearchIcon color="action" />
                        </InputAdornment>
                    ),
                }}
            />

            {/* ======= City Bar ======= */}
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
                Things to do wherever you&apos;re going
            </Typography>

            <Box
                sx={{
                    display: 'flex',
                    gap: 3,
                    overflowX: 'auto',
                    pb: 2,
                    mb: 4,
                }}
            >
                {filteredCities.map((c) => (
                    <Card
                        key={c.id}
                        sx={{
                            width: 220,
                            borderRadius: 3,
                            overflow: 'hidden',
                            flex: '0 0 auto',
                            boxShadow: 2,
                        }}
                    >
                        <CardActionArea
                            component={Link}
                            to={`/city/${c.id}`}
                            sx={{ '&:hover .city-img': { transform: 'scale(1.15)' } }}
                        >
                            <CardMedia
                                component="img"
                                className="city-img"
                                image={c.image}
                                alt={c.name}
                                sx={{
                                    height: 280,
                                    width: '100%',
                                    objectFit: 'cover',
                                    transition: 'transform .3s ease',
                                }}
                            />
                            <Typography
                                variant="subtitle1"
                                sx={{
                                    position: 'absolute',
                                    top: 12,
                                    left: 12,
                                    bgcolor: '#00214d',
                                    color: '#fff',
                                    px: 1.5,
                                    py: 0.5,
                                    borderRadius: 1,
                                    fontWeight: 700,
                                    lineHeight: 1.2,
                                }}
                            >
                                {c.name}
                            </Typography>
                        </CardActionArea>
                    </Card>
                ))}
            </Box>

            {/* ======= Attraction Grid ======= */}
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
                Popular Attractions
            </Typography>

            <Grid container spacing={4} justifyContent="center">
                {filteredAttractions.map((a) => (
                    <Grid key={a.id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                        <Card
                            sx={{
                                overflow: 'hidden',
                                borderRadius: 2,
                                boxShadow: 3,
                                transition: '.3s',
                                '&:hover': { boxShadow: 6 },
                            }}
                        >
                            <CardActionArea
                                component={Link}
                                to={`/attractions/${a.id}`}
                                sx={{ '&:hover .MuiCardMedia-root': { transform: 'scale(1.15)' } }}
                            >
                                <CardMedia
                                    component="img"
                                    height="180"
                                    image={a.image}
                                    alt={a.name}
                                    sx={{ transition: 'transform .3s ease', transformOrigin: 'center' }}
                                />
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Chip label={a.location} size="small" sx={{ mb: 1 }} />
                                    <Typography variant="h6" gutterBottom>
                                        {a.name}
                                    </Typography>
                                    <Typography
                                        variant="body2"
                                        color="text.secondary"
                                        gutterBottom
                                        sx={{
                                            display: '-webkit-box',
                                            WebkitLineClamp: 2,
                                            WebkitBoxOrient: 'vertical',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                        }}
                                    >
                                        {a.description}
                                    </Typography>
                                    <Rating value={a.rating} precision={0.1} readOnly size="small" />
                                </CardContent>
                            </CardActionArea>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

export default AttractionList;