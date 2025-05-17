export interface SearchResult {
  id: string;
  title: string;
  description?: string;
  branch: string;
  lastUpdate: string;
  state: DocumentState;
  totalTokens: number;
  totalSnippets: number;
  totalPages: number;
  stars: number;
}

export interface SearchResponse {
  results: SearchResult[];
}

// Version state is still needed for validating search results
export type DocumentState = "initial" | "finalized" | "error" | "delete";
