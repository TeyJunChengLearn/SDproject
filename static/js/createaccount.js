//Phone number
const phoneInput = document.querySelector("#phone");
    const iti = window.intlTelInput(phoneInput, {
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
      preferredCountries: ['my', 'sg', 'us', 'gb'],
      separateDialCode: true,
      initialCountry: "my",
      nationalMode: false
    });

    // Prevent non-numeric input
    phoneInput.addEventListener('keydown', function(e) {
      // Allow: backspace, delete, tab, escape, enter
      if ([46, 8, 9, 27, 13].includes(e.keyCode) || 
          // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
          (e.keyCode == 65 && e.ctrlKey === true) || 
          (e.keyCode == 67 && e.ctrlKey === true) || 
          (e.keyCode == 86 && e.ctrlKey === true) || 
          (e.keyCode == 88 && e.ctrlKey === true) ||
          // Allow: home, end, left, right
          (e.keyCode >= 35 && e.keyCode <= 39)) {
            return;
      }
      // Ensure it's a number
      if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
      }
    });

    // Form validation
    document.getElementById('signupForm').addEventListener('submit', function(e) {
      const phoneNumber = iti.getNumber();
      if (!iti.isValidNumber()) {
        e.preventDefault();
        alert('Please enter a valid phone number');
        phoneInput.focus();
      }
    });

//Password
document.addEventListener('DOMContentLoaded', function() {
    // Phone input initialization (existing code)
    const phoneInput = document.querySelector("#phone");
    const iti = window.intlTelInput(phoneInput, {
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
      preferredCountries: ['my', 'sg', 'us', 'gb'],
      separateDialCode: true,
      initialCountry: "my",
      nationalMode: false
    });
  
    // Phone number validation (existing code)
    phoneInput.addEventListener('keydown', function(e) {
      if ([46, 8, 9, 27, 13].includes(e.keyCode) || 
          (e.keyCode == 65 && e.ctrlKey === true) || 
          (e.keyCode == 67 && e.ctrlKey === true) || 
          (e.keyCode == 86 && e.ctrlKey === true) || 
          (e.keyCode == 88 && e.ctrlKey === true) ||
          (e.keyCode >= 35 && e.keyCode <= 39)) {
            return;
      }
      if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
      }
    });
  
    // Password toggle functionality
    const togglePassword = document.querySelector('#togglePassword');
    const password = document.querySelector('#password');
    
    // Character limit enforcement
    password.addEventListener('input', function() {
      if (this.value.length > 8) {
        this.value = this.value.slice(0, 8);
      }
    });
    
    // Toggle password visibility
    togglePassword.addEventListener('click', function() {
      const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
      password.setAttribute('type', type);
      
      // Toggle icon
      this.classList.toggle('bi-eye-slash');
      this.classList.toggle('bi-eye');
    });
  
    // Form validation
    document.getElementById('signupForm').addEventListener('submit', function(e) {
      // Phone validation
      if (!iti.isValidNumber()) {
        e.preventDefault();
        alert('Please enter a valid phone number');
        phoneInput.focus();
        return;
      }
      
      // Password validation
      if (password.value.length !== 8) {
        e.preventDefault();
        password.setCustomValidity('Password must be exactly 8 characters');
        password.reportValidity();
        password.focus();
      } else {
        password.setCustomValidity('');
      }
    });
  });


//upload profile
document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('.uploadprofile').style.backgroundImage = `url('${e.target.result}')`;
            document.querySelector('.uploadprofile').style.backgroundSize = 'cover';
            document.querySelector('.uploadprofile').style.backgroundPosition = 'center';
            document.querySelector('.uploadprofile i').style.display = 'none'; // hide camera icon after upload
        }
        reader.readAsDataURL(file);
    }
});