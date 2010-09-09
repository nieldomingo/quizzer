function SaveQuestionResult(data) {
	if (data.result == 'saved') {
		alert("Question Saved");
	}
	else {
		alert("Question Not Saved");
	}
	$("#editquestion").hide();
	LoadQuestions();
	$("#questionslist").show();
}

function SaveQuestion() {
	var questiontype = $("#questionform select[name='questiontype']").val();
	var question = $("#questionform textarea[name='question']").val();
	var answer = $("#questionform input[name='answer']").val();
	var key = $("#questionform input[name='key']").val();
	
	if (!question) {
		alert("Missing question value");
		return;
	}
	
	if (!answer) {
		alert("Missing answer value");
		return;
	}
		
	if (questiontype == '1') {
		if (answer.search(/(^-*\d+$)|(^-*\d+\.\d+$)/) == -1) {
			alert("Invalid numerical value for answer");
			return;
		}
	}
	if (key)
		$.getJSON('/savequestion', {'questiontype': questiontype, 'question': question, 'answer': answer, 'key': key}, SaveQuestionResult)
	else
		$.getJSON('/savequestion', {'questiontype': questiontype, 'question': question, 'answer': answer}, SaveQuestionResult)
}

function InitializeQuestionForm() {
	var questiontype = $("#questionform select[name='questiontype']").val('1');
	var question = $("#questionform textarea[name='question']").val('');
	var answer = $("#questionform input[name='answer']").val('');
}

function DisplayQuestion() {
	$("#questionslist").hide();
	$("#questionview").show();
	$("#questionviewcontent").load("/questionview", {'key': $(this).attr('key')})
}

function LoadQuestions() {
	$("#questionslist").load("/getquestions", function() {
		$("#questionslist .questionrow").unbind('click');
		$("#questionslist .questionrow").click(DisplayQuestion);
		$("#questionslist .questionrow").mouseenter(function() {
			$(this).addClass('overquestionrow');
		});
		$("#questionslist .questionrow").mouseleave(function() {
			$(this).removeClass('overquestionrow');
		});
		$("#questionslist input[type='checkbox']").click(function (event) {
			event.stopPropagation();
		});
	});
}

$(document).ready(function() {
	
	$("#buttons input[name='addquestion']").click(function() {
		$("#questionslist").hide();
		$("#questionview").hide();
		$("#editquestioncontent").load("/editquestion", function () {
			$("#questionform input[name='cancel']").click(function() {
				$("#editquestion").hide();
				$("#questionslist").show();
			});
			$("#questionform input[name='save']").click(SaveQuestion);
		});
		$("#editquestion").show();
	});
	
	//$("#questionform input[name='cancel']").click(function() {
	//	$("#questionform").hide();
	//});
	
	//$("#questionform input[name='save']").click(SaveQuestion);
	
	$("#questionview").hide();
	LoadQuestions();
	
	$("input[name='closequestion']").click(function () {
		$("#questionview").hide();
		$("#questionslist").show();
	});
	
	$("input[name='editquestion']").click(function () {
		$("#questionview").hide();
		
		var key = $("#questionviewcontent input[name='questionkey']").val();
		
		$("#editquestioncontent").load("/editquestion", {'key': key}, function () {
			$("#questionform input[name='cancel']").click(function() {
				$("#editquestion").hide();
				$("#questionview").show();
			});
			$("#questionform input[name='save']").click(SaveQuestion);
		});
		$("#editquestion").show();
	});
	
});