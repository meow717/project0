/**
 * Lightweight i18n — a typed message catalog, no framework. The active locale
 * lives in `stores/ui.store.ts`; read it through the `useTranslation` hook.
 * Switching locale also flips text direction (ar → rtl, en → ltr).
 */

export type Locale = "ar" | "en";

const en = {
  "landing.title": "App Template — Ready to Work",
  "landing.subtitle":
    "Next.js 16 · shadcn (RTL) · Zustand · feature-based and DRY, wired to a hexagonal Django + Ninja backend with JWT auth.",
  "landing.login": "Login",
  "landing.enterApp": "Open App",

  "auth.loginTitle": "Login",
  "auth.loginSubtitle": "Enter your email and password to continue",
  "auth.signupTitle": "Create account",
  "auth.signupSubtitle": "Create your account to get started",
  "auth.fullName": "Full name",
  "auth.email": "Email",
  "auth.password": "Password",
  "auth.loginBtn": "Sign in",
  "auth.loginLoading": "Signing in…",
  "auth.signupBtn": "Sign up",
  "auth.signupLoading": "Creating…",
  "auth.haveAccount": "Already have an account?",
  "auth.noAccount": "Don't have an account?",
  "auth.toLogin": "Login",
  "auth.toSignup": "Sign up",
  "auth.welcome": "Welcome",
  "auth.loginError": "Could not sign in",
  "auth.signupError": "Could not create account",

  "nav.account": "My account",
  "common.logout": "Logout",
  "common.loading": "Loading…",

  "account.thisAccount": "This account",
  "account.summaryAdmin": "You are signed in as an administrator account.",
  "account.summaryUser": "You are signed in as a standard user account.",
  "account.name": "Name",
  "account.email": "Email",
  "account.role": "Role",
  "account.roleAdmin": "Administrator",
  "account.roleUser": "User",
  "account.status": "Status",
  "account.active": "Active",
  "account.inactive": "Inactive",

  "toggle.language": "Switch language",
  "toggle.theme": "Toggle theme",
} as const;

export type MessageKey = keyof typeof en;

const ar: Record<MessageKey, string> = {
  "landing.title": "قالب التطبيق — جاهز للعمل",
  "landing.subtitle":
    "Next.js 16 · shadcn (RTL) · Zustand · بنية قائمة على الميزات وDRY، موصولة بخلفية Django + Ninja سداسية مع مصادقة JWT.",
  "landing.login": "تسجيل الدخول",
  "landing.enterApp": "فتح التطبيق",

  "auth.loginTitle": "تسجيل الدخول",
  "auth.loginSubtitle": "أدخل بريدك الإلكتروني وكلمة المرور للمتابعة",
  "auth.signupTitle": "إنشاء حساب",
  "auth.signupSubtitle": "أنشئ حسابك للبدء",
  "auth.fullName": "الاسم الكامل",
  "auth.email": "البريد الإلكتروني",
  "auth.password": "كلمة المرور",
  "auth.loginBtn": "دخول",
  "auth.loginLoading": "جارٍ الدخول…",
  "auth.signupBtn": "إنشاء حساب",
  "auth.signupLoading": "جارٍ الإنشاء…",
  "auth.haveAccount": "لديك حساب بالفعل؟",
  "auth.noAccount": "ليس لديك حساب؟",
  "auth.toLogin": "تسجيل الدخول",
  "auth.toSignup": "إنشاء حساب",
  "auth.welcome": "مرحباً",
  "auth.loginError": "تعذّر تسجيل الدخول",
  "auth.signupError": "تعذّر إنشاء الحساب",

  "nav.account": "حسابي",
  "common.logout": "خروج",
  "common.loading": "جارٍ التحميل…",

  "account.thisAccount": "هذا الحساب",
  "account.summaryAdmin": "أنت مسجّل الدخول بحساب مدير.",
  "account.summaryUser": "أنت مسجّل الدخول بحساب مستخدم عادي.",
  "account.name": "الاسم",
  "account.email": "البريد الإلكتروني",
  "account.role": "الدور",
  "account.roleAdmin": "مدير",
  "account.roleUser": "مستخدم",
  "account.status": "الحالة",
  "account.active": "نشط",
  "account.inactive": "غير نشط",

  "toggle.language": "تغيير اللغة",
  "toggle.theme": "تبديل السمة",
};

export const messages: Record<Locale, Record<MessageKey, string>> = { en, ar };

export const NUMBER_LOCALE: Record<Locale, string> = { en: "en-US", ar: "ar-EG" };
