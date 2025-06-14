function nextStep(stepNumber) {
  const steps = document.querySelectorAll('.form-step');
  steps.forEach(step => step.classList.remove('active'));
  const target = document.getElementById('step' + stepNumber);
  if (target) {
    target.classList.add('active');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  nextStep(1); // Start at step 1
});


  // Image preview
  document.getElementById('fileInput').addEventListener('change', function () {
    const previewContainer = document.getElementById('previewContainer');
    previewContainer.innerHTML = '';
    Array.from(this.files).forEach(file => {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.margin = '5px';
        previewContainer.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  });


