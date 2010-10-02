function LoadQuizzes() {
	$("#quizlist").load("/listquiz", function () {
		$("#quizlistcontent .quizrow").click(function () {
			var key = $(this).find("input[type='checkbox']").val();
			window.location = '/quiz?key=' + key;
		});
	});
}

$(document).ready(function() {
	$("input[name='generatequiz']").click(function () {
		$("#generatequizform").load("/generatequizform", function () {
			
			$("#generatequizform input[name='cancel']").click(function () {
				$("#generatequizform").hide();
				$("#quizlist").show();
			});
			
			$("#generatequizform input[name='generate']").click(function () {
				var category = $("#generatequizform select[name='quizcategory']").val();
				$.getJSON('/generatequiz', {'category':category}, function () {
					$("#generatequizform").hide();
					$("#quizlist").show();
					LoadQuizzes();
				});
			});
			
			$("#quizlist").hide();
			$("#generatequizform").show();
			
		});
	});
	LoadQuizzes();
});