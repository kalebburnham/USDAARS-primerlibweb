function clearField(id) {
    document.getElementById(id).value="";
}

function formatSnpSequence() {
    data = document.getElementById('input_data').value;
    // Replace all carriage returns with line feeds.
    data = data.replace(new RegExp('\r', 'g'), '\n');
    // Remove excessive new lines.
    data = data.replace(new RegExp('(\n){2,}', 'g'), '\n');
    // Remove all spaces.
    data = data.replace(' ', '');

    // Regex look behinds are not supported by all browsers so care
    // is taken to remove new lines from sequences.
    correctFormat = '';
    lines = data.split('\n');
    for (var i=0; i < lines.length; i++) {

        if (lines[i].startsWith('>')) {
        // Add the allele name followed by a \n.
        correctFormat = correctFormat + lines[i] + '\n';
        continue;
        }

        if (lines[i+1]) {
        if (lines[i+1].startsWith('>')) {
            // Add new line if beginning second allele.
            correctFormat = correctFormat + lines[i] + '\n';
        } else {
            // Else the sequence is just taking up multiple lines.
            correctFormat = correctFormat + lines[i];
        }
        } else {
        correctFormat = correctFormat + lines[i]
        }
    }

    document.getElementById('input_data').value = correctFormat;
    return true;
}

function toggle_non_targets() {
    var nontarget_div = document.getElementById("non_target_div")
    var nontarget_checkbox = document.getElementById("nontargets_checkbox");

    if (nontarget_checkbox.checked) {
        nontarget_div.style.display = "block";
    } else {
        nontarget_div.style.display = "none";
        clearField("nontargets");
    }
}

/**
 * Open a File Reader and attempt to load the user's XML file
 * into the nontargets text area.
 */
function update_nontargets() {
    const reader = new FileReader();
    var file = document.getElementById('xml_upload_input').files[0]

    allowedExtensions = /(\.xml)$/i;

    if (allowedExtensions.exec(file.name)) {
        reader.readAsText(file);
        reader.onload = function(e) {
            document.getElementById("nontargets").innerText = reader.result;
        }
    } else {
        alert("Allowed file extension is .xml.");
    }
}