import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

// ── Search (GET) ──────────────────────────────────────────────────────────────
export const searchGlossary      = (term, limit) => api.get('/glossary',         { params: { term, limit } });
export const searchAmbiguousTerms = (term, limit) => api.get('/ambiguity',        { params: { term, limit } });
export const searchEnGu          = (term, limit) => api.get('/aliases/en-gu',    { params: { term, limit } });
export const searchEnglish       = (term, limit) => api.get('/aliases/english',  { params: { term, limit } });
export const searchForbidden     = (term, limit) => api.get('/forbidden',        { params: { term, limit } });
export const searchPreferred     = (term, limit) => api.get('/preferred',        { params: { term, limit } });
export const searchSchemes       = (term, limit) => api.get('/schemes',          { params: { term, limit } });

// ── POST (full snapshot) ──────────────────────────────────────────────────────
export const postGlossary   = (body) => api.post('/glossary',   body);
export const postForbidden  = (body) => api.post('/forbidden',  body);
export const postPreferred  = (body) => api.post('/preferred',  body);
export const postSchemes    = (body) => api.post('/schemes',    body);

// ── PATCH (edit existing key) ─────────────────────────────────────────────────
export const patchGlossary  = (body) => api.patch('/glossary',  body);
export const patchForbidden = (body) => api.patch('/forbidden',  body);
export const patchPreferred = (body) => api.patch('/preferred',  body);
export const patchSchemes   = (body) => api.patch('/schemes',    body);

// ── DELETE (map config key) ───────────────────────────────────────────────────
export const deleteGlossary  = (body) => api.delete('/glossary',  { data: body });
export const deleteForbidden = (body) => api.delete('/forbidden', { data: body });
export const deletePreferred = (body) => api.delete('/preferred', { data: body });
export const deleteSchemes   = (body) => api.delete('/schemes',   { data: body });

// ── Ambiguous Terms ───────────────────────────────────────────────────────────
export const patchAmbiguousTerms = (body) => api.patch('/ambiguity', body);

// ── Aliases en-gu ─────────────────────────────────────────────────────────────
export const patchAliasEnGu   = (body) => api.patch('/aliases/en-gu', body);
export const putAliasEnGu     = (body) => api.put('/aliases/en-gu',   body);
export const deleteAliasEnGu  = (body) => api.delete('/aliases/en-gu', { data: body });

// ── Aliases english ───────────────────────────────────────────────────────────
export const patchAliasEnglish  = (body) => api.patch('/aliases/english', body);
export const putAliasEnglish    = (body) => api.put('/aliases/english',   body);
export const deleteAliasEnglish = (body) => api.delete('/aliases/english', { data: body });

// ── Config management ─────────────────────────────────────────────────────────
export const reloadConfigs   = ()     => api.post('/configs/reload');
export const rollbackConfig  = (body) => api.post('/configs/rollback', body);
export const getVersions     = (configType) => api.get('/configs/versions', { params: { config_type: configType } });
export const getAllConfigs    = ()     => api.get('/configs');
