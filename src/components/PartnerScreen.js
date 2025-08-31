// src/components/PartnerScreen.js
class PartnerScreen {
    constructor(app) {
        this.app = app;
        this.element = null;
    }

    init() {
        this.element = document.getElementById('partner-screen');
        if (!this.element) {
            console.error('PartnerScreen element not found');
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
        const submitButton = document.getElementById('partner-submit');
        if (submitButton) {
            submitButton.addEventListener('click', () => {
                console.log('Partner submit button clicked');
                const partnerName = document.getElementById('partner-name-input').value.trim();
                const partnerBirthdate = document.getElementById('partner-birthdate-input').value.trim();
                
                if (partnerName && this.app.validation.isValidDate(partnerBirthdate)) {
                    this.app.userData.partner.name = partnerName;
                    this.app.userData.partner.birthdate = partnerBirthdate;
                    this.app.calculations.calculatePartnerCompatibility();
                } else {
                    this.app.WebApp.showAlert('Пожалуйста, введите корректные данные партнера');
                }
            });
        } else {
            console.error('Partner submit button not found');
        }

        const backButton = document.getElementById('partner-back');
        if (backButton) {
            backButton.addEventListener('click', () => {
                console.log('Partner back button clicked');
                this.app.navigation.goBack();
            });
        } else {
            console.error('Partner back button not found');
        }
    }
}

// Export the class
export { PartnerScreen };
