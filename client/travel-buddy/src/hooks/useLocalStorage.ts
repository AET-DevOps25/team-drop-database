import React, { useState, useEffect } from "react";

const getLocalValue = <T>(key: string, initValue: T): T => {
    if (typeof window === 'undefined') return initValue;

    try {
        const localValue = localStorage.getItem(key);
        if (localValue !== null) {
            return JSON.parse(localValue) as T;
        }
    } catch (error) {
        console.error(`Error parsing localStorage key "${key}":`, error);
    }

    if (initValue instanceof Function) {
        return initValue();
    }

    return initValue;
};

const useLocalStorage = <T,>(key: string, initValue: T): [T, React.Dispatch<React.SetStateAction<T>>] => {
    const [value, setValue] = useState<T>(() => getLocalValue(key, initValue));

    useEffect(() => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error(`Error setting localStorage key "${key}":`, error);
        }
    }, [key, value]);

    return [value, setValue];
};

export default useLocalStorage;
