import React, { useState, useEffect } from 'react';
import ScreenSwitcher from './components/ScreenSwitcher';
import TopNav from './components/TopNav';

// Import all Screens
import SplashScreen from './screens/SplashScreen';
import LoginScreen from './screens/LoginScreen';
import SignUpScreen from './screens/SignUpScreen';
import ForgotPasswordScreen from './screens/ForgotPasswordScreen';
import OtpScreen from './screens/OtpScreen';
import ResetPasswordScreen from './screens/ResetPasswordScreen';
import AccountCreatedScreen from './screens/AccountCreatedScreen';
import DashboardScreen from './screens/DashboardScreen';
import UploadScreen from './screens/UploadScreen';
import ProcessingScreen from './screens/ProcessingScreen';
import ResultsScreen from './screens/ResultsScreen';
import CompareScreen from './screens/CompareScreen';
import HistoryScreen from './screens/HistoryScreen';
import ReportsScreen from './screens/ReportsScreen';
import ProfileScreen from './screens/ProfileScreen';

import { 
  fetchAnalysesHistory, 
  fetchDeletedAnalyses,
  fetchDeletedNotes,
  restoreAnalysis,
  restoreNote,
  fetchNotes, 
  fetchSavedComparisons, 
  fetchProfile,
  deleteAnalysis, 
  deleteNote,
  deleteComparison,
  saveComparison,
  signOutUser,
  getAuthToken
} from './api';

export default function App() {
  // Restore initial activeScreen from sessionStorage or default to 'dashboard' if logged in / 'splash'
  const [activeScreen, setActiveScreen] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedScreen = sessionStorage.getItem('stainscope_active_screen');
      if (savedScreen && savedScreen !== 'splash') {
        return savedScreen;
      }
    }
    return 'splash';
  });

  const [deviceView, setDeviceView] = useState('desktop');
  const [theme, setTheme] = useState('light');
  
  // Auth & Session States
  const [session, setSession] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  // Active User Data States
  const [analysesHistory, setAnalysesHistory] = useState([]);
  const [savedNotes, setSavedNotes] = useState([]);
  const [savedComparisons, setSavedComparisons] = useState([]);
  const [recentlyDeleted, setRecentlyDeleted] = useState([]);

  const [currentAnalysis, setCurrentAnalysis] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = sessionStorage.getItem('stainscope_current_analysis');
        if (saved) return JSON.parse(saved);
      } catch (e) {}
    }
    return null;
  });
  const [selectedCompareSamples, setSelectedCompareSamples] = useState([]);
  const [processingPayload, setProcessingPayload] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Helper to load user data from FastAPI backend
  const loadUserData = async () => {
    try {
      const historyData = await fetchAnalysesHistory();
      setAnalysesHistory(Array.isArray(historyData) ? historyData : []);

      const deletedAnalyses = await fetchDeletedAnalyses();
      const deletedNotes = await fetchDeletedNotes();
      const combinedDeleted = [
        ...(Array.isArray(deletedAnalyses) ? deletedAnalyses : []),
        ...(Array.isArray(deletedNotes) ? deletedNotes : [])
      ];
      setRecentlyDeleted(combinedDeleted);
      
      const notesData = await fetchNotes();
      setSavedNotes(Array.isArray(notesData) ? notesData : []);
      
      const compsData = await fetchSavedComparisons();
      setSavedComparisons(Array.isArray(compsData) ? compsData : []);
      
      const profileData = await fetchProfile();
      if (profileData) {
        setUserProfile(profileData);
      }
    } catch (err) {
      console.warn('Error loading user data:', err);
    }
  };

  // Full Session & State Cleanup Handler on Logout button click
  const handleLogout = async () => {
    try {
      await signOutUser();
    } catch (e) {
      console.warn('Logout warning:', e);
    }
    sessionStorage.removeItem('stainscope_active_screen');
    sessionStorage.removeItem('stainscope_current_analysis');
    setSession(null);
    setUserProfile(null);
    setAnalysesHistory([]);
    setSavedNotes([]);
    setSavedComparisons([]);
    setRecentlyDeleted([]);
    setCurrentAnalysis(null);
    setSelectedCompareSamples([]);
    setProcessingPayload(null);
    setActiveScreen('login');
  };

  // Verify and restore authenticated session on app mount / page refresh
  useEffect(() => {
    let mounted = true;

    async function checkAuthSession() {
      try {
        const token = getAuthToken();
        if (!token) {
          if (mounted) {
            setSession(null);
            setIsLoadingAuth(false);
            const saved = sessionStorage.getItem('stainscope_active_screen');
            if (saved && ['dashboard', 'upload', 'processing', 'results', 'compare', 'history', 'reports', 'profile'].includes(saved)) {
              setActiveScreen('login');
            }
          }
          return;
        }

        // Validate token against backend /profile endpoint
        const profileData = await fetchProfile();
        if (profileData && mounted) {
          const userObj = {
            id: profileData.id,
            email: profileData.email || '',
            full_name: profileData.full_name || ''
          };
          const activeSession = { access_token: token, user: userObj };
          
          setSession(activeSession);
          setUserProfile(profileData);

          // Load user's records from MySQL
          await loadUserData();

          const savedScreen = sessionStorage.getItem('stainscope_active_screen');
          if (savedScreen && ['dashboard', 'upload', 'processing', 'results', 'compare', 'history', 'reports', 'profile'].includes(savedScreen)) {
            setActiveScreen(savedScreen);
          } else {
            setActiveScreen('dashboard');
            sessionStorage.setItem('stainscope_active_screen', 'dashboard');
          }
        } else if (mounted) {
          // Token invalid or expired
          await signOutUser();
          sessionStorage.removeItem('stainscope_active_screen');
          setSession(null);
          setUserProfile(null);
          setActiveScreen('login');
        }
      } catch (err) {
        console.warn('Session check error:', err);
        if (mounted) {
          setSession(null);
          setActiveScreen('login');
        }
      } finally {
        if (mounted) {
          setIsLoadingAuth(false);
        }
      }
    }

    checkAuthSession();

    return () => {
      mounted = false;
    };
  }, []);

  const handleLoginSuccess = async (newSession) => {
    setSession(newSession);
    await loadUserData();
    setActiveScreen('dashboard');
    sessionStorage.setItem('stainscope_active_screen', 'dashboard');
  };

  const handleSaveAnalysis = (newAnalysis) => {
    setAnalysesHistory((prev) => {
      const exists = prev.some((item) => item.id === newAnalysis.id || (item.dbId && item.dbId === newAnalysis.dbId));
      if (exists) return prev;
      return [newAnalysis, ...prev];
    });
  };

  const handleDeleteAnalysis = async (analysis) => {
    const targetId = analysis.dbId || analysis.id;
    if (targetId) {
      await deleteAnalysis(targetId);
      await loadUserData();
    }
  };

  const handleDeleteNote = async (noteId) => {
    await deleteNote(noteId);
    await loadUserData();
  };

  const handleSaveComparison = async (comparisonData) => {
    const { title, analysis_ids, ranking_summary } = comparisonData;
    const saved = await saveComparison(title || 'ARS Differential Matrix Comparison', analysis_ids || [], ranking_summary || {});
    if (saved) {
      setSavedComparisons((prev) => {
        const exists = prev.some(c => c.id === saved.id);
        if (exists) return prev;
        return [saved, ...prev];
      });
      return saved;
    }
    return null;
  };

  const handleDeleteComparison = async (compId) => {
    const compToDelete = savedComparisons.find((c) => c.id === compId);
    setSavedComparisons((prev) => prev.filter((item) => item.id !== compId));
    if (compToDelete) {
      const deletedItem = {
        id: 'del-comp-' + compToDelete.id + '-' + Date.now(),
        originalId: compToDelete.id,
        name: compToDelete.title,
        type: 'Comparison',
        deletedDate: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
        deletedTimestamp: Date.now(),
        itemData: compToDelete
      };
      setRecentlyDeleted((prev) => [deletedItem, ...prev]);
    }
    await deleteComparison(compId);
  };

  const handleRestoreItem = async (deletedItem) => {
    const targetId = deletedItem.dbId || deletedItem.originalId || deletedItem.id;
    if (targetId) {
      if (deletedItem.type === 'Note') {
        await restoreNote(targetId);
      } else {
        await restoreAnalysis(targetId);
      }
      await loadUserData();
    }
  };

  const handleNavigate = (screenId, extraData = {}) => {
    const isProtected = ['dashboard', 'upload', 'processing', 'results', 'compare', 'history', 'reports', 'profile'].includes(screenId);
    if (isProtected && !session) {
      setActiveScreen('login');
      sessionStorage.setItem('stainscope_active_screen', 'login');
      return;
    }

    if (['profile', 'history', 'reports', 'dashboard'].includes(screenId) && session) {
      loadUserData();
    }

    if (screenId === 'processing' && extraData) {
      setProcessingPayload(extraData);
    }
    if (extraData?.analysis) {
      setCurrentAnalysis(extraData.analysis);
      try {
        sessionStorage.setItem('stainscope_current_analysis', JSON.stringify(extraData.analysis));
      } catch (e) {}
    } else if (extraData?.analysisId) {
      const found = analysesHistory.find(a => a.id === extraData.analysisId || a.dbId === extraData.analysisId);
      if (found) {
        setCurrentAnalysis(found);
        try {
          sessionStorage.setItem('stainscope_current_analysis', JSON.stringify(found));
        } catch (e) {}
      }
    }
    if (extraData?.selectedSamples && Array.isArray(extraData.selectedSamples)) {
      setSelectedCompareSamples(extraData.selectedSamples);
    } else if (extraData?.sampleA || extraData?.sampleB) {
      const sampleA = extraData.sampleA || selectedCompareSamples[0] || null;
      const sampleB = extraData.sampleB || selectedCompareSamples[1] || null;
      const validSamples = [sampleA, sampleB].filter(Boolean);
      setSelectedCompareSamples(validSamples);
    }
    setActiveScreen(screenId);
    sessionStorage.setItem('stainscope_active_screen', screenId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Render session restoration loading screen while checking initial authentication
  if (isLoadingAuth) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#060203',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#ffffff',
        fontFamily: 'Inter, system-ui, sans-serif'
      }}>
        <div style={{
          width: 44,
          height: 44,
          border: '4px solid rgba(139, 29, 29, 0.25)',
          borderTopColor: '#8B1D1D',
          borderRadius: '50%',
          animation: 'stainscope-spin 0.8s linear infinite'
        }} />
        <style>{`@keyframes stainscope-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
        <h4 style={{ marginTop: 20, fontWeight: 700, fontSize: '1rem', letterSpacing: '0.04em', color: 'rgba(255, 255, 255, 0.85)' }}>
          Restoring StainScope Session...
        </h4>
      </div>
    );
  }

  const renderScreen = () => {
    const isProtected = ['dashboard', 'upload', 'processing', 'results', 'compare', 'history', 'reports', 'profile'].includes(activeScreen);
    if (isProtected && !session) {
      return <LoginScreen onNavigate={handleNavigate} onLoginSuccess={handleLoginSuccess} />;
    }

    switch (activeScreen) {
      case 'splash':
        return <SplashScreen onNavigate={handleNavigate} />;
      case 'login':
        return <LoginScreen onNavigate={handleNavigate} onLoginSuccess={handleLoginSuccess} />;
      case 'signup':
        return <SignUpScreen onNavigate={handleNavigate} onLoginSuccess={handleLoginSuccess} />;
      case 'forgot-password':
        return <ForgotPasswordScreen onNavigate={handleNavigate} />;
      case 'otp':
        return <OtpScreen onNavigate={handleNavigate} />;
      case 'reset-password':
        return <ResetPasswordScreen onNavigate={handleNavigate} />;
      case 'account-created':
        return <AccountCreatedScreen onNavigate={handleNavigate} />;
      case 'dashboard':
        return <DashboardScreen onNavigate={handleNavigate} analysesHistory={analysesHistory} userProfile={userProfile} />;
      case 'upload':
        return <UploadScreen onNavigate={handleNavigate} analysesHistory={analysesHistory} />;
      case 'processing':
        return <ProcessingScreen onNavigate={handleNavigate} currentAnalysis={currentAnalysis} onSaveAnalysis={handleSaveAnalysis} processingPayload={processingPayload} />;
      case 'results':
        return <ResultsScreen onNavigate={handleNavigate} result={currentAnalysis} />;
      case 'compare':
        return (
          <CompareScreen
            onNavigate={handleNavigate}
            analysesHistory={analysesHistory}
            initialSelectedSamples={selectedCompareSamples}
            savedComparisons={savedComparisons}
            onSaveComparison={handleSaveComparison}
            onDeleteComparison={handleDeleteComparison}
          />
        );
      case 'history':
        return (
          <HistoryScreen
            onNavigate={handleNavigate}
            analysesHistory={analysesHistory}
            onDeleteAnalysis={handleDeleteAnalysis}
          />
        );
      case 'reports':
        return (
          <ReportsScreen
            onNavigate={handleNavigate}
            analysesHistory={analysesHistory}
            currentAnalysis={currentAnalysis}
            savedComparisons={savedComparisons}
            onSaveComparison={handleSaveComparison}
            onDeleteComparison={handleDeleteComparison}
            onDeleteAnalysis={handleDeleteAnalysis}
          />
        );
      case 'profile':
        return (
          <ProfileScreen
            onNavigate={handleNavigate}
            onLogout={handleLogout}
            analysesHistory={analysesHistory}
            userProfile={userProfile}
            savedNotes={savedNotes}
            onSaveNote={(noteObj) => setSavedNotes([noteObj, ...savedNotes])}
            onDeleteNote={handleDeleteNote}
            savedComparisons={savedComparisons}
            onDeleteComparison={handleDeleteComparison}
            recentlyDeleted={recentlyDeleted}
            onRestoreItem={handleRestoreItem}
            theme={theme}
            onThemeChange={setTheme}
          />
        );
      default:
        return <SplashScreen onNavigate={handleNavigate} />;
    }
  };

  const isAuthScreen = ['splash', 'login', 'signup', 'forgot-password', 'otp', 'reset-password', 'account-created'].includes(activeScreen);

  return (
    <div style={{ minHeight: '100vh', background: activeScreen === 'splash' ? '#060203' : 'var(--bg-light-app)' }}>
      {/* Sticky Screen Switcher Bar for direct screen jumping & responsive testing */}
      <ScreenSwitcher
        activeScreen={activeScreen}
        onSelectScreen={handleNavigate}
        deviceView={deviceView}
        onSelectDevice={setDeviceView}
      />

      {/* Main App Container wrapped with selected device viewport mode */}
      <div className={`app-viewport viewport-${deviceView}`}>
        {/* Render Top Nav for Dashboard & Main Application Screens */}
        {(!isAuthScreen && session) && (
          <TopNav activeScreen={activeScreen} onNavigate={handleNavigate} onLogout={handleLogout} userProfile={userProfile} />
        )}

        {/* Screen Content */}
        <main style={{ width: '100%', flex: 1 }}>
          {renderScreen()}
        </main>
      </div>
    </div>
  );
}
