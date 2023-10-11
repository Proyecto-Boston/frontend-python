document.getElementById("choose-file-button").addEventListener("click", function () {
    document.getElementById("file-input").click();
});

document.getElementById("upload-button").addEventListener("click", function (event) {
    const fileInput = document.getElementById("file-input");
    const errorMessage = document.getElementById("error-message");

    if (fileInput.files.length === 0) {
        event.preventDefault(); // No dejar que se envie el input form
        // Explicación de por qué el botón no funcionó
        alert("No ha seleccionado un archivo");
        errorMessage.style.display = "block";
    } else {
        errorMessage.style.display = "none";
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

document.addEventListener("DOMContentLoaded", function() {
    const deleteButtons = document.querySelectorAll(".delete-button");

    deleteButtons.forEach(button => {
        button.addEventListener("click", function() {
            const directoryId = this.closest("li").querySelector(".btn-wide").getAttribute("data-directory-id");
            // BORRAR DIRECTORIO DEL SERVIDOR AQUI
            directories = directories.filter(directory => directory.directory_id !== parseInt(directoryId));
            // Refresh the directory list (you can implement this)
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const deleteButtons = document.querySelectorAll(".delete-button");

    deleteButtons.forEach(button => {
        button.addEventListener("click", function() {
            const listItem = this.closest("li"); // Get the parent <li> element
            listItem.remove(); // Remove the <li> element from the DOM
        });
    });
});