import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  I18nManager,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useColors } from '@/hooks/useColors';
import {
  AccountSummary,
  activateMgmReward,
  activatePaidOffer,
  activateWalk2Go,
  cleanPhoneNumber,
  cooldownKey,
  cooldownRemaining,
  executeMigration,
  formatRemaining,
  getAccountSummary,
  getMigrationOptions,
  maskPhone,
  MigrationOption,
  PAID_OFFERS,
  requestOtp,
  sendMgmInvitation,
  serviceCooldownMs,
  verifyOtp,
} from '@/lib/djezzy';

I18nManager.allowRTL(true);
I18nManager.forceRTL(true);

type Screen = 'login' | 'home';
type BusyAction = 'login' | 'refresh' | 'walk' | 'offer' | 'mgm' | 'reward' | 'migration' | null;

const PHONE_STORAGE_KEY = '@nactivi/phone';
const COOLDOWNS_STORAGE_KEY = '@nactivi/cooldowns';

export default function HomeScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const styles = useMemo(() => createStyles(colors), [colors]);
  const [screen, setScreen] = useState<Screen>('login');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [pendingPhone, setPendingPhone] = useState('');
  const [token, setToken] = useState('');
  const [msisdn, setMsisdn] = useState('');
  const [account, setAccount] = useState<AccountSummary | null>(null);
  const [cooldowns, setCooldowns] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState<BusyAction>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [showOffers, setShowOffers] = useState(false);
  const [showMgm, setShowMgm] = useState(false);
  const [showMigration, setShowMigration] = useState(false);
  const [receiver, setReceiver] = useState('');
  const [migrationOptions, setMigrationOptions] = useState<MigrationOption[]>([]);
  const [clock, setClock] = useState(Date.now());

  useEffect(() => {
    void AsyncStorage.multiGet([PHONE_STORAGE_KEY, COOLDOWNS_STORAGE_KEY]).then(([savedPhone, savedCooldowns]) => {
      if (savedPhone[1]) setPhone(savedPhone[1]);
      if (savedCooldowns[1]) setCooldowns(JSON.parse(savedCooldowns[1]) as Record<string, number>);
    });
  }, []);

  useEffect(() => {
    const interval = setInterval(() => setClock(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);

  const saveCooldown = (key: string) => {
    const next = { ...cooldowns, [key]: Date.now() };
    setCooldowns(next);
    void AsyncStorage.setItem(COOLDOWNS_STORAGE_KEY, JSON.stringify(next));
  };

  const run = async <T,>(action: BusyAction, operation: () => Promise<T>, onSuccess: (value: T) => void) => {
    setBusy(action);
    setError('');
    setNotice('');
    try {
      const result = await operation();
      onSuccess(result);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'حدث خطأ غير متوقع');
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setBusy(null);
    }
  };

  const handleRequestOtp = () => {
    const normalized = cleanPhoneNumber(phone);
    if (!normalized) {
      setError('أدخل رقم جيزي صحيحاً يبدأ بـ 05 أو 06 أو 07.');
      return;
    }
    setPhone(normalized);
    setPendingPhone(normalized);
    void run('login', () => requestOtp(normalized), () => {
      setOtpSent(true);
      setNotice('أرسلنا رمز التحقق إلى رقمك. أدخله خلال 5 دقائق.');
      void AsyncStorage.setItem(PHONE_STORAGE_KEY, normalized);
    });
  };

  const handleVerifyOtp = () => {
    if (!/^[0-9]{6}$/.test(otp)) {
      setError('رمز التحقق يجب أن يتكون من 6 أرقام.');
      return;
    }
    void run('login', () => verifyOtp(pendingPhone, otp), (result) => {
      setToken(result.token);
      setMsisdn(result.msisdn);
      setScreen('home');
      void loadAccount(result.token, result.msisdn);
    });
  };

  const loadAccount = async (activeToken = token, activeMsisdn = msisdn) => {
    if (!activeToken || !activeMsisdn) return;
    await run('refresh', () => getAccountSummary(activeToken, activeMsisdn), setAccount);
  };

  const guardCooldown = (key: string) => {
    const remaining = cooldownRemaining(cooldowns, key);
    if (remaining <= 0) return true;
    setError(`هذه الخدمة متاحة مجدداً بعد ${formatRemaining(remaining)}.`);
    return false;
  };

  const activateWalk = () => {
    const key = cooldownKey('walk-2go');
    if (!guardCooldown(key)) return;
    void run('walk', () => activateWalk2Go(token, msisdn), (result) => {
      saveCooldown(key);
      setNotice(result.message);
      void loadAccount();
    });
  };

  const activateOffer = (offer: (typeof PAID_OFFERS)[number]) => {
    const key = cooldownKey('paid-offer', offer.code);
    if (!guardCooldown(key)) return;
    setShowOffers(false);
    void run('offer', () => activatePaidOffer(token, msisdn, offer), (result) => {
      saveCooldown(key);
      setNotice(result.message);
      void loadAccount();
    });
  };

  const sendInvitation = () => {
    const normalized = cleanPhoneNumber(receiver);
    if (!normalized) {
      setError('أدخل رقم المستفيد بصيغة صحيحة.');
      return;
    }
    const key = cooldownKey('mgm-invite');
    if (!guardCooldown(key)) return;
    void run('mgm', () => sendMgmInvitation(token, msisdn, normalized), (result) => {
      saveCooldown(key);
      setReceiver('');
      setNotice(result.message);
      setShowMgm(false);
    });
  };

  const rewardMgm = () => {
    const key = cooldownKey('mgm-reward');
    if (!guardCooldown(key)) return;
    void run('reward', () => activateMgmReward(token, msisdn), (result) => {
      saveCooldown(key);
      setNotice(result.message);
      setShowMgm(false);
      void loadAccount();
    });
  };

  const loadMigrations = () => {
    if (!guardCooldown(cooldownKey('migration'))) return;
    void run('migration', () => getMigrationOptions(token, msisdn), (result) => {
      setMigrationOptions(result.options);
      setShowMigration(true);
    });
  };

  const chooseMigration = (option: MigrationOption) => {
    Alert.alert('تأكيد التحويل', `هل تريد التحويل إلى ${option.name}؟`, [
      { text: 'إلغاء', style: 'cancel' },
      {
        text: 'تأكيد',
        onPress: () => void run('migration', () => executeMigration(token, msisdn, option.id), (result) => {
          saveCooldown(cooldownKey('migration'));
          setNotice(result.message);
          setShowMigration(false);
        }),
      },
    ]);
  };

  if (screen === 'login') {
    return (
      <View style={[styles.root, { paddingTop: insets.top }]}>
        <LinearGradient colors={[colors.heroStart, colors.heroEnd]} style={styles.loginHero}>
          <View style={styles.brandMark}>
            <Ionicons name="radio-outline" size={28} color={colors.primaryForeground} />
          </View>
          <Text style={styles.heroEyebrow}>خدمات الهاتف في مكان واحد</Text>
          <Text style={styles.heroTitle}>إدارة خط جيزي{'\n'}بهدوء وثقة</Text>
          <Text style={styles.heroDescription}>تحقق من رصيدك، راقب باقاتك وفعل الخدمة التي تحتاجها بخطوات واضحة.</Text>
        </LinearGradient>
        <KeyboardAvoidingView style={styles.loginPanel} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          <Text style={styles.panelKicker}>{otpSent ? 'الخطوة الثانية' : 'ابدأ الآن'}</Text>
          <Text style={styles.panelTitle}>{otpSent ? 'أدخل رمز التحقق' : 'أدخل رقم جيزي'}</Text>
          <Text style={styles.panelHint}>{otpSent ? `تم إرسال الرمز إلى ${maskPhone(pendingPhone)}` : 'سنرسل لك رمزاً لمرة واحدة للتحقق من ملكية الرقم.'}</Text>
          {!otpSent ? (
            <TextInput
              value={phone}
              onChangeText={setPhone}
              placeholder="07 xx xx xx xx"
              placeholderTextColor={colors.mutedForeground}
              keyboardType="phone-pad"
              style={styles.input}
              textAlign="right"
              testID="phone-input"
            />
          ) : (
            <TextInput
              value={otp}
              onChangeText={setOtp}
              placeholder="000000"
              placeholderTextColor={colors.mutedForeground}
              keyboardType="number-pad"
              maxLength={6}
              style={[styles.input, styles.otpInput]}
              textAlign="center"
              testID="otp-input"
            />
          )}
          {(error || notice) && <Feedback tone={error ? 'error' : 'success'} message={error || notice} styles={styles} />}
          <Pressable
            onPress={otpSent ? handleVerifyOtp : handleRequestOtp}
            disabled={busy === 'login'}
            style={({ pressed }) => [styles.primaryButton, pressed && styles.pressed, busy === 'login' && styles.disabled]}
            testID="login-button"
          >
            {busy === 'login' ? <ActivityIndicator color={colors.primaryForeground} /> : <Text style={styles.primaryButtonText}>{otpSent ? 'دخول آمن' : 'إرسال رمز التحقق'}</Text>}
            {busy !== 'login' && <Ionicons name="arrow-back" size={18} color={colors.primaryForeground} />}
          </Pressable>
          {otpSent && (
            <Pressable onPress={() => { setOtpSent(false); setOtp(''); setError(''); }} style={styles.linkButton}>
              <Text style={styles.linkText}>تغيير الرقم</Text>
            </Pressable>
          )}
          <Text style={styles.privacyNote}>لا يتم حفظ رمز التحقق. اتصال الخدمة يتم عبر خادم آمن.</Text>
        </KeyboardAvoidingView>
      </View>
    );
  }

  return (
    <View style={[styles.root, { paddingTop: insets.top }]}>
      <ScrollView
        contentContainerStyle={[styles.scrollContent, { paddingBottom: insets.bottom + 28 }]}
        refreshControl={<RefreshControl refreshing={busy === 'refresh'} onRefresh={() => void loadAccount()} tintColor={colors.primary} />}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.topBar}>
          <View>
            <Text style={styles.welcomeLabel}>مساحتك الشخصية</Text>
            <Text style={styles.topTitle}>أهلاً بك</Text>
          </View>
          <Pressable onPress={() => { setScreen('login'); setToken(''); setAccount(null); setOtpSent(false); }} style={styles.iconButton} testID="logout-button">
            <Ionicons name="log-out-outline" size={21} color={colors.foreground} />
          </Pressable>
        </View>

        <LinearGradient colors={[colors.heroStart, colors.heroEnd]} style={styles.accountCard}>
          <View style={styles.accountCardHeader}>
            <View style={styles.onlinePill}><View style={styles.onlineDot} /><Text style={styles.onlineText}>متصل</Text></View>
            <Text style={styles.cardLabel}>رقم جيزي</Text>
          </View>
          <Text style={styles.cardPhone}>{maskPhone(phone)}</Text>
          <View style={styles.balanceRow}>
            <View><Text style={styles.balanceCaption}>الرصيد الرئيسي</Text><Text style={styles.balanceValue}>{account?.balance ?? '—'} <Text style={styles.balanceUnit}>دج</Text></Text></View>
            <View style={styles.cardBadge}><Ionicons name="wallet-outline" size={22} color={colors.heroStart} /></View>
          </View>
        </LinearGradient>

        {(error || notice) && <Feedback tone={error ? 'error' : 'success'} message={error || notice} styles={styles} />}

        <View style={styles.sectionHeader}><Text style={styles.sectionTitle}>الخدمات السريعة</Text><Text style={styles.sectionMeta}>4 خدمات</Text></View>
        <View style={styles.quickGrid}>
          <QuickAction icon="gift-outline" label="2Go مجاني" accent={colors.primary} disabled={busy !== null} onPress={activateWalk} styles={styles} />
          <QuickAction icon="pricetag-outline" label="العروض" accent={colors.accent} onPress={() => setShowOffers(true)} styles={styles} />
          <QuickAction icon="people-outline" label="دعوات MGM" accent={colors.blue} onPress={() => setShowMgm(true)} styles={styles} />
          <QuickAction icon="swap-horizontal-outline" label="تحويل العرض" accent={colors.amber} onPress={loadMigrations} styles={styles} />
        </View>

        <View style={styles.sectionHeader}><Text style={styles.sectionTitle}>الباقة الحالية</Text><Pressable onPress={() => void loadAccount()}><Ionicons name="refresh-outline" size={20} color={colors.primary} /></Pressable></View>
        <View style={styles.productsCard}>
          <View style={styles.productMain}><View style={[styles.productIcon, { backgroundColor: colors.accentSoft }]}><Ionicons name="speedometer-outline" size={21} color={colors.accent} /></View><View style={styles.productCopy}><Text style={styles.productName}>{account?.subscriptionType || 'جارٍ تحميل العرض'}</Text><Text style={styles.productCaption}>{account?.products.length ? `${account.products.length} باقات نشطة` : 'معلومات العرض تظهر بعد التحقق'}</Text></View><Ionicons name="chevron-back" size={18} color={colors.mutedForeground} /></View>
          {account?.products.slice(0, 3).map((product) => <View style={styles.productLine} key={`${product.name}-${product.expiry}`}><Text style={styles.productLineName}>{product.name}</Text><Text style={styles.productLineValue}>{product.amount}</Text></View>)}
          {!account?.products.length && <Text style={styles.emptyText}>لا توجد باقات إضافية نشطة حالياً.</Text>}
        </View>

        <View style={styles.sectionHeader}><Text style={styles.sectionTitle}>حالة الانتظار</Text><Text style={styles.sectionMeta}>12 دقيقة للخدمة</Text></View>
        <CooldownList cooldowns={cooldowns} now={clock} styles={styles} colors={colors} />
      </ScrollView>

      <OfferModal visible={showOffers} onClose={() => setShowOffers(false)} onSelect={activateOffer} busy={busy === 'offer'} styles={styles} colors={colors} />
      <MgmModal visible={showMgm} onClose={() => setShowMgm(false)} receiver={receiver} setReceiver={setReceiver} onInvite={sendInvitation} onReward={rewardMgm} busy={busy === 'mgm' || busy === 'reward'} styles={styles} colors={colors} />
      <MigrationModal visible={showMigration} options={migrationOptions} onClose={() => setShowMigration(false)} onSelect={chooseMigration} styles={styles} colors={colors} />
    </View>
  );
}

function Feedback({ tone, message, styles }: { tone: 'error' | 'success'; message: string; styles: ReturnType<typeof createStyles> }) {
  return <View style={[styles.feedback, tone === 'error' ? styles.feedbackError : styles.feedbackSuccess]}><Ionicons name={tone === 'error' ? 'alert-circle-outline' : 'checkmark-circle-outline'} size={18} color={tone === 'error' ? styles.feedbackError.color : styles.feedbackSuccess.color} /><Text style={[styles.feedbackText, { color: tone === 'error' ? styles.feedbackError.color : styles.feedbackSuccess.color }]}>{message}</Text></View>;
}

function QuickAction({ icon, label, accent, disabled, onPress, styles }: { icon: keyof typeof Ionicons.glyphMap; label: string; accent: string; disabled?: boolean; onPress: () => void; styles: ReturnType<typeof createStyles> }) {
  return <Pressable onPress={onPress} disabled={disabled} style={({ pressed }) => [styles.quickAction, pressed && styles.pressed, disabled && styles.disabled]}><View style={[styles.quickIcon, { backgroundColor: `${accent}20` }]}><Ionicons name={icon} size={22} color={accent} /></View><Text style={styles.quickLabel}>{label}</Text><Ionicons name="chevron-back" size={16} color={styles.quickChevron.color} /></Pressable>;
}

function CooldownList({ cooldowns, now, styles, colors }: { cooldowns: Record<string, number>; now: number; styles: ReturnType<typeof createStyles>; colors: ReturnType<typeof useColors> }) {
  const entries = [
    { key: 'walk-2go', label: '2Go مجاني', icon: 'gift-outline' as const, color: colors.primary },
    { key: 'mgm-invite', label: 'دعوة MGM', icon: 'people-outline' as const, color: colors.blue },
    { key: 'mgm-reward', label: 'مكافأة MGM', icon: 'sparkles-outline' as const, color: colors.accent },
    { key: 'migration', label: 'تحويل العرض', icon: 'swap-horizontal-outline' as const, color: colors.amber },
  ];
  return (
    <View style={styles.cooldownCard}>
      {entries.map((entry) => {
        const remaining = cooldownRemaining(cooldowns, entry.key);
        return (
          <View style={styles.cooldownRow} key={entry.key}>
            <View style={[styles.cooldownIcon, { backgroundColor: `${entry.color}20` }]}>
              <Ionicons name={entry.icon} size={17} color={entry.color} />
            </View>
            <Text style={styles.cooldownLabel}>{entry.label}</Text>
            <Text style={[styles.cooldownValue, remaining > 0 ? { color: colors.amber } : { color: colors.primary }]}>
              {remaining > 0 ? formatRemaining(remaining) : 'متاح الآن'}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

function OfferModal({ visible, onClose, onSelect, busy, styles, colors }: { visible: boolean; onClose: () => void; onSelect: (offer: (typeof PAID_OFFERS)[number]) => void; busy: boolean; styles: ReturnType<typeof createStyles>; colors: ReturnType<typeof useColors> }) {
  return <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}><View style={styles.modalBackdrop}><View style={styles.modalSheet}><View style={styles.modalHandle} /><View style={styles.modalHeader}><View><Text style={styles.modalKicker}>عروض الإنترنت</Text><Text style={styles.modalTitle}>اختر العرض المناسب</Text></View><Pressable onPress={onClose} style={styles.closeButton}><Ionicons name="close" size={21} color={colors.foreground} /></Pressable></View><FlatList data={PAID_OFFERS} keyExtractor={(item) => item.code} contentContainerStyle={styles.offerList} renderItem={({ item }) => <Pressable onPress={() => onSelect(item)} disabled={busy} style={({ pressed }) => [styles.offerRow, pressed && styles.pressed]}><View style={styles.offerAmount}><Text style={styles.offerAmountText}>{item.amount}</Text><Text style={styles.offerDuration}>{item.duration}</Text></View><View style={styles.offerCopy}><Text style={styles.offerLabel}>{item.label}</Text><Text style={styles.offerName}>{item.name}</Text></View><View style={styles.offerPrice}><Text style={styles.offerPriceText}>{item.price}</Text><Text style={styles.offerPriceUnit}>دج</Text></View></Pressable>} /></View></View></Modal>;
}

function MgmModal({ visible, onClose, receiver, setReceiver, onInvite, onReward, busy, styles, colors }: { visible: boolean; onClose: () => void; receiver: string; setReceiver: (value: string) => void; onInvite: () => void; onReward: () => void; busy: boolean; styles: ReturnType<typeof createStyles>; colors: ReturnType<typeof useColors> }) {
  return <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}><View style={styles.modalBackdrop}><View style={styles.modalSheet}><View style={styles.modalHandle} /><View style={styles.modalHeader}><View><Text style={styles.modalKicker}>MGM</Text><Text style={styles.modalTitle}>شارك واستفد</Text></View><Pressable onPress={onClose} style={styles.closeButton}><Ionicons name="close" size={21} color={colors.foreground} /></Pressable></View><Text style={styles.modalDescription}>أرسل دعوة إلى رقم جيزي آخر، ثم فعّل مكافأتك عند اكتمال الدعوة.</Text><TextInput value={receiver} onChangeText={setReceiver} keyboardType="phone-pad" placeholder="رقم المستفيد 07..." placeholderTextColor={colors.mutedForeground} textAlign="right" style={styles.input} /><Pressable onPress={onInvite} disabled={busy} style={[styles.primaryButton, busy && styles.disabled]}><Ionicons name="send-outline" size={18} color={colors.primaryForeground} /><Text style={styles.primaryButtonText}>إرسال الدعوة</Text></Pressable><Pressable onPress={onReward} disabled={busy} style={[styles.secondaryButton, busy && styles.disabled]}><Ionicons name="gift-outline" size={18} color={colors.primary} /><Text style={styles.secondaryButtonText}>تفعيل المكافأة</Text></Pressable></View></View></Modal>;
}

function MigrationModal({ visible, options, onClose, onSelect, styles, colors }: { visible: boolean; options: MigrationOption[]; onClose: () => void; onSelect: (option: MigrationOption) => void; styles: ReturnType<typeof createStyles>; colors: ReturnType<typeof useColors> }) {
  return <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}><View style={styles.modalBackdrop}><View style={styles.modalSheet}><View style={styles.modalHandle} /><View style={styles.modalHeader}><View><Text style={styles.modalKicker}>نوع العرض</Text><Text style={styles.modalTitle}>اختر التحويل</Text></View><Pressable onPress={onClose} style={styles.closeButton}><Ionicons name="close" size={21} color={colors.foreground} /></Pressable></View>{options.length ? options.map((option) => <Pressable key={option.id} onPress={() => onSelect(option)} style={({ pressed }) => [styles.migrationRow, pressed && styles.pressed]}><View style={styles.migrationIcon}><Ionicons name="swap-horizontal-outline" size={19} color={colors.amber} /></View><View style={styles.migrationCopy}><Text style={styles.offerLabel}>{option.name}</Text>{option.description && <Text style={styles.offerName}>{option.description}</Text>}</View><Ionicons name="chevron-back" size={17} color={colors.mutedForeground} /></Pressable>) : <Text style={styles.emptyText}>لا توجد خيارات تحويل متاحة لهذا الرقم.</Text>}</View></View></Modal>;
}

const createStyles = (colors: ReturnType<typeof useColors>) => StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  loginHero: { paddingHorizontal: 24, paddingTop: 36, paddingBottom: 40, borderBottomLeftRadius: 30, borderBottomRightRadius: 30 },
  brandMark: { width: 54, height: 54, borderRadius: 18, backgroundColor: `${colors.primaryForeground}22`, alignItems: 'center', justifyContent: 'center', marginBottom: 28 },
  heroEyebrow: { color: colors.heroMuted, fontSize: 13, fontFamily: 'Inter_500Medium', marginBottom: 10, textAlign: 'right' },
  heroTitle: { color: colors.primaryForeground, fontSize: 32, lineHeight: 42, fontFamily: 'Inter_700Bold', textAlign: 'right' },
  heroDescription: { color: colors.heroMuted, fontSize: 14, lineHeight: 24, fontFamily: 'Inter_400Regular', textAlign: 'right', marginTop: 16 },
  loginPanel: { flex: 1, padding: 24, justifyContent: 'center' },
  panelKicker: { color: colors.primary, fontSize: 13, fontFamily: 'Inter_600SemiBold', textAlign: 'right', marginBottom: 8 },
  panelTitle: { color: colors.foreground, fontSize: 26, fontFamily: 'Inter_700Bold', textAlign: 'right' },
  panelHint: { color: colors.mutedForeground, fontSize: 14, fontFamily: 'Inter_400Regular', textAlign: 'right', lineHeight: 22, marginTop: 8, marginBottom: 22 },
  input: { backgroundColor: colors.inputBackground, borderWidth: 1, borderColor: colors.border, borderRadius: 16, minHeight: 56, paddingHorizontal: 16, color: colors.foreground, fontSize: 16, fontFamily: 'Inter_500Medium', marginBottom: 14 },
  otpInput: { letterSpacing: 8, fontSize: 24 },
  primaryButton: { minHeight: 56, borderRadius: 17, backgroundColor: colors.primary, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 10, paddingHorizontal: 18 },
  primaryButtonText: { color: colors.primaryForeground, fontFamily: 'Inter_700Bold', fontSize: 15 },
  secondaryButton: { minHeight: 52, borderRadius: 16, backgroundColor: colors.accentSoft, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 9, paddingHorizontal: 18, marginTop: 10 },
  secondaryButtonText: { color: colors.primary, fontFamily: 'Inter_700Bold', fontSize: 14 },
  linkButton: { alignItems: 'center', padding: 16 },
  linkText: { color: colors.primary, fontFamily: 'Inter_600SemiBold', fontSize: 14 },
  privacyNote: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 11, textAlign: 'center', marginTop: 24 },
  scrollContent: { paddingHorizontal: 18, paddingTop: 20 },
  topBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  welcomeLabel: { color: colors.mutedForeground, fontFamily: 'Inter_500Medium', fontSize: 12, textAlign: 'right' },
  topTitle: { color: colors.foreground, fontFamily: 'Inter_700Bold', fontSize: 27, marginTop: 3, textAlign: 'right' },
  iconButton: { width: 43, height: 43, borderRadius: 15, borderWidth: 1, borderColor: colors.border, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.card },
  accountCard: { borderRadius: 24, padding: 20, minHeight: 190, marginBottom: 18 },
  accountCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardLabel: { color: colors.heroMuted, fontFamily: 'Inter_500Medium', fontSize: 12 },
  onlinePill: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: `${colors.primaryForeground}18`, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20 },
  onlineDot: { width: 7, height: 7, borderRadius: 4, backgroundColor: colors.lime },
  onlineText: { color: colors.primaryForeground, fontFamily: 'Inter_600SemiBold', fontSize: 11 },
  cardPhone: { color: colors.primaryForeground, fontFamily: 'Inter_600SemiBold', fontSize: 15, marginTop: 22, textAlign: 'right' },
  balanceRow: { marginTop: 18, flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between' },
  balanceCaption: { color: colors.heroMuted, fontFamily: 'Inter_400Regular', fontSize: 12, textAlign: 'right' },
  balanceValue: { color: colors.primaryForeground, fontFamily: 'Inter_700Bold', fontSize: 34, marginTop: 3, textAlign: 'right' },
  balanceUnit: { fontSize: 14, fontFamily: 'Inter_500Medium' },
  cardBadge: { width: 48, height: 48, borderRadius: 17, backgroundColor: colors.lime, alignItems: 'center', justifyContent: 'center' },
  feedback: { minHeight: 46, borderRadius: 14, paddingHorizontal: 13, alignItems: 'center', flexDirection: 'row', gap: 8, marginBottom: 16 },
  feedbackError: { backgroundColor: colors.errorSoft, color: colors.error },
  feedbackSuccess: { backgroundColor: colors.successSoft, color: colors.success },
  feedbackText: { flex: 1, fontFamily: 'Inter_500Medium', fontSize: 12, lineHeight: 19, textAlign: 'right' },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 4, marginBottom: 11 },
  sectionTitle: { color: colors.foreground, fontFamily: 'Inter_700Bold', fontSize: 17, textAlign: 'right' },
  sectionMeta: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 11 },
  quickGrid: { gap: 9, marginBottom: 21 },
  quickAction: { minHeight: 67, borderRadius: 17, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, gap: 11 },
  quickIcon: { width: 42, height: 42, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  quickLabel: { flex: 1, color: colors.foreground, fontFamily: 'Inter_600SemiBold', fontSize: 14, textAlign: 'right' },
  quickChevron: { color: colors.mutedForeground },
  productsCard: { borderRadius: 19, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, padding: 15, marginBottom: 21 },
  productMain: { flexDirection: 'row', alignItems: 'center', gap: 11 },
  productIcon: { width: 42, height: 42, borderRadius: 14, alignItems: 'center', justifyContent: 'center' },
  productCopy: { flex: 1 },
  productName: { color: colors.foreground, fontFamily: 'Inter_700Bold', fontSize: 14, textAlign: 'right' },
  productCaption: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 11, marginTop: 4, textAlign: 'right' },
  productLine: { flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 11, marginTop: 12 },
  productLineName: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 12, flex: 1, textAlign: 'right' },
  productLineValue: { color: colors.foreground, fontFamily: 'Inter_700Bold', fontSize: 12, marginLeft: 10 },
  emptyText: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 12, lineHeight: 20, textAlign: 'right', paddingVertical: 13 },
  cooldownCard: { borderRadius: 19, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, paddingHorizontal: 15 },
  cooldownRow: { minHeight: 55, flexDirection: 'row', alignItems: 'center', gap: 10, borderBottomWidth: 1, borderBottomColor: colors.border },
  cooldownIcon: { width: 31, height: 31, borderRadius: 11, alignItems: 'center', justifyContent: 'center' },
  cooldownLabel: { flex: 1, color: colors.foreground, fontFamily: 'Inter_500Medium', fontSize: 12, textAlign: 'right' },
  cooldownValue: { fontFamily: 'Inter_600SemiBold', fontSize: 11 },
  modalBackdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: colors.modalBackdrop },
  modalSheet: { backgroundColor: colors.background, borderTopLeftRadius: 28, borderTopRightRadius: 28, padding: 18, paddingBottom: 30, maxHeight: '88%' },
  modalHandle: { width: 42, height: 4, borderRadius: 4, backgroundColor: colors.border, alignSelf: 'center', marginBottom: 18 },
  modalHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 },
  modalKicker: { color: colors.primary, fontFamily: 'Inter_600SemiBold', fontSize: 12, textAlign: 'right' },
  modalTitle: { color: colors.foreground, fontFamily: 'Inter_700Bold', fontSize: 22, textAlign: 'right', marginTop: 4 },
  closeButton: { width: 38, height: 38, borderRadius: 13, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, alignItems: 'center', justifyContent: 'center' },
  offerList: { gap: 8 },
  offerRow: { minHeight: 75, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card, borderRadius: 17, padding: 11, flexDirection: 'row', alignItems: 'center', gap: 10 },
  offerAmount: { minWidth: 62, alignItems: 'center' },
  offerAmountText: { color: colors.primary, fontFamily: 'Inter_700Bold', fontSize: 14 },
  offerDuration: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 10, marginTop: 3 },
  offerCopy: { flex: 1 },
  offerLabel: { color: colors.foreground, fontFamily: 'Inter_600SemiBold', fontSize: 13, textAlign: 'right' },
  offerName: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 11, marginTop: 4, textAlign: 'right' },
  offerPrice: { minWidth: 42, alignItems: 'center' },
  offerPriceText: { color: colors.foreground, fontFamily: 'Inter_700Bold', fontSize: 15 },
  offerPriceUnit: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 10 },
  modalDescription: { color: colors.mutedForeground, fontFamily: 'Inter_400Regular', fontSize: 13, lineHeight: 21, textAlign: 'right', marginBottom: 16 },
  migrationRow: { minHeight: 68, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card, borderRadius: 17, padding: 12, flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 8 },
  migrationIcon: { width: 38, height: 38, borderRadius: 13, backgroundColor: colors.amberSoft, alignItems: 'center', justifyContent: 'center' },
  migrationCopy: { flex: 1 },
  pressed: { opacity: 0.78, transform: [{ scale: 0.99 }] },
  disabled: { opacity: 0.55 },
});