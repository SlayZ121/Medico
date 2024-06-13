
'use strict';
document.querySelectorAll('.close').forEach(button => {
  button.addEventListener('click', () => {
      button.parentElement.style.display = 'none';
  });
});

const inputs = document.querySelectorAll("input"),
  button = document.querySelector("button");

//   document.addEventListener('DOMContentLoaded', (event) => {
//   const contactLink = document.querySelector('.navbar-link[href="#about"]');

//   contactLink.addEventListener('click', function(e) {
//     e.preventDefault();
//     document.querySelector('#about').scrollIntoView({ behavior: 'smooth' });
//   });
// });
// document.addEventListener('DOMContentLoaded', (event) => {
//   const contactLink = document.querySelector('.navbar-link[href="#footer"]');

//   contactLink.addEventListener('click', function(e) {
//     e.preventDefault();
//     document.querySelector('#footer').scrollIntoView({ behavior: 'smooth' });
//   });
// });



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