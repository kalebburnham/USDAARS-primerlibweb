const REFSEQ_MIN_LENGTH = 100;
const REFSEQ_MAX_LENGTH = 20000;

function toggle_nontargets() {
    var nontarget_div = document.getElementById("nontarget_div")
    var nontarget_checkbox = document.getElementById("nontarget_checkbox");

    if (nontarget_checkbox.checked) {
        nontarget_div.style.display = "block";
    } else {
        nontarget_div.style.display = "none";
        document.getElementById("nontargets").innerText = "";
    }
}

function change_blast_site() {
    // Change the embedded BLAST website.
    site = document.getElementById('website_selector').value;
    embedded_frame = document.getElementById('embedded_blast');
    var website_height = "800";

    if (site == "") {
        embedded_frame.display = "none";
        embedded_frame.src = "";
        embedded_frame.height = "0";
    }

    if (site == "ncbi") {
        embedded_frame.src = "https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome";
        embedded_frame.height = website_height;
    }

    if (site == "graingenes") {
        embedded_frame.src = "https://wheat.pw.usda.gov/cgi-bin/seqserve/blast_wheat.cgi";
        embedded_frame.height = website_height;
    }

    if (site == "atgsp") {
        embedded_frame.src = "http://aegilops.wheat.ucdavis.edu/ATGSP/blast.php";
        embedded_frame.height = website_height;
    }
}

function open_fasta_file() {
    const reader = new FileReader();
    var file = get_file();

    allowedExtensions = /(\.fasta|\.fna|\.ffn|\.frn)$/i;

    if (allowedExtensions.exec(file.name)) {
        reader.readAsText(file);
        reader.onload = function(e) {
            document.getElementById("ref_sequence").innerText = reader.result;
        }
    } else {
        alert('Allowed file extensions are .fasta, .fna, .ffn, or .frn.')
    }
}

function open_xml_file() {
    const reader = new FileReader();
    var file = get_file();

    allowedExtensions = /(\.xml)$/i;

    if (allowedExtensions.exec(file.name)) {
        reader.readAsText(file);
        reader.onload = function(e) {
            document.getElementById("nontargets").innerText = reader.result;
        }
    } else {
        alert("Allowed file extension is XML.");
    }
}

function get_file() {
    var file = document.createElement("input");
    file.setAttribute("type", "file");
    file.click();
    return file.files[0];
}

function populate_with_length(id) {
    input = document.getElementById(id);
    length = document.getElementById("ref_sequence").textLength.toString();
    if (length > 0) {
      input.value = length;
    } else {
      input.value = 1;
    }
}

function update_reference_sequence() {
  const reader = new FileReader();
  var file = document.getElementById('fasta_upload_input').files[0]

  allowedExtensions = /(\.fasta|\.fna|\.ffn|\.frn)$/i;

  if (allowedExtensions.exec(file.name)) {
    reader.readAsText(file);
    reader.onload = function(e) {
      document.getElementById("ref_sequence").innerText = reader.result;
    }
  } else {
    alert('Allowed file extensions are .fasta, .fna, .ffn, or .frn.')
  }
}

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

function validateForm() {
  refsequenceField = document.getElementById('ref_sequence');
  fFromField = document.getElementById('fFrom');
  fToField = document.getElementById('fTo');
  rFromField = document.getElementById('rFrom');
  rToField = document.getElementById('rTo');
  pcrMinField = document.getElementById('ampliconLengthMin');
  pcrMaxField = document.getElementById('ampliconLengthMax');
  tmMinField = document.getElementById('tmMin');
  tmOptField = document.getElementById('tmOpt');
  tmMaxField = document.getElementById('tmMax');

  return (_validateRefsequence(refsequenceField) 
          && _validateFSpan(fFromField, fToField)
          && _validateRSpan(rFromField, rToField)
          && _validateAmpliconLength(pcrMinField, pcrMaxField)
          && _validateMeltingTemperatures(tmMinField, tmOptField, tmMaxField));
}


function _validateRefsequence(refsequenceField) {
len = refsequenceField.value.length;

if (len < REFSEQ_MIN_LENGTH || len > REFSEQ_MAX_LENGTH) {
  // Check the sequence is between min and max characters.
  refsequenceField.setCustomValidity("Reference sequence must contain between " + REFSEQ_MIN_LENGTH + " and " + REFSEQ_MAX_LENGTH + " characters.");
  return false;
} else {
  refsequenceField.setCustomValidity("");
  return true
}

}

function _validateFSpan(fFromField, fToField) {
if (parseInt(fToField.value) <= parseInt(fFromField.value)) {
  console.log(parseInt(fToField.value));
  console.log(parseInt(fFromField.value));
  fToField.setCustomValidity("'To' region of F primer must be larger than 'From'.");
  return false;
} else {
  console.log('clearing');
  fToField.setCustomValidity("");
  return true;
}
}

function _validateRSpan(rFromField, rToField) {
if (parseInt(rToField.value) <= parseInt(rFromField.value)) {
  rToField.setCustomValidity("'To' region of R primer must be larger than 'From'.");
  return false;
} else {
  rToField.setCustomValidity("");
  return true;
}
}

function _validateAmpliconLength(pcrMinField, pcrMaxField) {
if (parseInt(pcrMaxField.value) <= parseInt(pcrMinField.value)) {
  pcrMaxField.setCustomValidity("Maximum amplicon length must be larger than the minimum.")
  return false;
} else {
  pcrMaxField.setCustomValidity("");
  return true;
}
}

function _validateMeltingTemperatures(tmMinField, tmOptField, tmMaxField) {
tmMin = parseInt(tmMinField.value);
tmOpt = parseInt(tmOptField.value);
tmMax = parseInt(tmMaxField.value);

if (tmOpt < tmMin || tmOpt > tmMax) {
  tmMaxField.setCustomValidity("Incorrect ordering of temperatures.");
  return false;
} else {
  tmMaxField.setCustomValidity("");
  return true;
}
}