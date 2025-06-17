import axios from 'axios';

const BASE_AUTH_URL = process.env.REACT_APP_BASE_AUTH_URL!;
const BASE_ATTR_URL = process.env.REACT_APP_BASE_ATTR_URL!;
const BASE_USER_URL = process.env.REACT_APP_BASE_USER_URL!;

export const axiosAuth = axios.create({
    baseURL: BASE_AUTH_URL,
});

export const axiosAttr = axios.create({
    baseURL: BASE_ATTR_URL,
});

export const axiosUser = axios.create({
    baseURL: BASE_USER_URL,
});

export const axiosPrivate = axios.create({
    baseURL: BASE_AUTH_URL,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true
});