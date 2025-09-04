// src/utils/calculations.js
class Calculations {
    constructor() {
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

    calculateCoreProfile(name, birthdate) {
        console.log('Calculating core profile...');
        
        if (!name || !birthdate) {
            throw new Error('Name and birthdate are required for core profile calculation');
        }

        try {
            // Используем локальные методы вместо API
            const lifePath = this.calculateLifePathNumber(birthdate);
            const birthday = this.calculateBirthdayNumber(birthdate);
            const expression = this.calculateExpressionNumber(name);
            const soul = this.calculateSoulNumber(name);
            const personality = this.calculatePersonalityNumber(name);

            // Формируем объект профиля
            const coreProfile = {
                lifePath,
                birthday,
                expression,
                soul,
                personality
            };

            console.log('Core profile calculated successfully:', coreProfile);
            return coreProfile;
        } catch (error) {
            console.error('Calculation error:', error);
            throw error;
        }
    }

    calculateExtendedProfile(name, birthdate) {
        console.log('Calculating extended profile...');
        
        try {
            // Calculate extended numbers (balance, growth, realization, mind)
            const balance = this.calculateBalanceNumber(birthdate);
            const growth = this.calculateGrowthNumber(birthdate);
            const realization = this.calculateRealizationNumber(name);
            const mind = this.calculateMindNumber(name, birthdate);

            const extendedProfile = {
                balance,
                growth,
                realization,
                mind
            };

            console.log('Extended profile calculated successfully:', extendedProfile);
            return extendedProfile;
        } catch (error) {
            console.error('Extended calculation error:', error);
            throw error;
        }
    }

    calculateBridges(coreProfile) {
        console.log('Calculating bridges...');
        
        try {
            if (!coreProfile) {
                throw new Error('Core profile is required for bridges calculation');
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

            const bridgesProfile = {
                expression_soul,
                soul_personality,
                life_soul,
                life_personality
            };

            console.log('Bridges calculated successfully:', bridgesProfile);
            return bridgesProfile;
        } catch (error) {
            console.error('Bridges calculation error:', error);
            throw error;
        }
    }

    calculateCycles(name, birthdate) {
        console.log('Calculating cycles...');
        
        try {
            if (!name || !birthdate) {
                throw new Error('Name and birthdate are required for cycles calculation');
            }

            // Calculate personal year
            const personalYear = this.calculatePersonalYear(birthdate);
            
            // Calculate pinnacles
            const pinnacles = this.calculatePinnacles(birthdate);

            const cyclesProfile = {
                personalYear,
                pinnacles
            };

            console.log('Cycles calculated successfully:', cyclesProfile);
            return cyclesProfile;
        } catch (error) {
            console.error('Cycles calculation error:', error);
            throw error;
        }
    }

    calculatePartnerCompatibility(name, birthdate, partnerName, partnerBirthdate) {
        console.log('Calculating partner compatibility...');
        
        try {
            if (!name || !birthdate || !partnerName || !partnerBirthdate) {
                throw new Error('All partner data is required for compatibility calculation');
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
                lifePath: this.calculateLifePathNumber(partnerBirthdate),
                birthday: this.calculateBirthdayNumber(partnerBirthdate),
                expression: this.calculateExpressionNumber(partnerName),
                soul: this.calculateSoulNumber(partnerName),
                personality: this.calculatePersonalityNumber(partnerName)
            };

            const compatibilityProfile = {
                partnerA,
                partnerB
            };

            console.log('Partner compatibility calculated successfully:', compatibilityProfile);
            return compatibilityProfile;
        } catch (error) {
            console.error('Compatibility calculation error:', error);
            throw error;
        }
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