import {axiosAttr} from "./axios";

export interface Location {
    latitude: number;
    longitude: number;
    address?: string;
}

export interface City {
    id: number;
    name: string;
    country?: string;
}

export interface OpeningHours {
    dayOfWeek: string;
    open: string;
    close: string;
}

export interface Attraction {
    id?: number; // Present when the entity already exists
    name: string;
    description: string;
    location: Location;
    city: City;
    openingHours: OpeningHours[];
    photos: string[];
    website?: string;
}
export interface CreateAttractionRequest {
    name: string;
    description: string;
    location: string;
    imageUrl?: string;
}

export interface Page<T> {
    content: T[];
    pageable: {
        pageNumber: number;
        pageSize: number;
        offset: number;
        paged: boolean;
        unpaged: boolean;
        sort: {
            sorted: boolean;
            unsorted: boolean;
            empty: boolean;
        };
    };
    totalPages: number;
    totalElements: number;
    last: boolean;
    first: boolean;
    size: number;
    number: number;
    sort: {
        sorted: boolean;
        unsorted: boolean;
        empty: boolean;
    };
    numberOfElements: number;
    empty: boolean;
}

export interface PaginationParams {
    page?: number; // default 0
    size?: number; // default 10
    sortBy?: string; // default 'name'
}

const END_POINT = '/attractions';

/**
 * Generic paginated GET helper.
 * @param relativePath Path appended to axiosAttr.baseURL.
 */
const getPaginated = async <T>(
    relativePath: string,
    params: PaginationParams = {}
): Promise<Page<T>> => {
    const { page = 0, size = 10, sortBy = 'name' } = params;
    const res = await axiosAttr.get<Page<T>>(relativePath, {
        params: { page, size, sortBy },
    });
    return res.data;
};

/**
 * Fetch all attractions.
 * An empty string means axiosAttr.baseURL itself (already includes /attractions).
 */
export const getAllAttractions = (params?: PaginationParams) =>
    getPaginated<Attraction>(END_POINT, params);

/**
 * Fetch attractions in a specific city.
 */
export const getAttractionsByCity = (city: string, params?: PaginationParams) =>
    getPaginated<Attraction>(`${END_POINT}/city/${encodeURIComponent(city)}`, params);

/**
 * Fetch a single attraction by name.
 */
export const getAttractionByName = async (
    name: string
): Promise<Attraction> => {
    const res = await axiosAttr.get<Attraction>(`${END_POINT}/${encodeURIComponent(name)}`);
    return res.data;
};

/**
 * Fetch a single attraction by id.
 */
export const getAttractionById = async (
    id: number
): Promise<Attraction> => {
    const res = await axiosAttr.get<Attraction>(`${END_POINT}/id/${id}`);
    return res.data;
};

/**
 * Create a new attraction.
 */
export const createAttraction = async (
    attraction: Omit<Attraction, 'id'>
): Promise<void> => {
    await axiosAttr.post(END_POINT, attraction);
};

/**
 * Delete an attraction (DELETE /attractions).
 * The backend expects the entity in the request body.
 */
export const deleteAttraction = async (
    attraction: Attraction
): Promise<void> => {
    await axiosAttr.delete(END_POINT, { data: attraction });
};