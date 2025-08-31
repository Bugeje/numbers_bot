// src/features/storage.js
class Storage {
    constructor(app) {
        this.app = app;
    }

    async saveUserData() {
        if (!this.app.WebApp.CloudStorage) return;

        try {
            const dataToSave = {
                name: this.app.userData.name,
                birthdate: this.app.userData.birthdate,
                partner: this.app.userData.partner
            };
            
            await this.app.WebApp.CloudStorage.setItem('userData', JSON.stringify(dataToSave));
        } catch (error) {
            console.warn('Could not save user data to CloudStorage:', error);
        }
    }

    async loadUserData() {
        if (!this.app.WebApp.CloudStorage) return;

        try {
            const savedData = await this.app.WebApp.CloudStorage.getItem('userData');
            if (savedData) {
                const parsedData = JSON.parse(savedData);
                this.app.userData.name = parsedData.name || '';
                this.app.userData.birthdate = parsedData.birthdate || '';
                this.app.userData.partner = parsedData.partner || { name: '', birthdate: '' };
                
                // Update UI with loaded data
                if (this.app.userData.name) {
                    document.getElementById('name-input').value = this.app.userData.name;
                }
                
                if (this.app.userData.birthdate) {
                    document.getElementById('birthdate-input').value = this.app.userData.birthdate;
                }
            }
        } catch (error) {
            console.warn('Could not load user data from CloudStorage:', error);
        }
    }
}

// Export the class
export { Storage };
