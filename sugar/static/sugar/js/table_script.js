function onBodyLoad() {
    document.getElementById('submit').click();
}

function getTableRows(url) {
    var request = createAjaxRequest({
        url: url,
        onSuccess: renderTable,
        onFailure: function () { alert('Failure!'); },
    });
    if (!request) {
        return;
    }

    request.send(
        getFormData('list_view_form').join('&'),
    );
}

function renderTable(request) {
    var response = JSON.parse(request.responseText);
    var listViewTableDiv = document.getElementById(
        'list_view_table_div',
    );
    listViewTableDiv.innerText = '';

    var fisrtShown = response['first_shown'];
    var lastShown = response['last_shown'];
    var totalRowsCount = response['total_rows_count'];

    var table = document.createElement('table');
    table.border = 1;
    table.cellSpacing = 0;
    listViewTableDiv.append(table);

    var tableCaptionText = `Показаны записи с ${fisrtShown} по ${lastShown} из ${totalRowsCount}`;
    var tableCaption = document.createElement('caption');
    tableCaption.append(
        document.createTextNode(tableCaptionText),
    );
    table.append(tableCaption);

    var topRow = document.createElement('tr');
    table.append(topRow);

    for (let column of response.columns) {
        let header = document.createElement('th');
        header.append(
            document.createTextNode(column['header']),
        );
        topRow.append(header);
    }

    for (let row of response.rows) {
        let tableRow = document.createElement('tr');
        table.append(tableRow);
        for (let column of response.columns) {
            let cell = document.createElement('td');
            let data = row[column['data_index']];
            if (data == null) {
                data = '-';
            }
            cell.append(
                document.createTextNode(data),
            );
            tableRow.append(cell);
        }
    }
}
