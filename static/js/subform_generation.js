$(function() {
	$('new_kind').click(function() {
		var old_content = $(this).parent().parent();
		alert(old_content);
		var old_content = old_content.clone(true);
		var form =  $('<div class="sub_form">' +
				'<label> Name :</label> <input type="text" name="js_kind_value" />'+
		'<a class="cancel" href="">Cancel </a>'+
		'</div>');
});
});
	
