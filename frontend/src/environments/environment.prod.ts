export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com/api/v1',
  appName: 'Plantitas AI',
  version: '1.0.0',
  features: {
    imageUpload: true,
    aiIdentification: true,
    userRegistration: true
  },
  upload: {
    maxFileSizeMB: 10,
    allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
    allowedExtensions: ['jpg', 'jpeg', 'png', 'gif', 'webp']
  },
  ui: {
    itemsPerPage: 12,
    debounceTimeMs: 300,
    toastDurationMs: 5000
  }
};