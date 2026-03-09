// Fallback to current origin if env variable is not set (useful for unified build)
export const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export const API_ENDPOINTS = {
    ALERTS: `${API_BASE_URL}/alerts`,
    EVENTS: `${API_BASE_URL}/events`,
    STATS: `${API_BASE_URL}/stats`,
    CAMERAS: `${API_BASE_URL}/cameras`,
    ARCHIVE_ANALYZE: `${API_BASE_URL}/archive/analyze`,
    ARCHIVE_STATUS: (jobId: string) => `${API_BASE_URL}/archive/status/${jobId}`,
    WATCHLIST: `${API_BASE_URL}/watchlist`,
    VIDEO_FEED: (camId: string) => `${API_BASE_URL}/video_feed/${camId}`,
    HEATMAP_FEED: (camId: string) => `${API_BASE_URL}/heatmap/${camId}`,
};
