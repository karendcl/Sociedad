const dropArea = document.getElementById('drop-area')
const fileInput = document.getElementById('file-input')

function preventDefaults(e) {
  e.preventDefault()
  e.stopPropagation()
}

dropArea.addEventListener('dragover', preventDefaults)
dropArea.addEventListener('dragenter', preventDefaults)
dropArea.addEventListener('dragleave', preventDefaults)

dropArea.addEventListener('drop', preventDefaults)

dropArea.addEventListener('dragover', () => {
    dropArea.classList.add('drag-over')
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('drag-over')
});

dropArea.addEventListener('drop', () => {
    dropArea.classList.remove('drag-over')
});

function handleDrop(e) {
  e.preventDefault();

  const files = e.dataTransfer.files;

  if (files.length) {
    fileInput.files = files;
    handleFiles(files);
  }
}

function handleFiles(files) {
    for (const file of files) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function(e) {
            const preview = document.createElement('img');
            if (isValidFileType(file)) {
                preview.src = e.target.result;
            }
                preview.classList.add('preview-image');
                const previewContainer = document.getElementById('preview-container');
                previewContainer.appendChild(preview);
        }
    }
}

function isValidFileType(file) {
    return ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type);
}

dropArea.addEventListener('drop', handleDrop);


const textarea = document.getElementById('viewer-text');
textarea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});


textarea.style.height = textarea.scrollHeight + 'px';


// Used to toggle the menu on small screens when clicking on the menu button
function myFunction() {
  var x = document.getElementById("navDemo");
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else {
    x.className = x.className.replace(" w3-show", "");
  }
}



