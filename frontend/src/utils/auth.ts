import { jwtDecode } from 'jwt-decode';

interface JwtPayload {
  exp: number;
  iat: number;
  sub: string;
  [key: string]: any;
}

/**
 * Checks if a JWT token is expired
 * @param token The JWT token to check
 * @returns boolean True if token is expired or invalid, false otherwise
 */
export const isTokenExpired = (token: string | null): boolean => {
  if (!token) return true;
  
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    const currentTime = Date.now() / 1000; // Convert to seconds
    
    // Check if token is expired (with 30 second buffer)
    return decoded.exp < currentTime - 30;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true; // Consider invalid tokens as expired
  }
};

/**
 * Extracts the expiration time from a JWT token
 * @param token The JWT token
 * @returns Date | null The expiration date or null if token is invalid
 */
export const getTokenExpiration = (token: string): Date | null => {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return new Date(decoded.exp * 1000); // Convert to milliseconds
  } catch (error) {
    console.error('Error getting token expiration:', error);
    return null;
  }
};

/**
 * Extracts the user data from a JWT token
 * @param token The JWT token
 * @returns The decoded user data or null if token is invalid
 */
export const getUserFromToken = <T = any>(token: string): T | null => {
  try {
    const decoded = jwtDecode<JwtPayload & { user: T }>(token);
    return decoded.user || (decoded as unknown as T);
  } catch (error) {
    console.error('Error getting user from token:', error);
    return null;
  }
};

/**
 * Checks if a token will expire soon (within the specified number of seconds)
 * @param token The JWT token
 * @param seconds The number of seconds to check for imminent expiration
 * @returns boolean True if token will expire soon, false otherwise
 */
export const isTokenExpiringSoon = (token: string, seconds = 300): boolean => {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    const currentTime = Date.now() / 1000; // Convert to seconds
    const timeUntilExpiry = decoded.exp - currentTime;
    
    return timeUntilExpiry <= seconds;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true; // Consider invalid tokens as expiring soon
  }
};

/**
 * Parses a JWT token without verification
 * @param token The JWT token to parse
 * @returns The decoded token payload or null if invalid
 */
export const parseJwt = <T = any>(token: string): T | null => {
  try {
    return jwtDecode<T>(token);
  } catch (error) {
    console.error('Error parsing JWT:', error);
    return null;
  }
};

/**
 * Extracts the token from an Authorization header
 * @param header The Authorization header value (e.g., "Bearer eyJhbGciOi...")
 * @returns The token or null if invalid format
 */
export const getTokenFromHeader = (header: string | null | undefined): string | null => {
  if (!header) return null;
  
  const parts = header.split(' ');
  if (parts.length === 2 && parts[0].toLowerCase() === 'bearer') {
    return parts[1];
  }
  
  return null;
};

/**
 * Creates an Authorization header with a Bearer token
 * @param token The JWT token
 * @returns The Authorization header value
 */
export const createAuthHeader = (token: string | null): string | undefined => {
  return token ? `Bearer ${token}` : undefined;
};

/**
 * Validates a JWT token's structure and expiration
 * @param token The JWT token to validate
 * @returns boolean True if token is valid, false otherwise
 */
export const validateToken = (token: string | null): boolean => {
  if (!token) return false;
  
  try {
    // Check token structure (should have 3 parts separated by dots)
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    
    // Check if token is expired
    return !isTokenExpired(token);
  } catch (error) {
    console.error('Error validating token:', error);
    return false;
  }
};
