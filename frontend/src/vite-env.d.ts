/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_ENABLE_AI_FEATURES?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
