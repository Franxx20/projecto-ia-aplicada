// Health check endpoint para Docker healthcheck
export async function GET() {
  return Response.json(
    { 
      status: 'healthy',
      service: 'frontend',
      timestamp: new Date().toISOString()
    },
    { status: 200 }
  );
}
