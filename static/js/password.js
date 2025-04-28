const otpInputs = document.querySelectorAll('#otp-container input');
const otpContainer = document.getElementById('otp-container');
const circleContainer = document.getElementById('circle-password');
const hiddenPassword = document.getElementById('hidden-password');
const circles = document.querySelectorAll('.circle');

otpInputs.forEach((input, idx) => {
  input.addEventListener('input', () => {
    // Move to the next input field after typing
    if (input.value.length > 0 && idx < otpInputs.length - 1) {
      otpInputs[idx + 1].focus();
    }

    // When all OTP inputs are filled, switch to the circle password style
    const value = Array.from(otpInputs).map(i => i.value).join('');
    if (value.length === otpInputs.length) {
      otpContainer.classList.add('hidden');  // Hide OTP input fields
      circleContainer.classList.remove('hidden');  // Show circle password style
      hiddenPassword.value = value;  // Set the hidden password input value
      hiddenPassword.focus();  // Focus on the hidden password field
      updateCircles(value);  // Update circles based on OTP input value
    }
  });
  
  // Allow backspace to move to previous field
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Backspace' && input.value.length === 0 && idx > 0) {
      otpInputs[idx - 1].focus();
    }
  });
});

// Handle input in the hidden password field (round password style)
hiddenPassword.addEventListener('input', () => {
  const value = hiddenPassword.value;
  updateCircles(value);
  
  // Auto-submit when 8 digits are entered
  if (value.length === 8) {
    document.querySelector('form').submit();
  }
});

// Update the circles based on the current input value
function updateCircles(value) {
  circles.forEach((circle, idx) => {
    if (idx < value.length) {
      circle.classList.add('filled');
    } else {
      circle.classList.remove('filled');
    }
  });
}

// Focus on first OTP input when page loads
otpInputs[0].focus();
