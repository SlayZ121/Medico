function sum() {
    var num1 = document.getElementById('number1');
    var num2 = document.getElementById('number2');
    if (num1.value !== '' && num2.value !== '') {
      var a = parseFloat(num1.value);
      var b = parseFloat(num2.value);
      var sum = (a / (b * b)) * 10000;
      document.getElementById('result').value = sum.toFixed(2);
      document.getElementById('bmi').value = sum.toFixed(2); // Set the BMI value for body fat calculation
      check(); // Automatically calculate body fat percentage
    }
  }

  function convert() {
    var feet = parseInt(document.cform.feet.value) || 0;
    var inches = parseInt(document.cform.inches.value) || 0;
    var icm = (feet * 12) + inches;
    var cm = icm * 2.54;
    document.getElementById('cm').value = cm.toFixed(2);
  }

  function pkconvert() {
    var pound = parseInt(document.cform.pound.value) || 0;
    var kg = pound * 0.45359237;
    document.getElementById('kg').value = kg.toFixed(2);
  }

  function check() {
    var age = document.fform.age.value;
    var bmi = document.fform.bmi.value;
    var sex = document.getElementById('male').checked ? 1 : 0;
    var fat = 0;

    if (age <= 15) {
      fat = (1.51 * bmi) - (0.70 * age) - (3.6 * sex) + 1.4;
    } else {
      fat = (1.20 * bmi) + (0.23 * age) - (10.8 * sex) - 5.4;
    }
    document.getElementById('fat').value = fat.toFixed(2);
  }