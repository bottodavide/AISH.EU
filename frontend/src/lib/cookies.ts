import Cookies from 'js-cookie'

export interface CookiePreferences {
  necessary: boolean
  analytics: boolean
  marketing: boolean
}

export const cookieConsent = {
  get: (): boolean => {
    return Cookies.get('cookie-consent') === 'true'
  },

  set: (accepted: boolean): void => {
    Cookies.set('cookie-consent', accepted.toString(), { expires: 365 })
  },

  remove: (): void => {
    Cookies.remove('cookie-consent')
  }
}

export const authToken = {
  get: (): string | undefined => {
    return Cookies.get('auth-token')
  },

  set: (token: string): void => {
    Cookies.set('auth-token', token, { expires: 7, secure: true, sameSite: 'strict' })
  },

  remove: (): void => {
    Cookies.remove('auth-token')
  }
}

export function hasGivenConsent(): boolean {
  return cookieConsent.get()
}

export function getCookiePreferences(): CookiePreferences {
  const prefs = Cookies.get('cookie-preferences')
  if (prefs) {
    try {
      return JSON.parse(prefs)
    } catch {
      return { necessary: true, analytics: false, marketing: false }
    }
  }
  return { necessary: true, analytics: false, marketing: false }
}

export function acceptAllCookies(): void {
  const prefs: CookiePreferences = {
    necessary: true,
    analytics: true,
    marketing: true
  }
  Cookies.set('cookie-preferences', JSON.stringify(prefs), { expires: 365 })
  cookieConsent.set(true)
}

export function rejectAllCookies(): void {
  const prefs: CookiePreferences = {
    necessary: true,
    analytics: false,
    marketing: false
  }
  Cookies.set('cookie-preferences', JSON.stringify(prefs), { expires: 365 })
  cookieConsent.set(false)
}

export function saveCookiePreferences(prefs: CookiePreferences): void {
  Cookies.set('cookie-preferences', JSON.stringify(prefs), { expires: 365 })
  cookieConsent.set(prefs.analytics || prefs.marketing)
}

export function initializeCookiePreferences(): void {
  if (!hasGivenConsent()) {
    const defaultPrefs: CookiePreferences = {
      necessary: true,
      analytics: false,
      marketing: false
    }
    Cookies.set('cookie-preferences', JSON.stringify(defaultPrefs), { expires: 365 })
  }
}
