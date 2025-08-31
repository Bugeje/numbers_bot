// src/app.js - Main application class for the Telegram Mini App
import { StartScreen } from './components/StartScreen.js';
import { NameScreen } from './components/NameScreen.js';
import { BirthdateScreen } from './components/BirthdateScreen.js';
import { ResultsScreen } from './components/ResultsScreen.js';
import { PartnerScreen } from './components/PartnerScreen.js';
import { Validation } from './utils/validation.js';
import { Calculations } from './utils/calculations.js';
import { Navigation } from './utils/navigation.js';
import { AIAnalysis } from './features/aiAnalysis.js';
import { Storage } from './features/storage.js';

class NumerologyApp {
    constructor() {
        this.userData = {
            name: '',
            birthdate: '',
            coreProfile: null,
            extendedProfile: null,
            bridgesProfile: null,
            interpretation: null,
            partner: {
                name: '',
                birthdate: ''
            }
        };
        
        // Initialize Telegram WebApp
        this.WebApp = window.Telegram.WebApp;
        
        // Initialize components
        this.initComponents();
        
        // Initialize the app
        this.init();
    }
    
    initComponents() {
        // Initialize utilities
        this.validation = Validation; // Use the class directly since it only has static methods
        this.calculations = new Calculations(this);
        this.navigation = new Navigation(this);
        
        // Initialize features
        this.aiAnalysis = new AIAnalysis(this);
        this.storage = new Storage(this);
        
        // Initialize screens
        this.startScreen = new StartScreen(this);
        this.nameScreen = new NameScreen(this);
        this.birthdateScreen = new BirthdateScreen(this);
        this.resultsScreen = new ResultsScreen(this);
        this.partnerScreen = new PartnerScreen(this);
    }
    
    init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeApp();
            });
        } else {
            // DOM is already loaded
            this.initializeApp();
        }
    }
    
    initializeApp() {
        console.log('Initializing app components...');
        
        // Initialize component DOM elements
        this.startScreen.init();
        this.nameScreen.init();
        this.birthdateScreen.init();
        this.resultsScreen.init();
        this.partnerScreen.init();
        
        // Set up Telegram WebApp
        this.WebApp.ready();
        this.WebApp.expand();
        
        // Set header color if supported
        if (this.WebApp.setHeaderColor) {
            try {
                this.WebApp.setHeaderColor('secondary_bg_color');
            } catch (e) {
                console.warn('Could not set header color:', e);
            }
        }
        
        // Apply theme colors
        this.applyThemeColors();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Show start screen
        this.navigation.goTo('start-screen');
        
        // Set up back button if supported
        this.setupBackButton();
        
        // Try to load user data from CloudStorage if supported
        this.storage.loadUserData();
        
        console.log('App initialized successfully');
    }
    
    applyThemeColors() {
        // Apply Telegram theme colors to CSS variables
        const theme = this.WebApp.themeParams;
        document.documentElement.style.setProperty('--tg-theme-bg-color', theme.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-text-color', theme.text_color || '#000000');
        document.documentElement.style.setProperty('--tg-theme-hint-color', theme.hint_color || '#999999');
        document.documentElement.style.setProperty('--tg-theme-link-color', theme.link_color || '#28a8ea');
        document.documentElement.style.setProperty('--tg-theme-button-color', theme.button_color || '#28a8ea');
        document.documentElement.style.setProperty('--tg-theme-button-text-color', theme.button_text_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', theme.secondary_bg_color || '#f1f1f1');
    }
    
    setupEventListeners() {
        // Set up event listeners for each screen
        this.startScreen.setupEventListeners();
        this.nameScreen.setupEventListeners();
        this.birthdateScreen.setupEventListeners();
        this.resultsScreen.setupEventListeners();
        this.partnerScreen.setupEventListeners();
        
        // Theme change event
        this.WebApp.onEvent('themeChanged', () => {
            this.applyThemeColors();
        });
    }
    
    setupBackButton() {
        // Set up back button functionality if supported
        if (this.WebApp.BackButton) {
            try {
                this.WebApp.BackButton.onClick(() => {
                    this.navigation.goBack();
                });
            } catch (e) {
                console.warn('Could not set up back button:', e);
            }
        }
    }
    
    showLoading(show) {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            if (show) {
                loadingElement.classList.remove('hidden');
            } else {
                loadingElement.classList.add('hidden');
            }
        }
    }
    
    restart() {
        // Clear user data
        this.userData = {
            name: '',
            birthdate: '',
            coreProfile: null,
            extendedProfile: null,
            bridgesProfile: null,
            interpretation: null,
            partner: {
                name: '',
                birthdate: ''
            }
        };
        
        // Clear input fields
        document.getElementById('name-input').value = '';
        document.getElementById('birthdate-input').value = '';
        document.getElementById('partner-name-input').value = '';
        document.getElementById('partner-birthdate-input').value = '';
        
        // Save cleared data to CloudStorage
        this.storage.saveUserData();
        
        // Go back to start screen
        this.navigation.goTo('start-screen');
    }
    
    // Screen update methods
    updateResultsScreen() {
        if (this.userData.coreProfile) {
            document.getElementById('life-path-value').textContent = this.userData.coreProfile.lifePath;
            document.getElementById('birthday-value').textContent = this.userData.coreProfile.birthday;
            document.getElementById('expression-value').textContent = this.userData.coreProfile.expression;
            document.getElementById('soul-value').textContent = this.userData.coreProfile.soul;
            document.getElementById('personality-value').textContent = this.userData.coreProfile.personality;
            document.getElementById('destiny-value').textContent = this.userData.coreProfile.destiny;
        }
    }
    
    updateExtendedScreen() {
        if (this.userData.extendedProfile) {
            document.getElementById('balance-value').textContent = this.userData.extendedProfile.balance;
            document.getElementById('growth-value').textContent = this.userData.extendedProfile.growth;
            document.getElementById('realization-value').textContent = this.userData.extendedProfile.realization;
            document.getElementById('mind-value').textContent = this.userData.extendedProfile.mind;
        }
    }
    
    updateBridgesScreen() {
        if (this.userData.bridgesProfile) {
            document.getElementById('expression-soul-value').textContent = this.userData.bridgesProfile.expression_soul;
            document.getElementById('soul-personality-value').textContent = this.userData.bridgesProfile.soul_personality;
            document.getElementById('life-soul-value').textContent = this.userData.bridgesProfile.life_soul;
            document.getElementById('life-personality-value').textContent = this.userData.bridgesProfile.life_personality;
        }
    }
    
    updateCyclesScreen() {
        if (this.userData.cyclesProfile) {
            document.getElementById('personal-year-value').textContent = this.userData.cyclesProfile.personalYear;
            // Update pinnacles
            const pinnaclesContainer = document.getElementById('pinnacles-container');
            if (pinnaclesContainer && this.userData.cyclesProfile.pinnacles) {
                pinnaclesContainer.innerHTML = this.userData.cyclesProfile.pinnacles
                    .map((pinnacle, index) => `
                        <div class="profile-item">
                            <span class="profile-label">Пик ${index + 1}:</span>
                            <span class="profile-value">${pinnacle}</span>
                        </div>
                    `).join('');
            }
        }
    }
    
    updateCompatibilityScreen() {
        if (this.userData.compatibilityProfile) {
            // Update partner A
            document.getElementById('partner-a-life-path').textContent = this.userData.compatibilityProfile.partnerA.lifePath;
            document.getElementById('partner-a-birthday').textContent = this.userData.compatibilityProfile.partnerA.birthday;
            document.getElementById('partner-a-expression').textContent = this.userData.compatibilityProfile.partnerA.expression;
            document.getElementById('partner-a-soul').textContent = this.userData.compatibilityProfile.partnerA.soul;
            document.getElementById('partner-a-personality').textContent = this.userData.compatibilityProfile.partnerA.personality;
            
            // Update partner B
            document.getElementById('partner-b-life-path').textContent = this.userData.compatibilityProfile.partnerB.lifePath;
            document.getElementById('partner-b-birthday').textContent = this.userData.compatibilityProfile.partnerB.birthday;
            document.getElementById('partner-b-expression').textContent = this.userData.compatibilityProfile.partnerB.expression;
            document.getElementById('partner-b-soul').textContent = this.userData.compatibilityProfile.partnerB.soul;
            document.getElementById('partner-b-personality').textContent = this.userData.compatibilityProfile.partnerB.personality;
        }
    }
    
    updateInterpretationScreen() {
        if (this.userData.interpretation) {
            document.getElementById('interpretation-content').innerHTML = this.userData.interpretation;
        }
    }
}

// Export for potential use in other modules
export { NumerologyApp };