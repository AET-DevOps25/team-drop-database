import {City} from "./City";
import {OpeningHours} from "./OpeningHours";
import {Location} from "./Location";

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