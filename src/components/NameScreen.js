// src/components/NameScreen.js
class NameScreen {
    constructor(app) {
        this.app = app;
        this.element = null;
    }

    init() {
        this.element = document.getElementById('name-screen');
        if (!this.element) {
            console.error('NameScreen element not found');
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
        const submitButton = document.getElementById('name-submit');
        if (submitButton) {
            submitButton.addEventListener('click', () => {
                console.log('Name submit button clicked');
                const name = document.getElementById('name-input').value.trim();
                if (name) {
                    this.app.userData.name = name;
                    this.app.navigation.goTo('birthdate-screen');
                } else {
                    this.app.WebApp.showAlert('Пожалуйста, введите ваше имя');
                }
            });
        } else {
            console.error('Name submit button not found');
        }

        const backButton = document.getElementById('name-back');
        if (backButton) {
            backButton.addEventListener('click', () => {
                console.log('Name back button clicked');
                this.app.navigation.goBack();
            });
        } else {
            console.error('Name back button not found');
        }
    }
}

// Export the class
export { NameScreen };
