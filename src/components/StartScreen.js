// src/components/StartScreen.js
class StartScreen {
    constructor(app) {
        this.app = app;
        this.element = null;
    }

    init() {
        this.element = document.getElementById('start-screen');
        if (!this.element) {
            console.error('StartScreen element not found');
        }
    }

    show() {
        if (this.element) {
            this.element.classList.remove('hidden');
            this.app.WebApp.BackButton.hide();
        }
    }

    hide() {
        if (this.element) {
            this.element.classList.add('hidden');
        }
    }

    setupEventListeners() {
        const startButton = document.getElementById('start-button');
        if (startButton) {
            startButton.addEventListener('click', () => {
                console.log('Start button clicked');
                this.app.navigation.goTo('name-screen');
            });
        } else {
            console.error('Start button not found');
        }
    }
}

// Export the class
export { StartScreen };