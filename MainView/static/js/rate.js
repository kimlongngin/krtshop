

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


$(document).ready(function(){
  $("#star1").click(function(){
  	$productID = $("#productID").val();
    $rate_number = 1;
    $rate = 1;
    $.ajax({
    	type: "GET",
    	headers: { "X-CSRFToken": getCookie("csrftoken") },
    	url: "/product/request_rate",
		data: {
			'productID': $productID ,
			'rate_number': $rate_number,
			'rate':$rate,
		},
		success: function () {
			// $('#message').html("<h2>Contact Form Submitted!</h2>")
			console.log("success");
		},

    });

  });


  $("#star2").click(function(){
    $productID = $("#productID").val();
    $rate_number = 2;
    $rate = 2;
  });
  $("#star3").click(function(){
    $productID = $("#productID").val();
    $rate_number = 3;
    $rate = 3;
  });
  $("#star4").click(function(){
    $productID = $("#productID").val();
    $rate_number = 4;
    $rate = 4;
  });
  $("#star5").click(function(){
    $productID = $("#productID").val();
    $rate_number = 5;
    $rate = 5;
  });

});

