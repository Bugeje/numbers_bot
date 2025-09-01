// src/components/BirthdateScreen.js
class BirthdateScreen {
    constructor(app) {
        this.app = app;
        this.element = null;
    }

    init() {
        this.element = document.getElementById('birthdate-screen');
        if (!this.element) {
            console.error('BirthdateScreen element not found');
        }
    }

    show() {
        if (this.element) {
            this.element.classList.remove('hidden');
            this.app.WebApp.BackButton.show();
        }
    }

    hide() {
        if (this.element) {
            this.element.classList.add('hidden');
        }
    }

    setupEventListeners() {
        const submitButton = document.getElementById('birthdate-submit');
        if (submitButton) {
            submitButton.addEventListener('click', () => {
                console.log('Birthdate submit button clicked');
                const birthdate = document.getElementById('birthdate-input').value.trim();
                if (this.app.validation.isValidDate(birthdate)) {
                    this.app.userData.birthdate = birthdate;
                    // Вызываем метод calculateCoreProfile из app.js, а не из calculations
                    this.app.calculateCoreProfile();
                } else {
                    this.app.WebApp.showAlert('Пожалуйста, введите корректную дату рождения в формате ДД.ММ.ГГГГ');
                }
            });
        } else {
            console.error('Birthdate submit button not found');
        }

        const backButton = document.getElementById('birthdate-back');
        if (backButton) {
            backButton.addEventListener('click', () => {
                console.log('Birthdate back button clicked');
                this.app.navigation.goBack();
            });
        } else {
            console.error('Birthdate back button not found');
        }
    }
}

// Export the class
export { BirthdateScreen };