import axios from 'axios';

const BASE_AUTH_URL = 'http://localhost:8081/auth-service/api/v1';

const BASE_ATTR_URL = 'http://localhost:8082/attraction-service/api/v1';

const BASE_USER_URL = 'http://localhost:8083/user-service/api/v1';

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