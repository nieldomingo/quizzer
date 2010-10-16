$(document).ready(function() {
	
	function LoadQuizzers() {
		$("#maincontentcontent").load("/selectquizzer", {}, function () {
			$(".quizzerrow").click( function () {
				var key = $(this).find("input[type='checkbox']").attr('name');
				var email = $(this).find("input[type='checkbox']").val();
				
				$("#quizzerkey").val(key);
				$("#currentquizzer").text(email);
				
				$('#quizzers').hide();
				
				$('#maincontentcontent').load('/listquiz', {'quizzerkey': key}, function () {
					$(".quizrow").click( function () {
						var key = $(this).find("input[type='checkbox']").val();
						window.location = '/quiz?key=' + key + '&disabledanswer=True';
					});
				});
			});
		});
	}
	
	$("#selectquizzer").click( function () {
		LoadQuizzers();
	});
	
	LoadQuizzers();
});