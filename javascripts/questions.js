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
								
				// check if there are empty fields
				if (!question || !answer) {
					$("#dialog-question-required-message").dialog("open");
					return;
				}
				
				// check if a valid numerical answer was provided
				if (qtype == '1') {
					if (answer.search(/(^-*\d+$)|(^-*\d+\.\d+$)/) == -1) {
						$("#dialog-question-invalid-answer-message").dialog("open");
						return;
					}
				}
								
				$.loading(true, {align: 'center'});
				
				if (key){
					//$.getJSON('/questions/save', {'category': category, 'qtype': qtype, 'question': question, 'answer': answer, 'key': key, 'diagram': diagram}, SaveQuestionResult);
					$.post('/questions/save', {'category': category, 'qtype': qtype, 'question': question, 'answer': answer, 'key': key, 'diagram': diagram}, SaveQuestionResult, 'json');
				}
				else {
					//$.getJSON('/questions/save', {'category': category, 'qtype': qtype, 'question': question, 'answer': answer, 'diagram': diagram}, SaveQuestionResult);
					$.post('/questions/save', {'category': category, 'qtype': qtype, 'question': question, 'answer': answer, 'diagram': diagram}, SaveQuestionResult, 'json');
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
				var s = window.frames[0].svgCanvas.getSvgString();
				$("#dialog-question-form input[name='diagram']").val(s);
				$("#form-diagram-view").html(s);
				$(this).dialog("close");
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
			$("#answervalue").text(data['answer']);
			$("#diagram-view").html(data['diagram']);
			
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
		
		if (s) {
			$("iframe[name='svg-edit']").load(function () {
				//window.frames['svg-edit'].svgCanvas.setSvgString(s);
				window.frames[0].svgCanvas.setSvgString(s);
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
		}
		$("#dialog-svg-edit").dialog("open");
	});
	
	LoadQuestions(0);
	
	//var svgCanvas = new embedded_svg_edit(window.frames['svg-edit']);
	var s = '\
			<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">\
			 <!-- Created with SVG-edit - http://svg-edit.googlecode.com/ -->\
			 <g>\
			  <title>Layer 1</title>\
			  <ellipse ry="61" rx="54" id="svg_1" cy="153" cx="147" stroke-width="5" stroke="#000000" fill="#FF0000"/>\
			 </g>\
			</svg>';
	//svgCanvas.setSvgString(s);
	//$("iframe[name='svg-edit']").load(function () {
	//	window.frames['svg-edit'].svgCanvas.setSvgString(s);
	//});
	
});