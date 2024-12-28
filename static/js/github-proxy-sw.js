self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Only intercept GitHub asset requests
  if (url.pathname.startsWith('/github-proxy/')) {
    event.respondWith(handleGitHubProxy(event.request));
  }
});

async function handleGitHubProxy(request) {
  try {
    // Extract the GitHub path from the URL
    const url = new URL(request.url);
    const githubPath = url.pathname.replace('/github-proxy/', '');
    
    // Get the GitHub token from the page
    const clients = await self.clients.matchAll();
    const client = clients[0];
    const message = await new Promise(resolve => {
      const channel = new MessageChannel();
      channel.port1.onmessage = event => resolve(event.data);
      client.postMessage({ type: 'GET_GITHUB_TOKEN' }, [channel.port2]);
    });
    
    const githubToken = message.token;
    
    // Make the authenticated request to GitHub
    const githubUrl = `https://github.com/${githubPath}`;
    console.log('githubUrl', githubUrl);
    const response = await fetch(githubUrl, {
      headers: {
        'Authorization': `token ${githubToken}`,
        'Accept': 'application/vnd.github.v3.raw'
      }
    });
    
    if (!response.ok) {
      throw new Error(`GitHub API responded with ${response.status}`);
    }
    
    return response;
  } catch (error) {
    console.error('Error proxying GitHub asset:', error);
    return new Response(`Error proxying GitHub asset: ${error.message}`, {
      status: 500,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
} 