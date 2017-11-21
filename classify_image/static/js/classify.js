$(document).ready(function() {

  var dropContainer = document.getElementById('drop-container');
  dropContainer.ondragover = dropContainer.ondragend = function() {
    return false;
  };

  dropContainer.ondrop = function(e) {
    e.preventDefault();
    loadImage(e.dataTransfer.files[0])
  }

  $("#browse-button").change(function() {
    loadImage($("#browse-button").prop("files")[0]);
  });

  $('.modal').modal({
    dismissible: false,
    ready: function(modal, trigger) {
      $.ajax({
        type: "POST",
        url: '/classify_image/classify/api/',
        data: {
          'image64': $('#img-card').attr('src')
        },
        dataType: 'text',
        success: function(data) {
          loadStats(data)
        }
      }).always(function() {
        modal.modal('close');
      });
    }
  });

  $('#go-back, #go-start').click(function() {
    $('#img-card').removeAttr("src");
    $('#stat-table').html('');
    switchCard(0);
  });

  $('#upload-button').click(function() {
    $('.modal').modal('open');
  });
});

switchCard = function(cardNo) {
  var containers = [".dd-container", ".uf-container", ".dt-container"];
  var visibleContainer = containers[cardNo];
  for (var i = 0; i < containers.length; i++) {
    var oz = (containers[i] === visibleContainer) ? '1' : '0';
    $(containers[i]).animate({
      opacity: oz
    }, {
      duration: 200,
      queue: false,
    }).css("z-index", oz);
  }
}

loadImage = function(file) {
  var reader = new FileReader();
  reader.onload = function(event) {
    $('#img-card').attr('src', event.target.result);
  }
  reader.readAsDataURL(file);
  switchCard(1);
}

loadStats = function(jsonData) {
  switchCard(2);
  var data = JSON.parse(jsonData);
  if (data["success"] == true) {
    for (category in data['confidence']) {
      var percent = Math.round(parseFloat(data["confidence"][category]) * 100);
      var markup = `
      <div class="card">
        <div class="card-content black-text stat-card">
          <span class="card-title capitalize">` + category + `</span>
          <p style="float: left;">Confidence</p>
          <p style="float: right;"><b>` + percent + `%</b></p>
          <div class="progress">
            <div class="determinate" style="width: ` + percent + `%;"></div>
          </div>
        </div>
      </div>`;
      $("#stat-table").append(markup);
    }
  }
}
