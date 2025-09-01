// src/features/aiAnalysis.js
import { UI } from '../utils/ui.js';

class AIAnalysis {
    constructor(app) {
        this.app = app;
    }

    async getAIAnalysis(profile) {
        console.log('Getting AI analysis for profile:', profile);
        
        try {
            // Make API call to backend for AI analysis
            const response = await fetch('/api/ai/analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ profile: profile })
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            return data.analysis;
        } catch (error) {
            console.error('AI API error:', error);
            // Fallback to sample analysis if API fails
            return this.getSampleAnalysis(profile);
        }
    }

    getSampleAnalysis(profile) {
        console.log('Generating sample analysis for profile:', profile);
        // This is a fallback implementation for demonstration
        const descriptions = {
            '1': 'Это число указывает на лидерские качества и стремление к независимости.',
            '2': 'Число 2 связано с дипломатией, сотрудничеством и чувствительностью.',
            '3': 'Тройка приносит творчество, самовыражение и оптимизм.',
            '4': 'Четверка олицетворяет стабильность, практичность и трудолюбие.',
            '5': 'Пятерка символизирует свободу, приключения и адаптивность.',
            '6': 'Шестерка связана с гармонией, заботой и ответственностью.',
            '7': 'Семерка указывает на аналитический ум, мудрость и духовность.',
            '8': 'Восьмерка приносит успех в бизнесе, материальное благополучие и власть.',
            '9': 'Девятка символизирует сострадание, гуманизм и завершение циклов.',
            '11': 'Мастер-число 11 указывает на интуицию, просветление и вдохновение.',
            '22': 'Мастер-число 22 - это число Мастера, указывающее на великие свершения.',
            '33': 'Мастер-число 33 указывает на мастерство в служении другим.'
        };

        let analysis = '<h3>Анализ ядра личности</h3>';
        
        if (profile.lifePath) {
            analysis += `<p><strong>Жизненный путь (${profile.lifePath}):</strong> ${descriptions[profile.lifePath.split('(')[0]] || 'Уникальное число с особым значением.'}</p>`;
        }
        
        if (profile.birthday) {
            analysis += `<p><strong>День рождения (${profile.birthday}):</strong> ${descriptions[profile.birthday.split('(')[0]] || 'Уникальное число с особым значением.'}</p>`;
        }
        
        if (profile.expression) {
            analysis += `<p><strong>Выражение (${profile.expression}):</strong> ${descriptions[profile.expression.split('(')[0]] || 'Уникальное число с особым значением.'}</p>`;
        }
        
        if (profile.soul) {
            analysis += `<p><strong>Душа (${profile.soul}):</strong> ${descriptions[profile.soul.split('(')[0]] || 'Уникальное число с особым значением.'}</p>`;
        }
        
        if (profile.personality) {
            analysis += `<p><strong>Личность (${profile.personality}):</strong> ${descriptions[profile.personality.split('(')[0]] || 'Уникальное число с особым значением.'}</p>`;
        }
        
        return analysis;
    }

    async showInterpretation() {
        console.log('Showing interpretation...');
        if (!this.app.userData.coreProfile) {
            this.app.WebApp?.showAlert?.('Сначала рассчитайте основной профиль');
            return;
        }

        // Normalize the coreProfile data to ensure snake_case keys for backend
        const normalizedProfile = {
            life_path: this.app.userData.coreProfile.lifePath || this.app.userData.coreProfile.life_path,
            birthday: this.app.userData.coreProfile.birthday,
            expression: this.app.userData.coreProfile.expression,
            soul: this.app.userData.coreProfile.soul,
            personality: this.app.userData.coreProfile.personality
        };

        UI.showLoading(true, '🧠 Генерирую интерпретацию...');
        
        try {
            const analysis = await this.getAIAnalysis(normalizedProfile);
            this.app.userData.interpretation = analysis;
            
            UI.showLoading(false);
            this.app.navigation.goTo('interpretation-screen');
            this.app.updateInterpretationScreen();
            console.log('Interpretation shown successfully');
        } catch (error) {
            UI.showLoading(false);
            this.app.WebApp?.showAlert?.('Ошибка при получении интерпретации.');
            console.error('AI Analysis error:', error);
        }
    }
}

// Export for potential use in other modules
export { AIAnalysis };