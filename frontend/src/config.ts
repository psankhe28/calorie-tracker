// Set VITE_ENABLE_AI_FEATURES=false (in .env / docker-compose) to hide the chat assistant and
// the photo-scan control -- e.g. while the OPENAI_API_KEY has no usable credits. Bulk PDF import
// still shows, since its primary path (tabular parsing) doesn't depend on AI at all.
export const AI_FEATURES_ENABLED = import.meta.env.VITE_ENABLE_AI_FEATURES !== "false";
