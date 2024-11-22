const API_BASE_URL = "http://localhost:8000";

export interface Article {
  url: string;
  title: string;
  content: string;
  publish_date: string;
}

export interface Summary {
  article: Article;
  summary: string;
  audio_path: string;
}

export interface Voice {
  id: string;
  name: string;
}

export interface Settings {
  ttsProvider: string;
  voice: string;
  neetModel: string;
  summarizerModel: string;
  rssFeeds: string[];
  autoPlay: boolean;
  processInterval: number;
}

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "An error occurred" }));
    throw new Error(error.detail || "An error occurred");
  }
  return response.json();
}

export async function getArticles(date?: string): Promise<{ [key: string]: Article }> {
  const url = date ? `${API_BASE_URL}/articles?filter_date=${date}` : `${API_BASE_URL}/articles`;
  const response = await fetch(url);
  return handleResponse(response);
}

const cache = new Map();
const pendingRequests = new Map();

async function fetchWithCache<T>(key: string, fetcher: () => Promise<T>, ttl = 60000): Promise<T> {
  if (cache.has(key)) {
    const { data, timestamp } = cache.get(key);
    if (Date.now() - timestamp < ttl) {
      return data;
    }
  }

  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }

  const request = fetcher().then(data => {
    cache.set(key, { data, timestamp: Date.now() });
    pendingRequests.delete(key);
    return data;
  });

  pendingRequests.set(key, request);
  return request;
}

export async function getSummaries(): Promise<{ [key: string]: Summary }> {
  return fetchWithCache('summaries', async () => {
    const response = await fetch(`${API_BASE_URL}/summaries`);
    return handleResponse(response);
  });
}

export async function getVoices(provider: string): Promise<Voice[]> {
  const response = await fetch(`${API_BASE_URL}/voices/${provider}`);
  const voices = await handleResponse(response);
  return voices.map((v: [string, string]) => ({
    id: v[0],
    name: v[1]
  }));
}

export async function getSettings(): Promise<Settings> {
  const response = await fetch(`${API_BASE_URL}/settings`);
  return handleResponse(response);
}

export async function updateSettings(settings: Settings): Promise<Settings> {
  const response = await fetch(`${API_BASE_URL}/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  return handleResponse(response);
}

export async function startProcessing(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/process`, {
    method: "POST",
  });
  await handleResponse(response);
}
