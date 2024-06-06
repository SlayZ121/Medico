
'use strict';
document.querySelectorAll('.close').forEach(button => {
  button.addEventListener('click', () => {
      button.parentElement.style.display = 'none';
  });
});

const inputs = document.querySelectorAll("input"),
 button = document.querySelector("button");

inputs.forEach((input, index1) => {
 input.addEventListener("keyup", (e) => {
      const currentInput = input,
     nextInput = input.nextElementSibling,
     prevInput = input.previousElementSibling;

   if (currentInput.value.length > 1) {
     currentInput.value = "";
     return;
   }
   if (nextInput && nextInput.hasAttribute("disabled") && currentInput.value !== "") {
     nextInput.removeAttribute("disabled");
     nextInput.focus();
   }

   if (e.key === "Backspace") {
     inputs.forEach((input, index2) => {
       if (index1 <= index2 && prevInput) {
         input.setAttribute("disabled", true);
         input.value = "";
         prevInput.focus();
       }
     });
   }
   if (!inputs[3].disabled && inputs[3].value !== "") {
     button.classList.add("active");
     return;
   }
   button.classList.remove("active");
 });
});

window.addEventListener("load", () => inputs[0].focus());



const addEventOnElements = function (elements, eventType, callback) {
 for (let i = 0, len = elements.length; i < len; i++) {
   elements[i].addEventListener(eventType, callback);
 }
}



const preloader = document.querySelector("[data-preloader]");

window.addEventListener("load", function () {
 preloader.classList.add("loaded");
 document.body.classList.add("loaded");
});





const navbar = document.querySelector("[data-navbar]");
const navTogglers = document.querySelectorAll("[data-nav-toggler]");
const overlay = document.querySelector("[data-overlay]");

const toggleNav = function () {
 navbar.classList.toggle("active");
 overlay.classList.toggle("active");
 document.body.classList.toggle("nav-active");
}

addEventOnElements(navTogglers, "click", toggleNav);



const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

const activeElementOnScroll = function () {
 if (window.scrollY > 100) {
   header.classList.add("active");
   backTopBtn.classList.add("active");
 } else {
   header.classList.remove("active");
   backTopBtn.classList.remove("active");
 }
}

window.addEventListener("scroll", activeElementOnScroll);


const revealElements = document.querySelectorAll("[data-reveal]");

const revealElementOnScroll = function () {
 for (let i = 0, len = revealElements.length; i < len; i++) {
   if (revealElements[i].getBoundingClientRect().top < window.innerHeight / 1.15) {
     revealElements[i].classList.add("revealed");
   } else {
     revealElements[i].classList.remove("revealed");
   }
 }
}

window.addEventListener("scroll", revealElementOnScroll);

window.addEventListener("load", revealElementOnScroll);





document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('.otp-input');
    const button = document.querySelector('.submit-btn');

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

    
    window.addEventListener('load', () => inputs[0].focus());

    
    document.getElementById('otp-form').addEventListener('submit', function (event) {
        const otp = Array.from(inputs).map(input => input.value).join('');
        if (otp.length !== 4) {
            alert('Please enter a 4-digit OTP.');
            event.preventDefault();
        } else {
            
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'otp';
            hiddenInput.value = otp;
            
            
            this.appendChild(hiddenInput);
        }
    });
});
