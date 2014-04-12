$(document).ready(function() {
	$('#mainbody').delegate('#report_problem', 'submit', sendReport);
})

/* Envia el reporte con un POST */
function sendReport(event) {
	event.preventDefault();
	$('.report_alert').remove();
	disableButtons(['#report_problem button']);
	$.post($(this).attr('action'), $(this).serialize(), reportSaved);
}

/* Escribe el reporte recibido arriba */
function reportSaved(data) {
	if (data.errors) {
		for (error in data.errors)
			alertBefore(data.errors[error], '#group_'+error, 'report_alert', 'danger', '#report_problem');
	} else if (data.ok) {
		$('#id_url').val('');
		$('#id_ask').val('');
		data['newer'] = true;
		data['reports'] = data.report;
		reportsReceived(data);
	}
	enableButtons(['#report_problem button']);
}

/* Pide mas reportes, si newer es True pide mas recientes y si es False anteriores */
function askReports(idreport, newer) {
	disableButtons(['#ask_newer', '#ask_older']);
	$.getJSON('/more/reports/' + idreport + '/' + newer, reportsReceived);
}

/* Coloca los reportes recibidos arriba o abajo de la lista de reportes */
function reportsReceived(data) {
	if (data.idreport == 0) {
		if (!data.newer) {
			$('#ask_older').replaceWith('<div class="btn btn-primary ' +
							'btn-sm btn-block disabled">No hay m&aacute;s reportes</div>')
		}
	} else {
		if (data.newer) {
			$('#reports_list > li:first').before(data.reports);
			$('#ask_newer').attr('onClick', 
						'askReports(' + data.idreport + ', true);return false;');
		} else {
			$('#reports_list > li:last').after(data.reports);
			$('#ask_older').attr('onClick', 
						'askReports(' + data.idreport + ', false);return false;');
		}
	}
	enableButtons(['#ask_newer', '#ask_older']);
}

