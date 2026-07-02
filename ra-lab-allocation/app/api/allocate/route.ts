import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const coursesFile = formData.get('courses') as File;
    const rasFile = formData.get('ras') as File;

    if (!coursesFile || !rasFile) {
      return NextResponse.json({ error: 'Missing files' }, { status: 400 });
    }

    // Use environment variable or fallback to localhost
    // Remove trailing slash if present to avoid double slashes
    const backendBaseUrl = (process.env.BACKEND_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
    const apiUrl = `${backendBaseUrl}/allocate`;
    const apiKey = process.env.API_KEY;

    const apiFormData = new FormData();
    apiFormData.append('courses', coursesFile);
    apiFormData.append('ras', rasFile);

    const headers: HeadersInit = {};
    if (apiKey) {
      headers['x-api-key'] = apiKey;
    }

    console.log(`Sending allocation request to: ${apiUrl}`);

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: headers,
      body: apiFormData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API error: ${response.status}`, errorText);
      return NextResponse.json(
        { error: `Backend API error: ${response.status}`, details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (err) {
    console.error('Error during allocation:', err);
    return NextResponse.json({ error: 'Server error', details: String(err) }, { status: 500 });
  }
}
