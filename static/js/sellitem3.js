const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');

fileInput.addEventListener('change', function () {
previewContainer.innerHTML = ''; // Clear existing previews
const files = Array.from(this.files);

files.forEach((file, index) => {
    if (file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('preview-wrapper');

        const img = document.createElement('img');
        img.src = e.target.result;

        const closeBtn = document.createElement('span');
        closeBtn.classList.add('close-button');
        closeBtn.innerHTML = '×';
        closeBtn.title = 'Remove photo';
        closeBtn.onclick = () => wrapper.remove();

        wrapper.appendChild(img);
        wrapper.appendChild(closeBtn);
        previewContainer.appendChild(wrapper);
    };
    reader.readAsDataURL(file);
    }
});
});