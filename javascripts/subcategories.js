$(document).ready(function() {
	$("input[name='addsubcategory']").button();
	
	$("#dialog-subcategory-success").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$("#dialog-subcategory-success").dialog("close");
			}
		}
	});
	
	$("#dialog-subcategory-failed").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$("#dialog-subcategory-failed").dialog("close");
			}
		}
	});
	
	$("#dialog-subcategory-invalid").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$("#dialog-subcategory-invalid").dialog("close");
			}
		}
	});
	
	$("#dialog-subcategory-form").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				var category = $("select[name='category']").val();
				var subcategoryname = $("#dialog-subcategory-form input[name='subcategoryname']").val();
				var subcategorykey = $("#dialog-subcategory-form input[name='subcategorykey']").val();
				
				if (subcategoryname) {
					if (subcategorykey) {
						$.post('/trainer/subcategories/save',
							{'category': category, 'subcategoryname': subcategoryname, 'key': subcategorykey},
							function (data) {
								if (data['result'] == 'saved') {
									$("#dialog-subcategory-success").dialog("open");
									LoadSubcategories();
								}
								else {
									$("#dialog-subcategory-failed").dialog("open");
								}
								$("#dialog-subcategory-form").dialog("close");
							},
							'json');
					}
					else {
						$.post('/trainer/subcategories/save',
							{'category': category, 'subcategoryname': subcategoryname},
							function (data) {
								if (data['result'] == 'saved') {
									$("#dialog-subcategory-success").dialog("open");
									LoadSubcategories();
								}
								else {
									$("#dialog-subcategory-failed").dialog("open");
								}
								
								$("#dialog-subcategory-form").dialog("close");
							},
							'json');
					}
				}
				else {
					$("#dialog-subcategory-invalid").dialog("open");
				}
			},
			'Cancel': function () {
				$(this).dialog("close");
			}
		}
	});
	
	var LoadSubcategories = function () {
		var category = $("select[name='category']").val();
		$("#subcategorylist").load("/trainer/subcategories/list",
			{'category': category},
			function () {
				$("#subcategorylist input[type='button']").button();
				$("#subcategorylist input[type='button']").click( function () {
					var subcategorykey = $(this).attr('name');
					var subcategoryname = $(this).parent().children("input[name='subcategoryname']").val();
					$("#dialog-subcategory-form input[name='subcategorykey']").val(subcategorykey);
					$("#dialog-subcategory-form input[name='subcategoryname']").val(subcategoryname);
					$("#dialog-subcategory-form").dialog("open");
				});
			});
	};
	
	$("input[name='addsubcategory']").click( function () {
		$("#dialog-subcategory-form input[name='subcategorykey']").val('');
		$("#dialog-subcategory-form input[name='subcategoryname']").val('');
		$("#dialog-subcategory-form").dialog("open");
	});
	
	$("select[name='category']").change(function () {
		LoadSubcategories();
	});
	
	LoadSubcategories();
});