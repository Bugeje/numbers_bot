// src/components/ResultsScreen.js
class ResultsScreen {
    constructor(app) {
        this.app = app;
        this.element = null;
    }

    init() {
        this.element = document.getElementById('results-screen');
        if (!this.element) {
            console.error('ResultsScreen element not found');
        }
    }

    show() {
        if (this.element) {
            this.element.classList.remove('hidden');
            this.app.WebApp.BackButton.show();
            this.updateUserInfo();
        }
    }

    hide() {
        if (this.element) {
            this.element.classList.add('hidden');
        }
    }

    updateUserInfo() {
        if (this.app.userData.name && this.app.userData.birthdate) {
            const userInfoElement = document.getElementById('user-info');
            if (userInfoElement) {
                userInfoElement.innerHTML = `
                    <strong>${this.app.userData.name}</strong><br>
                    ${this.app.userData.birthdate}
                `;
            }
        }
    }

    setupEventListeners() {
        // Results screen - feature cards
        const interpretationCard = document.getElementById('interpretation-card');
        if (interpretationCard) {
            interpretationCard.addEventListener('click', () => {
                console.log('Interpretation card clicked');
                this.app.aiAnalysis.showInterpretation();
            });
        } else {
            console.error('Interpretation card not found');
        }

        const extendedCard = document.getElementById('extended-card');
        if (extendedCard) {
            extendedCard.addEventListener('click', () => {
                console.log('Extended card clicked');
                this.app.calculations.calculateExtendedProfile();
            });
        } else {
            console.error('Extended card not found');
        }

        const bridgesCard = document.getElementById('bridges-card');
        if (bridgesCard) {
            bridgesCard.addEventListener('click', () => {
                console.log('Bridges card clicked');
                this.app.calculations.calculateBridges();
            });
        } else {
            console.error('Bridges card not found');
        }

        const cyclesCard = document.getElementById('cycles-card');
        if (cyclesCard) {
            cyclesCard.addEventListener('click', () => {
                console.log('Cycles card clicked');
                this.app.calculations.calculateCycles();
            });
        } else {
            console.error('Cycles card not found');
        }

        const partnerCard = document.getElementById('partner-card');
        if (partnerCard) {
            partnerCard.addEventListener('click', () => {
                console.log('Partner card clicked');
                this.app.navigation.goTo('partner-screen');
            });
        } else {
            console.error('Partner card not found');
        }

        const restartButton = document.getElementById('restart-button');
        if (restartButton) {
            restartButton.addEventListener('click', () => {
                console.log('Restart button clicked');
                this.app.restart();
            });
        } else {
            console.error('Restart button not found');
        }
    }
}

// Export the class
export { ResultsScreen };
