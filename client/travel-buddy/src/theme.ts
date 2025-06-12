'use client';
import { createTheme } from '@mui/material/styles';

const colors = {
    color1: '#FF6242',
    color2: '#FF8142',
    color3: '#FFA142',
    color4: '#FFD642',
    color5: '#FFE99C',
}

const theme = createTheme({
    // use CSS theme variables
   
    typography: {
        fontFamily: 'var(--font-roboto)',
    },
    palette:{
        primary: {
            main: colors.color2,
        },
        secondary: {
            main: colors.color3,
        }
    },
});

export default theme;
