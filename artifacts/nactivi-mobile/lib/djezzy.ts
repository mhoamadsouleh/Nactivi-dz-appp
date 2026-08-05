export type DjezzyOffer = {
  label: string;
  code: string;
  kind: 'shake' | 'activate-product';
  name: string;
  amount: string;
  price: number;
  duration: string;
};

export type AccountSummary = {
  phone: string;
  balance: string;
  subscriptionType: string;
  products: Array<{
    name: string;
    amount: string;
    expiry: string;
  }>;
};

export type MigrationOption = {
  id: string;
  name: string;
  description?: string;
};

export const PAID_OFFERS: DjezzyOffer[] = [
  { label: 'عرض 70 دج · 4 جيغا', code: 'BTLINTSPEEDDAY2Go', kind: 'shake', name: 'عرض 70 دج 4Go', amount: '4GB', price: 70, duration: '24 ساعة' },
  { label: 'عرض 100 دج · 2 جيغا', code: 'DOVINTSPEEDDAY1GoPRE', kind: 'activate-product', name: 'عرض 100 دج 2Go', amount: '2GB', price: 100, duration: '24 ساعة' },
  { label: 'عرض 30 دج · 300 ميغا', code: 'DOVINTSPEEDDAY100MoPRE', kind: 'activate-product', name: 'عرض 30 دج 300Mo', amount: '300MB', price: 30, duration: '24 ساعة' },
  { label: 'عرض 50 دج · 600 ميغا', code: 'DOVINTSPEEDDAY250MoPRE', kind: 'activate-product', name: 'عرض 50 دج 600Mo', amount: '600MB', price: 50, duration: '24 ساعة' },
  { label: 'عرض 150 دج · 4 جيغا', code: 'DOVINTSPEEDWEEK2GoPRE', kind: 'activate-product', name: 'عرض 150 دج 4Go', amount: '4GB', price: 150, duration: '7 أيام' },
  { label: 'عرض 300 دج · 10 جيغا', code: 'DOVINTSPEEDWEEK3GoPRE', kind: 'activate-product', name: 'عرض 300 دج 10Go', amount: '10GB', price: 300, duration: '7 أيام' },
  { label: 'عرض 190 دج · 10 جيغا', code: 'BTL4GBDAY', kind: 'shake', name: 'عرض 190 دج 10Go', amount: '10GB', price: 190, duration: '72 ساعة' },
  { label: 'عرض 70 دج · 3 جيغا', code: '1GBFB3DAY', kind: 'shake', name: 'عرض 70 دج 3Go', amount: '3GB', price: 70, duration: '3 أيام' },
  { label: 'عرض 500 دج · 12 جيغا', code: 'DOVINTSPEEDMONTH6GoPRE', kind: 'activate-product', name: 'عرض 500 دج 12Go', amount: '12GB', price: 500, duration: 'شهر' },
  { label: 'عرض 1000 دج · 30 جيغا', code: 'DOVINTSPEEDMONTH15GoPRE', kind: 'activate-product', name: 'عرض 1000 دج 30Go', amount: '30GB', price: 1000, duration: 'شهر' },
  { label: 'عرض 1500 دج · 60 جيغا', code: 'DOVINTSPEEDMONTH30GoPRE', kind: 'activate-product', name: 'عرض 1500 دج 60Go', amount: '60GB', price: 1500, duration: 'شهر' },
  { label: 'عرض 2000 دج · 100 جيغا', code: 'DOVINTSPEEDMONTH100GoPRE5G', kind: 'activate-product', name: 'عرض 2000 دج 100Go', amount: '100GB', price: 2000, duration: '30 يوم' },
  { label: 'عرض 4000 دج · 200 جيغا', code: 'DOVINTSPEEDMONTH220GoPRE5G', kind: 'activate-product', name: 'عرض 4000 دج 200Go', amount: '200GB', price: 4000, duration: '30 يوم' },
];

const SERVICE_COOLDOWN_MS = 12 * 60 * 1000;

const getApiOrigin = () => {
  const domain = process.env.EXPO_PUBLIC_DOMAIN;
  if (!domain) {
    throw new Error('الخادم غير مهيأ بعد. أضف نطاق الخادم في إعدادات التطبيق.');
  }
  return `https://${domain}`;
};

async function call<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${getApiOrigin()}${path}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const payload = (await response.json().catch(() => ({}))) as {
    message?: string;
    error?: string;
  } & T;

  if (!response.ok) {
    throw new Error(payload.message || payload.error || 'تعذر الاتصال بخدمة جيزي');
  }
  return payload;
}

export const cleanPhoneNumber = (value: string): string | null => {
  let cleaned = value.replace(/[^0-9]/g, '');
  if (cleaned.startsWith('213')) cleaned = `0${cleaned.slice(3)}`;
  return /^0[567][0-9]{8}$/.test(cleaned) ? cleaned : null;
};

export const maskPhone = (phone: string) =>
  phone.length >= 6 ? `${phone.slice(0, 4)}••••${phone.slice(-2)}` : phone;

export const cooldownKey = (service: string, offerCode?: string) =>
  offerCode ? `${service}:${offerCode}` : service;

export const cooldownRemaining = (timestamps: Record<string, number>, key: string) =>
  Math.max(0, SERVICE_COOLDOWN_MS - (Date.now() - (timestamps[key] || 0)));

export const formatRemaining = (milliseconds: number) => {
  const totalSeconds = Math.ceil(milliseconds / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes} د ${seconds.toString().padStart(2, '0')} ث`;
};

export const serviceCooldownMs = SERVICE_COOLDOWN_MS;

export const requestOtp = (phone: string) =>
  call<{ message: string }>('/api/djezzy/request-otp', { phone });

export const verifyOtp = (phone: string, otp: string) =>
  call<{ token: string; msisdn: string }>('/api/djezzy/verify-otp', { phone, otp });

export const getAccountSummary = (token: string, msisdn: string) =>
  call<AccountSummary>('/api/djezzy/account', { token, msisdn });

export const activateWalk2Go = (token: string, msisdn: string) =>
  call<{ message: string }>('/api/djezzy/activate/walk-2go', { token, msisdn });

export const activatePaidOffer = (token: string, msisdn: string, offer: DjezzyOffer) =>
  call<{ message: string }>('/api/djezzy/activate/offer', { token, msisdn, offer });

export const sendMgmInvitation = (token: string, sender: string, receiver: string) =>
  call<{ message: string }>('/api/djezzy/mgm/invite', { token, sender, receiver });

export const activateMgmReward = (token: string, sender: string) =>
  call<{ message: string }>('/api/djezzy/mgm/reward', { token, sender });

export const getMigrationOptions = (token: string, msisdn: string) =>
  call<{ options: MigrationOption[] }>('/api/djezzy/migration/options', { token, msisdn });

export const executeMigration = (token: string, msisdn: string, migrationId: string) =>
  call<{ message: string }>('/api/djezzy/migration/execute', { token, msisdn, migrationId });