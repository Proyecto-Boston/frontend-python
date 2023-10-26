document.getElementById("choose-file-button").addEventListener("click", function () {
    document.getElementById("file-input").click();
});

document.getElementById("upload-button").addEventListener("click", function (event) {
    const fileInput = document.getElementById("file-input");
    const directoryDropdown = document.getElementById("directory-dropdown");
    const errorMessage = document.getElementById("error-message");

    if (fileInput.files.length === 0) {
        event.preventDefault(); // Prevent the form from submitting
        // Notify the user why the button didn't work
        alert("No ha seleccionado un archivo");
        errorMessage.style.display = "block";
    } else {
        errorMessage.style.display = "none";
    }
});

document.getElementById("directory-dropdown").addEventListener("change", function () {
    const selectedDirectory = this.value;
    console.log('Selected option:', selectedDirectory);
    document.getElementById("selected-directory").value = selectedDirectory;
});

document.getElementById("create-folder-button").addEventListener("click", function (event) {
    const folderNameInput = document.getElementById("folder-name-input");
    const folderNameValue = folderNameInput.value.trim();

    if (folderNameValue.length === 0) {
        event.preventDefault();
        alert("No ha ingresado un nombre para la carpeta");
    }
});

document.getElementById("directory-dropdown").addEventListener("change", function () {
    const selectedDirectory = this.value;
    console.log('Selected option:', selectedDirectory);
    document.getElementById("selected-directory").value = selectedDirectory;
});

document.addEventListener("change", function (event) {
    if (event.target.classList.contains("target-directory")) {
        const selectedMoveDirectory = event.target.value;
        const targetId = event.target.id;
        console.log('Selected ID:', selectedMoveDirectory);
        const fileId = targetId.replace("target_directory_", "");
        console.log('File ID ' + fileId);
        document.getElementById("target_directory_move_"+fileId).value = selectedMoveDirectory;
    }
});

document.addEventListener("submit", function (event) {
    // Check if the form being submitted is for sharing a file
    if (event.target.querySelector("[name=share_file_button]")) {
        const fileForm = event.target;
        const shareEmailInput = fileForm.querySelector("[name=share_email]").value;
        console.log("Share Email:", shareEmailInput);

        // Check if the email field is empty
        if (shareEmailInput.trim() === "") {
            event.preventDefault(); // Prevent the form from submitting normally
            alert("Por favor, ingrese un correo electrónico.");
        } else {
            document.getElementById("share_user_id").value = shareEmailInput;
        }
    }
});


// Revisar si la URL tiene el parámetro 'upload success' para saber si el usuario ha subido un archivo
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has("upload_success")) {
    // Mostrarle alerta al usuario
    alert("Archivo subido con éxito");
    // Refrescar la página para quitar el parámetro y actualizar la lista de archivos
    window.location.href = window.location.pathname;
}
