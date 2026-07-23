export const API_CONFIG = {
    BASE_URL: process.env.NEXT_PUBLIC_API_URL,
    VERSION: "v1",
} as const;
export const getBaseUrl = (): string => {
    if (process.env.NODE_ENV === 'production') {
        return `/api/${API_CONFIG.VERSION}`;
    } else {
        return `${API_CONFIG.BASE_URL}/api/${API_CONFIG.VERSION}`;
    }
}