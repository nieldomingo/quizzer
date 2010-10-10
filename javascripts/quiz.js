$(document).ready(function() {
	var keys = [];
	var questionindex = 0;
	var inputs = $("input[name^='question']");
	var sessionkey = '';
	var timercount = 0;
	var pause;
	
	for (var i=0; i < inputs.length; i++) {
		keys.push(inputs.eq(i).val());
	}
	
	function uptimer() {
		timercount += 1;
		$("#timer").text('time elapsed: ' + timercount + 's');
		pause = setTimeout(uptimer, 1000);
	}
	
	function starttimer() {
		timercount = 0;
		pause = setTimeout(uptimer, 1000);
		$("#timer").html('time elapsed: 0s');
	}
	
	function stoptimer() {
		clearTimeout(pause);
	}
	
	function LoadStats() {
		var quizkey = $("input[name='quizkey']").val();
		$("#quizcontent").load('/quizstats', {'quizkey': quizkey}, function () {
			$(".resultrow").click( function () {
				var key = $(this).find("input[type='checkbox']").val();
				$("#quizresult").load('/quizresult', {'quizsession': key}, function () {
					$("#quizcontent").hide();
					$("#quizresult").show();
					$("#quizresult input[name='closeresult']").click( function () {
						$("#quizcontent").show();
						$("#quizresult").hide();
					});
				});
			});
		});
	}
	
	function LoadQuestion(sessionkey) {
		if (questionindex < keys.length) {
			var key = keys[questionindex];
			starttimer();
			$("#quizcontent").load('/quizquestionview', {'key': key}, function () {
				$("#questioncounter").html((questionindex + 1) + '/' + keys.length);
				$("input[name='submit']").click( function () {
					var that = $(this).busy({'img': '/images/busy.gif'});
					stoptimer();
					var answer = $("input[name='answer']").val();
					
					$.getJSON('/quizquestionanswer',
						{'key': key, 'answer': answer, 'sessionkey': sessionkey, 'duration': timercount},
						function (data) {
							/*if (data.result == 'correct') {
								alert("answer is correct");
							}
							else {
								alert("answer is wrong");
							}*/
							questionindex += 1;
							that.busy("hide");
							LoadQuestion(sessionkey);
							
					});
				});
			});
		}
		else {
			var quizkey = $("input[name='quizkey']").val();
			$("#quizcontent").load('/quizend',
									{'quizkey': quizkey, 'sessionkey': sessionkey},
									function () {
										$("#quizcontent input[name='closeresults']").click( function () {
											$(".controls").show();
											LoadStats();
											questionindex = 0;
										});
									});
		}
	}
	
	$("input[name='start']").click( function () {
		$(".controls").hide();
		var quizkey = $("input[name='quizkey']").val();
		$.getJSON('/startquiz', {'quizkey': quizkey}, function (data) {
			LoadQuestion(data.sessionkey);
		});
	});
	
	LoadStats();

});