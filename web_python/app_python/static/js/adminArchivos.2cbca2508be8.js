// Initialize the files array with data from the HTML table rows
const tableRows = document.querySelectorAll("tbody tr");
const files = Array.from(tableRows).map(row => ({
    name: row.getAttribute("data-file-name"),
    size: row.getAttribute("data-file-size"),
}));

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
    } /*else if (directoryDropdown.value === "") {
        event.preventDefault(); // Prevent the form from submitting
        // Notify the user that they need to select a directory
        alert("Debe seleccionar una carpeta para subir el archivo");
        errorMessage.style.display = "block";
    }*/ else {
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

// Function to sort files alphabetically A-Z
document.getElementById("sort-alphabetically-az").addEventListener("click", function () {
    files.sort((a, b) => a.name.localeCompare(b.name));
    updateTable();
});

// Function to sort files alphabetically Z-A
document.getElementById("sort-alphabetically-za").addEventListener("click", function () {
    files.sort((a, b) => b.name.localeCompare(a.name));
    updateTable();
});

// Function to sort files by size in ascending order
document.getElementById("sort-size-asc").addEventListener("click", function () {
    files.sort((a, b) => a.size.localeCompare(b.size));
    updateTable();
});

// Function to sort files by size in descending order
document.getElementById("sort-size-desc").addEventListener("click", function () {
    files.sort((a, b) => b.size.localeCompare(a.size));
    updateTable();
});

// Function to update the table with sorted data
function updateTable() {
    const tableBody = document.querySelector("tbody");
    tableBody.innerHTML = "";

    for (const file of files) {
        const row = document.createElement("tr");
        row.innerHTML = `
                <td style="text-align: center;">${file.name}</td>
                <td style="text-align: center;">${file.size}</td>
                <td style="text-align: center;">
                    <div class="dropdown">
                        <button class="btn btn-secondary btn-orange dropdown-toggle" type="button"
                            id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true"
                            aria-expanded="false">
                            Opciones
                        </button>
                        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                            <form method="post" action="{% url 'manager' %}">
                                {% csrf_token %}
                                <input type="hidden" name="download_file_name" value="{{ file.id }}">
                                <button type="submit" class="dropdown-item">Descargar</button>
                            </form>
                            <form method="post" action="{% url 'manager' %}">
                                {% csrf_token %}
                                <input type="hidden" name="change_file_name" value="{{ file.id }}">
                                <button type="submit" class="dropdown-item">Renombrar</button>
                            </form>
                            <div class="dropdown-item">
                                <form method="post" action="{% url 'manager' %}">
                                    {% csrf_token %}
                                    <input type="hidden" name="move_file_name" value="{{ file.id }}">
                                    <input type="hidden" name="move_file_fullname" value="{{ file.name }}">
                                    <select name="target_directory" required onchange="setDirectoryName(this)">
                                        <option value="">Mover</option>
                                        {% for directory in directories %}
                                            <option value="{{ directory.id }}" data-dir-name="{{ directory.name }}">{{ directory.name }}</option>
                                        {% endfor %}
                                    </select>
                                    <input type="hidden" name="target_directory_name" id="target_directory_name_{{ file.id }}">
                                    <button type="submit">Mover</button>
                                </form>
                            </div>            
                            <form method="post" action="{% url 'manager' %}">
                                {% csrf_token %}
                                <input type="hidden" name="share_file_name" value="{{ file.id }}">
                                <button type="submit" class="dropdown-item">Compartir</button>
                            </form>                                
                            <form method="post" action="{% url 'manager' %}">
                                {% csrf_token %}
                                <input type="hidden" name="delete_file_name" value="{{ file.id }}">
                                <button type="submit" class="dropdown-item">Eliminar</button>
                            </form>
                        </div>
                    </div>
                </td>
            `;
        tableBody.appendChild(row);
    }
}