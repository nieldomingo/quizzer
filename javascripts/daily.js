$(document).ready(function() {
	
	//google.load("visualization", "1", {packages:["corechart", "table"]});
	
	var LoadPercentCorrect = function () {
		var dateval = $("select[name='day']").val();
		var quizzer = $("select[name='quizzer']").val()
		
		d = {};
		d['day'] = dateval;
		
		if (quizzer && quizzer != 'all') {
			d['quizzer'] = quizzer;
		}
		
		$.post('/trainer/daily/percentcorrect',
			d,
			function (data) {
				var piedata = new google.visualization.DataTable(data);
				
				var chart = new google.visualization.PieChart($("#percentcorrect")[0]);
				//chart.draw(piedata, {width: 450, height: 300, title: 'Percent Correct'});
				chart.draw(piedata, {title: 'Correct Answers'});
				
			}, 'json');
	};
	
	var LoadPercentCategory = function () {
		var dateval = $("select[name='day']").val();
		var quizzer = $("select[name='quizzer']").val()
		
		d = {};
		d['day'] = dateval;
		
		if (quizzer && quizzer != 'all') {
			d['quizzer'] = quizzer;
		}
		
		$.post('/trainer/daily/percentcategory',
			d,
			function (data) {
				var piedata = new google.visualization.DataTable(data);
				
				var chart = new google.visualization.PieChart($("#percentcategory")[0]);
				//chart.draw(piedata, {width: 450, height: 300, title: 'Percent Correct'});
				chart.draw(piedata, {title: 'Questions Answered by Category'});
				
			}, 'json');
	};
	
	var LoadAnswerbyCategory = function () {
		var dateval = $("select[name='day']").val();
		var quizzer = $("select[name='quizzer']").val()
		
		d = {};
		d['day'] = dateval;
		
		if (quizzer && quizzer != 'all') {
			d['quizzer'] = quizzer;
		}
		
		$.post('/trainer/daily/answerbycategory',
			d,
			function (data) {
				var piedata = new google.visualization.DataTable(data);
				
				var chart = new google.visualization.BarChart($("#answerbycategory")[0]);
				//chart.draw(piedata, {width: 450, height: 300, title: 'Percent Correct'});
				chart.draw(piedata, {title: 'Questions Answered by Category', vAxis: {title: 'Categories'}});
				
			}, 'json');
	};
	
	var LoadSessionList = function () {
		var dateval = $("select[name='day']").val();
		var quizzer = $("select[name='quizzer']").val()
		
		d = {};
		d['day'] = dateval;
		
		if (quizzer && quizzer != 'all') {
			d['quizzer'] = quizzer;
		}
		
		$.post('/trainer/daily/sessionlist',
			d,
			function (data) {
				var tabdata = new google.visualization.DataTable(data);
				var view = new google.visualization.DataView(tabdata);
				view.setColumns([1, 2, 3, 4, 5]);
				
				var chart = new google.visualization.Table($("#answersessions")[0]);
				//chart.draw(piedata, {width: 450, height: 300, title: 'Percent Correct'});
				chart.draw(view, {'page': 'enable', 'pageSize': 20});
				
			}, 'json');
	};
	
	var LoadQuizzerOptions = function () {
		var dateval = $("select[name='day']").val();
		
		$("select[name='quizzer']").load('/trainer/daily/quizzeroptions', {day: dateval});
	
	}
	
	$("select[name='day']").change(function () {
		LoadPercentCorrect();
		LoadPercentCategory();
		LoadAnswerbyCategory();
		LoadQuizzerOptions();
		
		$("#answersessions").hide();
	});
	
	$("select[name='quizzer']").change(function () {
		LoadPercentCorrect();
		LoadPercentCategory();
		LoadAnswerbyCategory();
		
		var quizzer = $("select[name='quizzer']").val();
		
		if (quizzer != 'all') {
			$("#answersessions").show();
			LoadSessionList();
		}
		else {
			$("#answersessions").hide();
		}
		
	});
	
	LoadPercentCorrect();
	LoadPercentCategory();
	LoadAnswerbyCategory();
	LoadQuizzerOptions();
	
	$("#answersessions").hide();
	
});