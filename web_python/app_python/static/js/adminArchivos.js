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
    } else if (directoryDropdown.value === "") {
        event.preventDefault(); // Prevent the form from submitting
        // Notify the user that they need to select a directory
        alert("Debe seleccionar una carpeta para subir el archivo");
        errorMessage.style.display = "block";
    } else {
        errorMessage.style.display = "none";
    }
});


document.getElementById("create-folder-button").addEventListener("click", function (event) {
    const folderNameInput = document.getElementById("folder-name-input");
    const folderNameValue = folderNameInput.value.trim();

    if (folderNameValue.length === 0) {
        event.preventDefault();
        alert("No ha ingresado un nombre para la carpeta");
    }
});

function setDirectoryName(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const hiddenInput = document.getElementById('target_directory_name_' + selectedOption.dataset.dirId);
    hiddenInput.value = selectedOption.dataset.dirName;
}

// Revisar si la URL tiene el parámetro 'upload success' para saber si el usuario ha subido un archivo
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has("upload_success")) {
    // Mostrarle alerta al usuario
    alert("Archivo subido con éxito");
    // Refrescar la página para quitar el parámetro y actualizar la lista de archivos
    window.location.href = window.location.pathname;
}
