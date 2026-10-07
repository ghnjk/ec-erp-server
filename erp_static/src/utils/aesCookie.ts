import CryptoJS from 'crypto-js';

/** 登录记住账户使用的固定 AES 口令 */
const AES_KEY = 'ec-erp-login-aes-key';

/** 记住账户 cookie 有效期：360 天 */
const COOKIE_MAX_AGE_SECONDS = 360 * 24 * 60 * 60;

export function encryptCookieValue(plain: string): string {
  return CryptoJS.AES.encrypt(plain, AES_KEY).toString();
}

export function decryptCookieValue(cipher: string): string {
  const bytes = CryptoJS.AES.decrypt(cipher, AES_KEY);
  return bytes.toString(CryptoJS.enc.Utf8);
}

function cookieName(suffix: 'user' | 'password'): string {
  return `${window.location.host}_${suffix}`;
}

function readCookie(name: string): string {
  const prefix = `${name}=`;
  const parts = document.cookie ? document.cookie.split(';') : [];
  for (let i = 0; i < parts.length; i += 1) {
    const item = parts[i].trim();
    if (item.indexOf(prefix) === 0) {
      return decodeURIComponent(item.substring(prefix.length));
    }
  }
  return '';
}

function writeCookie(name: string, value: string) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${COOKIE_MAX_AGE_SECONDS}`;
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; path=/; max-age=0`;
}

export function saveRememberedAccount(account: string, password: string) {
  writeCookie(cookieName('user'), encryptCookieValue(account));
  writeCookie(cookieName('password'), encryptCookieValue(password));
}

export function clearRememberedAccount() {
  deleteCookie(cookieName('user'));
  deleteCookie(cookieName('password'));
}

export function loadRememberedAccount(): { account: string; password: string } | null {
  const accountCipher = readCookie(cookieName('user'));
  const passwordCipher = readCookie(cookieName('password'));
  if (!accountCipher && !passwordCipher) {
    return null;
  }
  try {
    const account = accountCipher ? decryptCookieValue(accountCipher) : '';
    const password = passwordCipher ? decryptCookieValue(passwordCipher) : '';
    if (!account && !password) {
      return null;
    }
    return { account, password };
  } catch (e) {
    return null;
  }
}
