$(document).ready(function() {
	var timercount = 0;
	var pause;
	
	$("#answeredfilter").buttonset();
	$("input[name='request']").button();
	
	function uptimer() {
		timercount += 1;
		$("#elapsedtime").text(timercount + 's');
		pause = setTimeout(uptimer, 1000);
	}
	
	function starttimer() {
		timercount = 0;
		pause = setTimeout(uptimer, 1000);
		$("#elapsedtime").html('0s');
	}
	
	function stoptimer() {
		clearTimeout(pause);
	}
	
	$("#dialog-answer-result").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
				LoadQuestions(false);
			}
		}
	});
	
	$("#dialog-question-details").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
			},
			'Answer Question': function () {
				$(this).dialog("close");
				$.loading(true, {align: 'center'});
				var key = $("#dialog-question-details input[name='key']").val();
				$.getJSON('/quizzer/startquestion', {key: key}, function (data) {
					$.loading(false);
					$("#dialog-answer-question input[name='questionkey']").val(data['questionkey']);
					$("#dialog-answer-question input[name='sessionkey']").val(data['sessionkey']);
					$("#dialog-answer-question #questionvalue").html(Wiky.toHtml(data['question']));
					$("#dialog-answer-question input[name='answer']").val('');
					$("#question-diagram").html(data['diagram']);
					$("#dialog-answer-question").dialog("open");
					starttimer();
				});
			}
		}
	});
	
	$("#dialog-answer-question").dialog({
		modal: true,
		autoOpen: false,
		width: 570,
		buttons: {
			'Ok': function () {
				stoptimer();
				$(this).dialog("close");
				var questionkey = $("#dialog-answer-question input[name='questionkey']").val();
				var sessionkey = $("#dialog-answer-question input[name='sessionkey']").val();
				var answer = $("#dialog-answer-question input[name='answer']").val();
				
				$.loading(true, {align: 'center'});
				$.getJSON('/quizzer/endquestion', {questionkey: questionkey, sessionkey: sessionkey, answer: answer, duration: timercount}, function (data) {
					$.loading(false);
					if (data['result'] == 'wrong') {
						$("#result-message").text("Incorrect Answer!");
						$("#dialog-answer-result").dialog("open");
					}
					else {
						$("#result-message").text("Correct Answer!");
						$("#dialog-answer-result").dialog("open");
					}
				});
			},
			'Cancel': function () {
				stoptimer();
				$(this).dialog("close");
			}
		}
	});
	
	$("#dialog-quizzer-request").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
				var category = $("#dialog-quizzer-request select[name='category']").val();
				$.loading(true, {align: 'center'});
				$.getJSON('/quizzer/requestquestions', {category: category}, function (data) {
					$.loading(false);
					LoadQuestions(false);
				});
			},
			'Cancel': function () {
				$(this).dialog("close");
			}
		}
	});
	
	var ViewQuestionDetails = function (key) {
		$("#dialog-question-details input[name='key']").val(key);
		$.loading(true, {align: 'center'});
		$("#answerhistory").load('/quizzer/answerstable', {questionkey: key}, function () {
			$.loading(false);
			$("#dialog-question-details").dialog("open");
		});
	}
	
	var LoadQuestions = function (usecursor) {
		var cursorval = '';
		var prevcursors = '';
		
		var cat = $("input[name='currentcategory']").attr("value");
		var filterval = $("input[name='currentfilter']").val();
		
		if (usecursor) {
			cursorval = $("input[name='listcursor']").val();
			prevcursors = $("input[name='prevcursors']").val();
		}
		
		$.loading(true, {align: 'center'});
		$("#list").load('/quizzer/list', {category: cat, 'cursor': cursorval, prevcursors: prevcursors, filterval: filterval}, function () {
			$.loading(false);
			$("#list tbody tr").click( function () {
				var key = $(this).attr('title');
				
				ViewQuestionDetails(key);
			});
			$("#nextpage").click( function (event) {
				LoadQuestions(true);
				event.preventDefault();
			});
			
			$("#previouspage").click( function (event) {
				LoadPreviousQuestions();
				event.preventDefault();
			});
		});
	};
	
	var LoadPreviousQuestions = function () {		
		var prevcursors = $("input[name='prevcursors']").val();
		var category = $("input[name='currentcategory']").attr("value");
		
		$.loading(true, {align: 'center'});
		$("#list").load('/quizzer/prevlist', {category: category, prevcursors: prevcursors}, function () {
			$.loading(false);
			$("#list tbody tr").click( function () {
				var key = $(this).attr('title');
				
				ViewQuestionDetails(key);
			});
			$("#nextpage").click( function (event) {
				LoadQuestions(true);
				event.preventDefault();
			});
			
			$("#previouspage").click( function (event) {
				LoadPreviousQuestions();
				event.preventDefault();
			});
		});
	}
	
	$("#categoryselector li").click(function() {
  		$(this).addClass("selected").siblings().removeClass("selected");
  		var category = $(this).attr("value");
  		$("input[name='currentcategory']").val(category);
  		LoadQuestions();
	});
	
	//$("input[name='answeredfilter']").val('all');
	$("#answeredfilter input[type='radio']").change( function () {
		var filterval = $(this).val();
		
		$("input[name='currentfilter']").val(filterval);
		
		LoadQuestions(false);
	});
	
	$("input[name='request']").click( function () {
		$("#dialog-quizzer-request").dialog("open");
	});
	
	LoadQuestions(false);
	
});