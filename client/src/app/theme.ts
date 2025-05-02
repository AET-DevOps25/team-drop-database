'use client';
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    // use CSS theme variables
    cssVariables: true,
    typography: {
        fontFamily: 'var(--font-roboto)',
    },
});

export default theme;
