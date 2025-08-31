// src/utils/navigation.js
class Navigation {
    constructor(app) {
        this.app = app;
        this.screenHistory = ['start-screen'];
    }

    goTo(screenId) {
        console.log('Navigating to screen:', screenId);
        // Hide current screen
        this.hideCurrentScreen();
        
        // Show new screen
        this.showScreen(screenId);
        
        // Update history
        this.screenHistory.push(screenId);
    }

    goBack() {
        console.log('Navigating back, history length:', this.screenHistory.length);
        if (this.screenHistory.length > 1) {
            // Hide current screen
            this.hideCurrentScreen();
            
            // Remove current screen from history
            this.screenHistory.pop();
            
            // Show previous screen
            const previousScreen = this.screenHistory[this.screenHistory.length - 1];
            console.log('Going back to:', previousScreen);
            this.showScreen(previousScreen);
        } else {
            // If we're at the start screen, go back to it
            console.log('Already at start screen, going to start screen');
            this.goTo('start-screen');
        }
    }

    showScreen(screenId) {
        console.log('Showing screen:', screenId);
        // Hide all screens
        document.querySelectorAll('[id$="-screen"]').forEach(screen => {
            screen.classList.add('hidden');
        });
        
        // Show requested screen
        const screenElement = document.getElementById(screenId);
        if (screenElement) {
            screenElement.classList.remove('hidden');
        } else {
            console.error('Screen element not found:', screenId);
        }
        
        // Handle back button visibility if supported
        if (this.app.WebApp.BackButton) {
            try {
                if (screenId === 'start-screen') {
                    this.app.WebApp.BackButton.hide();
                } else {
                    this.app.WebApp.BackButton.show();
                }
            } catch (e) {
                console.warn('Could not control back button:', e);
            }
        }
    }

    hideCurrentScreen() {
        const currentScreen = document.querySelector('[id$="-screen"]:not(.hidden)');
        if (currentScreen) {
            currentScreen.classList.add('hidden');
        }
    }
}

// Export the class
export { Navigation };
