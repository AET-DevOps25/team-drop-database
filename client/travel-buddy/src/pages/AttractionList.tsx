// src/pages/AttractionList.tsx
// A Material‑UI page that consumes the attraction API.
// Added full pagination support (page selector at the bottom) so the user can
// browse page 1, 2, 3 … in their entirety.

import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Box,
    Card,
    CardActionArea,
    CardContent,
    CardMedia,
    Chip,
    CircularProgress,
    Grid,
    InputAdornment,
    Pagination,
    TextField,
    Typography,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

import {
    getAllAttractions,
    Attraction,
    Page as PageResponse,
} from '../api/attrac';

/**
 * Helper that returns the first photo of an attraction or a random Unsplash fallback.
 */
const getAttractionImage = (a: Attraction) =>
    a.photos?.[0] ??
    `https://placehold.co/800x600`;

const PAGE_SIZE = 12; // number of attractions per page

const AttractionList: React.FC = () => {
    /* -------------------------------- state -------------------------------- */
    const [query, setQuery] = useState('');
    const [attractions, setAttractions] = useState<Attraction[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(0); // zero‑based index used by the backend
    const [totalPages, setTotalPages] = useState(1);

    /* ------------------------------- fetching ------------------------------ */
    useEffect(() => {
        setLoading(true);
        getAllAttractions({ page, size: PAGE_SIZE })
            .then((res: PageResponse<Attraction>) => {
                setAttractions(res.content);
                setTotalPages(res.totalPages || 1);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message ?? 'Failed to fetch attractions');
                setLoading(false);
            });
    }, [page]);

    /* --------------------------- memoised helpers --------------------------- */
    const filteredAttractions = useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return attractions;
        return attractions.filter(
            (a) =>
                a.name.toLowerCase().includes(q) ||
                a.city?.name?.toLowerCase().includes(q)
        );
    }, [query, attractions]);

    const derivedCities = useMemo(() => {
        const seen: Record<string, Attraction> = {};
        attractions.forEach((a) => {
            if (a.city) seen[a.city.name] = a;
        });
        return Object.entries(seen).map(([name, attr]) => ({
            id: name,
            name,
            image: getAttractionImage(attr),
        }));
    }, [attractions]);

    /* ------------------------------- renders ------------------------------- */
    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box sx={{ p: 4, textAlign: 'center', color: 'error.main' }}>{error}</Box>
        );
    }

    return (
        <Box sx={{ p: 4 }}>
            {/* Search bar */}
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

            {/* City bar */}
            <Typography variant="h4" gutterBottom fontWeight={700}>
                Things to do wherever you’re going
            </Typography>

            <Box
                sx={{
                    display: 'flex',
                    gap: 3,
                    overflowX: 'auto',
                    pb: 2,
                    mb: 4,
                    // Left‑align items on small screens so the first card is fully visible.
                    justifyContent: { xs: 'flex-start', md: 'center' },
                    pl: { xs: 1 }, // slight padding so the first card isn't flush with the edge
                }}
            >
                {derivedCities.map((c) => (
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
                            to={`/city/${encodeURIComponent(c.name)}`}
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

            {/* Attraction grid */}
            <Typography variant="h4" gutterBottom fontWeight={700}>
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
                                sx={{
                                    '&:hover .MuiCardMedia-root': { transform: 'scale(1.15)' },
                                }}
                            >
                                <CardMedia
                                    component="img"
                                    height="180"
                                    image={getAttractionImage(a)}
                                    alt={a.name}
                                    sx={{
                                        transition: 'transform .3s ease',
                                        transformOrigin: 'center',
                                    }}
                                />
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Chip
                                        label={a.city?.name ?? 'Unknown'}
                                        size="small"
                                        sx={{ mb: 1 }}
                                    />
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
                                </CardContent>
                            </CardActionArea>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Pagination control */}
            {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
                    <Pagination
                        count={totalPages}
                        page={page + 1} // MUI is 1‑based
                        onChange={(_, value) => setPage(value - 1)}
                        color="primary"
                        shape="rounded"
                        showFirstButton
                        showLastButton
                    />
                </Box>
            )}
        </Box>
    );
};

export default AttractionList;
