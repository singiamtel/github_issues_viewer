// Get the GitHub token from the page
let githubToken = null;

// Register the service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('GitHub proxy service worker registered:', registration);
      })
      .catch(error => {
        console.error('GitHub proxy service worker registration failed:', error);
      });
  });
}

// Listen for messages from the service worker
navigator.serviceWorker.addEventListener('message', event => {
  if (event.data.type === 'GET_GITHUB_TOKEN') {
    // Send the token back to the service worker
    event.ports[0].postMessage({ token: githubToken });
  }
});

// Function to set the GitHub token
function setGitHubToken(token) {
  githubToken = token;
}

// Function to create a proxied GitHub URL
function getProxiedGitHubUrl(originalUrl) {
  const githubPrefix = 'https://github.com/';
  const rawGithubPrefix = 'https://raw.githubusercontent.com/';
  return originalUrl;
  
  if (originalUrl.startsWith(githubPrefix)) {
    // Check if it's an image URL (ends with common image extensions)
    if (/\.(jpg|jpeg|png|gif|svg)$/i.test(originalUrl)) {
      // Convert github.com URLs to raw.githubusercontent.com for images
      const path = originalUrl.slice(githubPrefix.length);
      return `${rawGithubPrefix}${path}?token=${githubToken}`;
    }
    const path = originalUrl.slice(githubPrefix.length);
    return `/github-proxy/${path}`;
  }
  return originalUrl;
} 