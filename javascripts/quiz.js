$(document).ready(function() {
	var keys = [];
	var questionindex = 0;
	var inputs = $("input[name^='question']");
	var sessionkey = '';
	
	for (var i=0; i < inputs.length; i++) {
		keys.push(inputs.eq(i).val());
	}
	
	function LoadQuestion(sessionkey) {
		if (questionindex < keys.length) {
			var key = keys[questionindex];
			$("#quizcontent").load('/quizquestionview', {'key': key}, function () {
				$("#questiontitle").text("Question " + (questionindex + 1));
				$("input[name='submit']").click( function () {
					var answer = $("input[name='answer']").val();
					
					$.getJSON('/quizquestionanswer',
						{'key': key, 'answer': answer, 'sessionkey': sessionkey},
						function (data) {
							if (data.result == 'correct') {
								alert("answer is correct");
							}
							else {
								alert("answer is wrong");
							}
							questionindex += 1;
							LoadQuestion(sessionkey);
							
					});
				});
			});
		}
		else {
			$("#questiontitle").text('');
			var quizkey = $("input[name='quizkey']").val();
			$("#quizcontent").load('/quizend', {'quizkey': quizkey, 'sessionkey': sessionkey});
		}
	}
	
	$("input[name='start']").click( function () {
		$("input[name='start']").hide();
		var quizkey = $("input[name='quizkey']").val();
		$.getJSON('/startquiz', {'quizkey': quizkey}, function (data) {
			LoadQuestion(data.sessionkey);
		});
	});

});