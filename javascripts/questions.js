$(document).ready(function() {
	
	$("input[name='add']").button();
	//$("input[name='searchgo']").button();
	
	$("#question-form-tab").tabs();
	
	$("#dialog-question-required-message").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
			}
		}
	});
	
	$("#dialog-question-invalid-answer-message").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
			}
		}
	});
	
	$("#dialog-question-not-saved-message").dialog({
		modal: true,
		autoOpen: false,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
			}
		}
	});
	
	$("#dialog-question-form" ).dialog({
		modal: true,
		autoOpen: false,
		width: 570,
		buttons: {
			'Save': function () {
				var category = $("#dialog-question-form select[name='category']").val();
				var qtype = $("#dialog-question-form select[name='type']").val();
				var question = $("#dialog-question-form textarea[name='question']").val();
				var answer = $("#dialog-question-form input[name='answer']").val();
				var key = $("#dialog-question-form input[name='key']").val();
				var diagram = $("#dialog-question-form input[name='diagram']").val();
				
				if (qtype == '1') {
					// check if there are empty fields
					if (!question || !answer) {
						$("#dialog-question-required-message").dialog("open");
						return;
					}
					
					// check if a valid numerical answer was provided
					if (answer.search(/(^-*\d+$)|(^-*\d+\.\d+$)/) == -1) {
						$("#dialog-question-invalid-answer-message").dialog("open");
						return;
					}
				}
				else if (qtype == '2') {
					var choice1 = $("#dialog-question-form input[name='choice1']").val();
					var choice2 = $("#dialog-question-form input[name='choice2']").val();
					var choice3 = $("#dialog-question-form input[name='choice3']").val();
					
					if (!question || !answer || !choice1 || !choice2 || !choice3) {
						$("#dialog-question-required-message").dialog("open");
						return;
					}
				}
								
				$.loading(true, {align: 'center'});
				
				if (key){
					if (qtype == '1') {
						$.post('/questions/save',
							{'category': category,
							'qtype': qtype,
							'question': question,
							'answer': answer,
							'key': key,
							'diagram': diagram},
							SaveQuestionResult, 'json');
					}
					else if (qtype == '2') {
						$.post('/questions/save',
							{'category': category,
							'qtype': qtype,
							'question': question,
							'answer': answer,
							'choice1': choice1,
							'choice2': choice2,
							'choice3': choice3,
							'key': key,
							'diagram': diagram},
							SaveQuestionResult, 'json');
					}
				}
				else {
					//$.post('/questions/save', {'category': category, 'qtype': qtype, 'question': question, 'answer': answer, 'diagram': diagram}, SaveQuestionResult, 'json');
					if (qtype == '1') {
						$.post('/questions/save',
							{'category': category,
							'qtype': qtype,
							'question': question,
							'answer': answer,
							'diagram': diagram},
							SaveQuestionResult, 'json');
					}
					else if (qtype == '2') {
						$.post('/questions/save',
							{'category': category,
							'qtype': qtype,
							'question': question,
							'answer': answer,
							'choice1': choice1,
							'choice2': choice2,
							'choice3': choice3,
							'diagram': diagram},
							SaveQuestionResult, 'json');
					}
				}
			},
			'Cancel': function () {
				$(this).dialog("close");
			}
		}
	});
	
	$("#dialog-question-view").dialog({
		modal: true,
		autoOpen: false,
		width: 570,
		buttons: {
			'Ok': function () {
				$(this).dialog("close");
			},
			'Edit': function () {
				$(this).dialog("close");
				$("#dialog-question-form").dialog("open");
			},
		}
	});
	
	$("#dialog-svg-edit").dialog({
		modal: true,
		autoOpen: false,
		width: 640,
		buttons: {
			'Ok': function () {
				//var s = window.frames['svg-edit'].svgCanvas.getSvgString();
				/*
				var s = window.frames[0].svgCanvas.getSvgString();
				$("#dialog-question-form input[name='diagram']").val(s);
				$("#form-diagram-view").html(s);
				$(this).dialog("close");
				*/
				
				window.svgCanvas.getSvgString()(function (data, error) {
					$("#dialog-question-form input[name='diagram']").val(data);
					$("#form-diagram-view").html(data);
					$("#dialog-svg-edit").dialog("close");
				});
			},
			'Cancel': function () {
				$(this).dialog("close");
			},
		}
	});
	
	var ViewQuestion = function (key) {
		$.loading(true, {align: 'center'});
		$.getJSON('/questions/detail', {'key': key}, function (data) {
			// fill in the values of the view question dialog
			$("#categoryvalue").text(data['categoryname']);
			$("#typevalue").text(data['typename']);
			//$("#questionvalue").text(data['question']);
			$("#questionvalue").html(Wiky.toHtml(data['question']));
			$("#answervalue").html(Wiky.toHtml(data['answer']));
			$("#diagram-view").html(data['diagram']);
			
			if (data.type == 2) {
				$("#otherchoicesview").show();
				$("#otherchoice1").html(Wiky.toHtml(data['choice1']));
				$("#otherchoice2").html(Wiky.toHtml(data['choice2']));
				$("#otherchoice3").html(Wiky.toHtml(data['choice3']));
			}
			else {
				$("#otherchoicesview").hide();
			}
			
			//AMprocessNode($("#questionvalue")[0]);
			// fill in the values of the edit question dialog
			
			$("#dialog-question-form").attr('title', 'Edit Question');
			$("#dialog-question-form select[name='category']").val(data['category']);
			$("#dialog-question-form select[name='type']").val(data['type']);
			$("#dialog-question-form textarea[name='question']").val(data['question']);
			$("#dialog-question-form input[name='answer']").val(data['answer']);
			$("#dialog-question-form input[name='diagram']").val(data['diagram']);
			$("#form-diagram-view").html(data['diagram']);
			$("#dialog-question-form input[name='key']").val(data['key']);
			
			if (data.type == 2) {
				$("#dialog-question-form input[name='choice1']").val(data['choice1']);
				$("#dialog-question-form input[name='choice2']").val(data['choice2']);
				$("#dialog-question-form input[name='choice3']").val(data['choice3']);
				var answer = [data['answer'], data['choice1'], data['choice2'], data['choice3']].join('\n\n')
				$("#answerspreview").html(Wiky.toHtml(answer));
				$("#multiple-choice-fields").show();
			}
			else {
				$("#dialog-question-form input[name='choice1']").val('');
				$("#dialog-question-form input[name='choice2']").val('');
				$("#dialog-question-form input[name='choice3']").val('');
				$("#answerspreview").html('');
				$("#multiple-choice-fields").hide();
			} 
			
			$("#questionpreview").html(Wiky.toHtml(data['question']));
			//AMprocessNode($("#questionpreview")[0]);
			
			$.loading(false);
			$("#question-form-tab").tabs("select", 0);
			$("#dialog-question-view").dialog("open");
		});
	};
	
	var LoadQuestions = function (category, usecursor, searchstring) {
		var cat = String(category)
		var cursorval = '';
		var prevcursors = '';
		
		if (usecursor) {
			cursorval = $("input[name='listcursor']").val();
			prevcursors = $("input[name='prevcursors']").val();
		}
		
		if (searchstring == undefined) {
			searchstring = '';
		}
		
		$.loading(true, {align: 'center'});
		$("#list").load('/questions/list', {category: cat, 'cursor': cursorval, searchstring: searchstring, prevcursors: prevcursors}, function () {
			$.loading(false);
			$("#list tbody tr").click( function () {
				var key = $(this).attr('title');
				
				ViewQuestion(key);
			});
			$("#nextpage").click( function (event) {
				var category = $("input[name='currentcategory']").val();
				var searchstring = $("input[name='search']").val();
				LoadQuestions(category, true, searchstring);
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
		var searchstring = $("input[name='search']").val();
		
		$.loading(true, {align: 'center'});
		$("#list").load('/questions/prevlist', {category: category, searchstring: searchstring, prevcursors: prevcursors}, function () {
			$.loading(false);
			$("#list tbody tr").click( function () {
				var key = $(this).attr('title');
				
				ViewQuestion(key);
			});
			$("#nextpage").click( function (event) {
				var category = $("input[name='currentcategory']").val();
				LoadQuestions(category, true);
				event.preventDefault();
			});
			
			$("#previouspage").click( function (event) {
				LoadPreviousQuestions();
				event.preventDefault();
			});
		});
	}
	
	var SaveQuestionResult = function (data) {
		$.loading(false);
		$("#dialog-question-form" ).dialog("close");
		if (data.result == 'not saved') {
			$("#dialog-question-not-saved-message").dialog("open");
		}
		else {
			var category = $("input[name='currentcategory']").val();
			LoadQuestions(category);
		}
	};
	
	$("#buttons input[name='add']").click( function () {
		$("#dialog-question-form").attr('title', 'Add Question');
		$("#dialog-question-form select[name='category']").val('1');
		$("#dialog-question-form select[name='type']").val('1');
		$("#dialog-question-form textarea[name='question']").val('');
		$("#dialog-question-form input[name='answer']").val('');
		$("#dialog-question-form input[name='diagram']").val('');
		$("#form-diagram-view").html('');
		$("#dialog-question-form input[name='key']").val('');
		$("#questionpreview").html('');
		
		$("#multiple-choice-fields").hide();
		$("#dialog-question-form input[name='choice1']").val('');
		$("#dialog-question-form input[name='choice2']").val('');
		$("#dialog-question-form input[name='choice3']").val('');
		$("#answerspreview").html('');
		
		$("#question-form-tab").tabs("select", 0);
		$("#dialog-question-form" ).dialog("open");
		
	});
	
	//$("#categoryselector").selectable();
	$("#categoryselector li").click(function() {
  		$(this).addClass("selected").siblings().removeClass("selected");
  		var category = $(this).attr("value");
  		$("input[name='currentcategory']").val(category);
  		$("input[name='search']").val('');
  		LoadQuestions(category);
	});
	
	$("input[name='search']").val('');
	$("input[name='searchgo']").click( function () {
		var searchstring = $("input[name='search']").val();
		if (searchstring) {
			var category = $("input[name='currentcategory']").attr("value");
			LoadQuestions(category, false, searchstring);
		}
	})
	
	$("input[name='updatepreview']").click( function () {
		var val = $("#dialog-question-form textarea[name='question']").val();
		//$("#questionpreview").text(val);
		$("#questionpreview").html(Wiky.toHtml(val));
		//AMprocessNode($("#questionpreview")[0]);
	});
	
	$("input[name='editdiagram']").click( function () {
		var s = $("#dialog-question-form input[name='diagram']").val();
		
		/*
		if (s) {
			$("iframe[name='svg-edit']").load(function () {
				//window.frames['svg-edit'].svgCanvas.setSvgString(s);
				window.frames[0].svgCanvas.setSvgString(s);
				setTimeout(function () {
					window.frames[0].svgCanvas.setSvgString(s);
				}, 1000);
			});
		}
		else {
			$("iframe[name='svg-edit']").load(function () {
				//window.frames['svg-edit'].svgCanvas.setSvgString(s);
				var initsvg = '\
								<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">\
								 <!-- Created with SVG-edit - http://svg-edit.googlecode.com/ -->\
								 <g>\
								  <title>Layer 1</title>\
								 </g>\
								</svg>\
								';
				window.frames[0].svgCanvas.setSvgString(initsvg);
			});
		}*/
		
		$("iframe[name='svg-edit']").load(function () {
			var s = $("#dialog-question-form input[name='diagram']").val();
			
			window.svgCanvas = new embedded_svg_edit($("iframe[name='svg-edit']")[0]);
			//$("iframe[name='svg-edit']").contents().find("#main_button").hide();
			if (s) {
				window.svgCanvas.setSvgString(s);
				setTimeout(function () {
					window.svgCanvas.setSvgString(s);
				}, 1000);
			}
			else {
				var initsvg = '\
								<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">\
								 <!-- Created with SVG-edit - http://svg-edit.googlecode.com/ -->\
								 <g>\
								  <title>Layer 1</title>\
								 </g>\
								</svg>\
								';
				window.svgCanvas.setSvgString(initsvg);
			}
		});
		
		$("#dialog-svg-edit").dialog("open");
	});
	
	$("#dialog-question-form select[name='type']").change( function () {
		var questiontype = $(this).val();
		if (questiontype == '2') {
			$("#multiple-choice-fields").show();
		}
		else {
			$("#multiple-choice-fields").hide();
		}
	});
	
	$("input[name=updateanswerpreview]").click( function () {
		var choices = [];
		choices.push($("#dialog-question-form input[name='answer']").val());
		choices.push($("#dialog-question-form input[name='choice1']").val());
		choices.push($("#dialog-question-form input[name='choice2']").val());
		choices.push($("#dialog-question-form input[name='choice3']").val());
		
		var answer = choices.join('\n\n');
		
		$("#answerspreview").html(Wiky.toHtml(answer));
		
	});
	
	LoadQuestions(0);
});