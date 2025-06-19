import {axiosAttr} from "./axios";
import {Attraction} from "../dto/attraction/Attraction";
import {Page} from "../dto/utils/Page";

interface PaginationParams {
    page?: number; // default 0
    size?: number; // default 10
    sortBy?: string; // default 'name'
}

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
    getPaginated<Attraction>("/attractions", params);

/**
 * Fetch attractions in a specific city.
 */
export const getAttractionsByCity = (city: string, params?: PaginationParams) =>
    getPaginated<Attraction>(`/attractions/city/${encodeURIComponent(city)}`, params);

/**
 * Fetch a single attraction by name.
 */
export const getAttractionByName = async (
    name: string
): Promise<Attraction> => {
    const res = await axiosAttr.get<Attraction>(`/attractions/${encodeURIComponent(name)}`);
    return res.data;
};

/**
 * Fetch a single attraction by id.
 */
export const getAttractionById = async (
    id: number
): Promise<Attraction> => {
    const res = await axiosAttr.get<Attraction>(`/attractions/id/${id}`);
    return res.data;
};