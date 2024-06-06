'use strict';

        document.addEventListener('DOMContentLoaded', function () {
            const inputs = document.querySelectorAll('.otp-input');
            const button = document.querySelector('#otp-form button[type="submit"]');

            if (button) {
                inputs.forEach((input, index1) => {
                    input.addEventListener('input', (e) => {
                        const currentInput = input;
                        const nextInput = input.nextElementSibling;
                        const prevInput = input.previousElementSibling;

                        if (currentInput.value.length > 1) {
                            currentInput.value = '';
                            return;
                        }

                        if (nextInput && nextInput.hasAttribute('disabled') && currentInput.value !== '') {
                            nextInput.removeAttribute('disabled');
                            nextInput.focus();
                        }

                        if (e.key === 'Backspace') {
                            inputs.forEach((input, index2) => {
                                if (index1 <= index2 && prevInput) {
                                    input.setAttribute('disabled', true);
                                    input.value = '';
                                    prevInput.focus();
                                }
                            });
                        }

                        if ([...inputs].every(input => input.value !== '')) {
                            button.classList.add('active');
                        } else {
                            button.classList.remove('active');
                        }
                    });
                });
            }

            // Close flash messages
            document.querySelectorAll('.close').forEach(button => {
                button.addEventListener('click', () => {
                    button.parentElement.style.display = 'none';
                });
            });

            // Form submission handling
            document.getElementById('otp-form').addEventListener('submit', function (event) {
                event.preventDefault();

                const otp = Array.from(inputs).map(input => input.value).join('');
                if (otp.length !== 4) {
                    alert('Please enter a 4-digit OTP.');
                } else {
                    const hiddenInput = document.createElement('input');
                    hiddenInput.type = 'hidden';
                    hiddenInput.name = 'otp';
                    hiddenInput.value = otp;
                    this.appendChild(hiddenInput);

                    // Submit the form
                    this.submit();
                }
            });
        });