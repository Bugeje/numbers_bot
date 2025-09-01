// src/utils/calculations.js
class Calculations {
    constructor(app) {
        this.app = app;
        // Define master and karmic numbers to match Python implementation
        this.MASTER_NUMBERS = new Set([11, 22, 33, 44, 55, 66, 77, 88, 99]);
        this.KARMIC_NUMBERS = new Set([13, 14, 16, 19]);
    }

    reduceNumber(num) {
        if (typeof num !== 'number') {
            num = parseInt(num, 10);
        }
        
        const original = num;
        while (num > 9) {
            num = num.toString().split('').reduce((sum, digit) => sum + parseInt(digit, 10), 0);
        }
        
        // Check if original number is a master or karmic number
        if (this.MASTER_NUMBERS.has(original) || this.KARMIC_NUMBERS.has(original)) {
            return `${num}(${original})`;
        }
        return num.toString();
    }

    nameToNumbers(name) {
        const charMap = {
            'а': 1, 'б': 2, 'в': 3, 'г': 4, 'д': 5, 'е': 6, 'ё': 7, 'ж': 8, 'з': 9,
            'и': 1, 'й': 2, 'к': 3, 'л': 4, 'м': 5, 'н': 6, 'о': 7, 'п': 8, 'р': 9,
            'с': 1, 'т': 2, 'у': 3, 'ф': 4, 'х': 5, 'ц': 6, 'ч': 7, 'ш': 8, 'щ': 9,
            'ъ': 1, 'ы': 2, 'ь': 3, 'э': 4, 'ю': 5, 'я': 6
        };
        
        return name.toUpperCase().split('').map(char => charMap[char.toLowerCase()] || 0);
    }

    calculateSumByLetters(text, filterFunc) {
        const charMap = {
            'а': 1, 'б': 2, 'в': 3, 'г': 4, 'д': 5, 'е': 6, 'ё': 7, 'ж': 8, 'з': 9,
            'и': 1, 'й': 2, 'к': 3, 'л': 4, 'м': 5, 'н': 6, 'о': 7, 'п': 8, 'р': 9,
            'с': 1, 'т': 2, 'у': 3, 'ф': 4, 'х': 5, 'ц': 6, 'ч': 7, 'ш': 8, 'щ': 9,
            'ъ': 1, 'ы': 2, 'ь': 3, 'э': 4, 'ю': 5, 'я': 6
        };
        
        return text.toUpperCase().split('').reduce((sum, char) => {
            if (charMap[char.toLowerCase()] && filterFunc(char.toLowerCase())) {
                return sum + charMap[char.toLowerCase()];
            }
            return sum;
        }, 0);
    }

    calculateLifePathNumber(dateStr) {
        const parts = dateStr.trim().split(".");
        const day = this.reduceNumber(parseInt(parts[0]));
        const month = this.reduceNumber(parseInt(parts[1]));
        const year = this.reduceNumber(parseInt(parts[2]));
        const total = [day, month, year].reduce((sum, num) => sum + parseInt(num.split("(")[0]), 0);
        return this.reduceNumber(total);
    }

    calculateBirthdayNumber(dateStr) {
        return this.reduceNumber(parseInt(dateStr.trim().split(".")[0]));
    }

    calculateExpressionNumber(fullName) {
        return this.reduceNumber(this.nameToNumbers(fullName).reduce((sum, num) => sum + num, 0));
    }

    calculateSoulNumber(fullName) {
        const vowels = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я'];
        return this.reduceNumber(this.calculateSumByLetters(fullName, char => vowels.includes(char)));
    }

    calculatePersonalityNumber(fullName) {
        const vowels = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я'];
        return this.reduceNumber(this.calculateSumByLetters(fullName, char => !vowels.includes(char)));
    }

    calculateCoreProfile() {
        console.log('Calculating core profile...');
        const { name, birthdate } = this.app.userData;
        
        if (!name || !birthdate) {
            this.app.WebApp?.showAlert?.('Пожалуйста, введите имя и дату рождения');
            return Promise.resolve();
        }

        try {
            // Используем локальные методы вместо API
            const lifePath = this.calculateLifePathNumber(birthdate);
            const birthday = this.calculateBirthdayNumber(birthdate);
            const expression = this.calculateExpressionNumber(name);
            const soul = this.calculateSoulNumber(name);
            const personality = this.calculatePersonalityNumber(name);

            // Формируем объект профиля
            this.app.userData.coreProfile = {
                lifePath,
                birthday,
                expression,
                soul,
                personality
            };

            console.log('Core profile calculated successfully:', this.app.userData.coreProfile);
            return Promise.resolve(this.app.userData.coreProfile);
        } catch (error) {
            this.app.WebApp?.showAlert?.('Ошибка при расчете. Пожалуйста, проверьте введенные данные.');
            console.error('Calculation error:', error);
            return Promise.reject(error);
        }
    }

    calculateExtendedProfile() {
        console.log('Calculating extended profile...');
        
        setTimeout(() => {
            try {
                // Calculate extended numbers (balance, growth, realization, mind)
                const balance = this.calculateBalanceNumber(this.app.userData.birthdate);
                const growth = this.calculateGrowthNumber(this.app.userData.birthdate);
                const realization = this.calculateRealizationNumber(this.app.userData.name);
                const mind = this.calculateMindNumber(this.app.userData.name, this.app.userData.birthdate);

                this.app.userData.extendedProfile = {
                    balance,
                    growth,
                    realization,
                    mind
                };

                this.app.navigation.goTo('extended-screen');
                this.app.updateExtendedScreen();
                console.log('Extended profile calculated successfully:', this.app.userData.extendedProfile);
            } catch (error) {
                this.app.WebApp?.showAlert?.('Ошибка при расчете расширенного профиля.');
                console.error('Extended calculation error:', error);
            }
        }, 100);
    }

    calculateBridges() {
        console.log('Calculating bridges...');
        
        setTimeout(() => {
            try {
                const { coreProfile } = this.app.userData;
                
                if (!coreProfile) {
                    this.app.WebApp?.showAlert?.('Сначала рассчитайте основной профиль');
                    return;
                }

                const expression_soul = this.reduceNumber(
                    Math.abs(parseInt(coreProfile.expression) - parseInt(coreProfile.soul))
                );
                const soul_personality = this.reduceNumber(
                    Math.abs(parseInt(coreProfile.soul) - parseInt(coreProfile.personality))
                );
                const life_soul = this.reduceNumber(
                    Math.abs(parseInt(coreProfile.lifePath) - parseInt(coreProfile.soul))
                );
                const life_personality = this.reduceNumber(
                    Math.abs(parseInt(coreProfile.lifePath) - parseInt(coreProfile.personality))
                );

                this.app.userData.bridgesProfile = {
                    expression_soul,
                    soul_personality,
                    life_soul,
                    life_personality
                };

                this.app.navigation.goTo('bridges-screen');
                this.app.updateBridgesScreen();
                console.log('Bridges calculated successfully:', this.app.userData.bridgesProfile);
            } catch (error) {
                this.app.WebApp?.showAlert?.('Ошибка при расчете мостов.');
                console.error('Bridges calculation error:', error);
            }
        }, 100);
    }

    calculateCycles() {
        console.log('Calculating cycles...');
        
        setTimeout(() => {
            try {
                const { name, birthdate } = this.app.userData;
                
                if (!name || !birthdate) {
                    this.app.WebApp?.showAlert?.('Сначала введите имя и дату рождения');
                    return;
                }

                // Calculate personal year
                const personalYear = this.calculatePersonalYear(birthdate);
                
                // Calculate pinnacles
                const pinnacles = this.calculatePinnacles(birthdate);

                this.app.userData.cyclesProfile = {
                    personalYear,
                    pinnacles
                };

                this.app.navigation.goTo('cycles-screen');
                this.app.updateCyclesScreen();
                console.log('Cycles calculated successfully:', this.app.userData.cyclesProfile);
            } catch (error) {
                this.app.WebApp?.showAlert?.('Ошибка при расчете циклов.');
                console.error('Cycles calculation error:', error);
            }
        }, 100);
    }

    calculatePartnerCompatibility() {
        console.log('Calculating partner compatibility...');
        
        setTimeout(() => {
            try {
                const { name, birthdate } = this.app.userData;
                const { partner } = this.app.userData;
                
                if (!name || !birthdate || !partner.name || !partner.birthdate) {
                    this.app.WebApp?.showAlert?.('Пожалуйста, введите данные обоих партнеров');
                    return;
                }

                // Calculate profiles for both partners
                const partnerA = {
                    lifePath: this.calculateLifePathNumber(birthdate),
                    birthday: this.calculateBirthdayNumber(birthdate),
                    expression: this.calculateExpressionNumber(name),
                    soul: this.calculateSoulNumber(name),
                    personality: this.calculatePersonalityNumber(name)
                };

                const partnerB = {
                    lifePath: this.calculateLifePathNumber(partner.birthdate),
                    birthday: this.calculateBirthdayNumber(partner.birthdate),
                    expression: this.calculateExpressionNumber(partner.name),
                    soul: this.calculateSoulNumber(partner.name),
                    personality: this.calculatePersonalityNumber(partner.name)
                };

                this.app.userData.compatibilityProfile = {
                    partnerA,
                    partnerB
                };

                this.app.navigation.goTo('compatibility-screen');
                this.app.updateCompatibilityScreen();
                console.log('Partner compatibility calculated successfully:', this.app.userData.compatibilityProfile);
            } catch (error) {
                this.app.WebApp?.showAlert?.('Ошибка при расчете совместимости.');
                console.error('Compatibility calculation error:', error);
            }
        }, 100);
    }

    // Helper functions for extended calculations
    calculateBalanceNumber(birthdate) {
        const day = parseInt(birthdate.split('.')[0]);
        return this.reduceNumber(day);
    }

    calculateGrowthNumber(birthdate) {
        const parts = birthdate.split('.');
        const month = parseInt(parts[1]);
        const day = parseInt(parts[0]);
        return this.reduceNumber(month + day);
    }

    calculateRealizationNumber(name) {
        const firstName = name.split(' ')[0];
        const firstLetterValue = this.nameToNumbers(firstName.charAt(0))[0] || 0;
        const lastName = name.split(' ').slice(-1)[0];
        const lastLetterValue = this.nameToNumbers(lastName.charAt(lastName.length - 1))[0] || 0;
        return this.reduceNumber(firstLetterValue + lastLetterValue);
    }

    calculateMindNumber(name, birthdate) {
        const firstName = name.split(' ')[0];
        const firstLetterValue = this.nameToNumbers(firstName.charAt(0))[0] || 0;
        const month = parseInt(birthdate.split('.')[1]);
        return this.reduceNumber(firstLetterValue + month);
    }

    // Helper functions for cycles calculations
    calculatePersonalYear(birthdate) {
        const currentYear = new Date().getFullYear();
        const birthDay = parseInt(birthdate.split('.')[0]);
        const birthMonth = parseInt(birthdate.split('.')[1]);
        return this.reduceNumber(birthDay + birthMonth + currentYear);
    }

    calculatePinnacles(birthdate) {
        const day = parseInt(birthdate.split('.')[0]);
        const month = parseInt(birthdate.split('.')[1]);
        const year = parseInt(birthdate.split('.')[2]);
        
        const pinnacles = [];
        
        // First pinnacle
        pinnacles.push(this.reduceNumber(day + month));
        
        // Second pinnacle
        pinnacles.push(this.reduceNumber(day + year));
        
        // Third pinnacle
        pinnacles.push(this.reduceNumber(
            parseInt(pinnacles[0]) + parseInt(pinnacles[1])
        ));
        
        // Fourth pinnacle
        pinnacles.push(this.reduceNumber(month + year));
        
        return pinnacles;
    }
}

// Export for potential use in other modules
export { Calculations };