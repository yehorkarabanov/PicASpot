/**
 * Development Host Configuration Script
 *
 * Automatically detects the Docker server IP address and configures
 * the Expo app to connect to the correct API endpoint.
 *
 * Features:
 * - Detects primary network interface with default gateway
 * - Falls back to production URL if no local IP is detected
 * - Creates/updates .env.local with EXPO_PUBLIC_API_URL
 * - Supports Windows, macOS, and Linux
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const { execSync } = require('child_process');

// ============================================================================
// IP Detection Functions
// ============================================================================

/**
 * Detect the Docker server IP address
 * Prioritizes host machine's local IP for mobile device connectivity
 * @returns {string|null} Detected IP address or null if detection fails
 */
function detectDockerServerIP() {
  try {
    // Primary method: Use host machine's local IP
    const localIP = findLocalIPv4();
    if (localIP && localIP !== '127.0.0.1') {
      console.log('Using host machine IP for Docker:', localIP);
      return localIP;
    }

    // Fallback: Try docker-machine (Docker Toolbox)
    try {
      const dockerIP = execSync('docker-machine ip default', { encoding: 'utf8' }).trim();
      if (dockerIP && /^\d+\.\d+\.\d+\.\d+$/.test(dockerIP)) {
        console.log('Docker IP detected via docker-machine:', dockerIP);
        return dockerIP;
      }
    } catch (e) {
      // docker-machine not available
    }

    // Last resort: Docker bridge network (usually internal only)
    try {
      const dockerInfo = execSync('docker network inspect bridge', { encoding: 'utf8' });
      const match = dockerInfo.match(/"Gateway":\s*"(\d+\.\d+\.\d+\.\d+)"/);
      if (match?.[1]) {
        console.log('Docker IP detected via bridge network:', match[1]);
        return match[1];
      }
    } catch (e) {
      // Docker network inspect failed
    }

    console.log('Could not detect Docker IP, defaulting to localhost');
    return '127.0.0.1';
  } catch (error) {
    console.error('Error detecting Docker IP:', error.message);
    return null;
  }
}

/**
 * Find the primary local IPv4 address
 * Prioritizes interface with default gateway (main network connection)
 * @returns {string} Primary IPv4 address or '127.0.0.1'
 */
function findLocalIPv4() {
  // Windows: Parse ipconfig output to find interface with default gateway
  if (process.platform === 'win32') {
    try {
      const ipconfigOutput = execSync('ipconfig', { encoding: 'utf8' });
      const primaryIP = findPrimaryIPFromIpconfig(ipconfigOutput);
      if (primaryIP) {
        console.log('Found primary network interface:', primaryIP);
        return primaryIP;
      }
    } catch (e) {
      console.log('Could not run ipconfig, using fallback method');
    }
  }

  // Fallback: Use os.networkInterfaces()
  const nets = os.networkInterfaces();
  const candidates = [];

  for (const interfaces of Object.values(nets)) {
    for (const net of interfaces) {
      if (net.family === 'IPv4' && !net.internal) {
        // Prioritize common local network ranges
        if (net.address.startsWith('192.168.') || net.address.startsWith('10.')) {
          candidates.unshift(net.address);
        } else if (!isDockerInternalIP(net.address)) {
          candidates.push(net.address);
        }
      }
    }
  }

  return candidates[0] || '127.0.0.1';
}

/**
 * Parse Windows ipconfig output to find primary IP
 * Looks for interface with both IPv4 address and default gateway
 * @param {string} ipconfigOutput - Output from ipconfig command
 * @returns {string|null} Primary IP address or null
 */
function findPrimaryIPFromIpconfig(ipconfigOutput) {
  const sections = ipconfigOutput.split(/\r?\n\r?\n/);

  for (const section of sections) {
    const ipMatch = section.match(/IPv4 Address[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)/);
    const gatewayMatch = section.match(/Default Gateway[.\s]*:\s*(\d+\.\d+\.\d+\.\d+)/);

    if (ipMatch?.[1] && gatewayMatch?.[1]) {
      const ip = ipMatch[1];
      if ((ip.startsWith('192.168.') || ip.startsWith('10.')) && !isDockerInternalIP(ip)) {
        return ip;
      }
    }
  }

  return null;
}

/**
 * Check if IP is in Docker's internal range (172.17.0.0 - 172.31.255.255)
 * @param {string} ip - IP address to check
 * @returns {boolean} True if IP is in Docker's internal range
 */
function isDockerInternalIP(ip) {
  const match = ip.match(/^172\.(\d+)\./);
  if (match) {
    const secondOctet = parseInt(match[1], 10);
    return secondOctet >= 17 && secondOctet <= 31;
  }
  return false;
}

// ============================================================================
// Environment File Functions
// ============================================================================

/**
 * Load and parse .env file
 * @param {string} envPath - Path to .env file
 * @returns {Object} Parsed environment variables
 */
function loadEnvFile(envPath) {
  if (!fs.existsSync(envPath)) {
    return {};
  }

  const content = fs.readFileSync(envPath, 'utf8');
  const env = {};

  content.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && !trimmed.startsWith('//')) {
      const [key, ...valueParts] = trimmed.split('=');
      if (key) {
        env[key.trim()] = valueParts.join('=').trim();
      }
    }
  });

  return env;
}

/**
 * Update or create .env.local file with new values
 * @param {string} envPath - Path to .env file
 * @param {Object} updates - Key-value pairs to update
 */
function updateEnvFile(envPath, updates) {
  let content = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf8') : '';

  for (const [key, value] of Object.entries(updates)) {
    const regex = new RegExp(`^${key}=.*$`, 'm');
    if (regex.test(content)) {
      content = content.replace(regex, `${key}=${value}`);
    } else {
      if (content.length > 0 && !content.endsWith('\n')) {
        content += '\n';
      }
      content += `${key}=${value}\n`;
    }
  }

  fs.writeFileSync(envPath, content, 'utf8');
}

// ============================================================================
// Main Execution
// ============================================================================

(function main() {
  console.log('=== Setting up development environment ===\n');

  // Detect Docker server IP
  const dockerIP = detectDockerServerIP();

  // Load configuration from .env
  const envPath = path.join(__dirname, '..', '.env');
  const envLocalPath = path.join(__dirname, '..', '.env.local');
  const env = loadEnvFile(envPath);

  const apiPreset = env.EXPO_API_PRESET || 'http://{{IP_ADDRESS}}/api';
  const prodServerUrl = env.EXPO_PROD_SERVER_URL || 'example.com';

  // Construct API URL
  let apiUrl;
  if (dockerIP && dockerIP !== '127.0.0.1') {
    apiUrl = apiPreset.replace('{{IP_ADDRESS}}', dockerIP);
    console.log('Development mode: Using detected IP');
    console.log('Detected IP:', dockerIP);
  } else {
    apiUrl = `https://${prodServerUrl}/api/v1`;
    console.log('Production mode: Using production server');
    console.log('Production URL:', prodServerUrl);
  }

  // Prepare updates
  const updates = { EXPO_PUBLIC_API_URL: apiUrl };
  if (dockerIP) {
    updates.DEV_HOST_IP = dockerIP;
  }

  // Write to .env.local
  console.log('\nConstructed API URL:', apiUrl);
  console.log('Writing to:', envLocalPath);

  try {
    updateEnvFile(envLocalPath, updates);
    console.log('\n✓ Successfully updated', envLocalPath);
    console.log('\nEnvironment variables set:');
    Object.entries(updates).forEach(([key, value]) => {
      console.log(`  ${key}=${value}`);
    });
  } catch (err) {
    console.error('\n✗ Failed to update .env.local:', err?.message || err);
    process.exit(2);
  }
})();

