function onBodyLoad() {
    document.getElementById('refresh').click();
}

function getTableRows(url) {
    var form = document.getElementById('list_view_form');

    var request = createAjaxRequest({
        url: url,
        onSuccess: onSuccessGetTableRows,
        onFailure: function () { alert('Failure!'); },
    });
    if (!request) {
        return;
    }

    request.send(getFormData(form).join('&'));
}

function onSuccessGetTableRows(request) {
    var response = JSON.parse(request.responseText);

    updateForm(request, response);
    renderTable(request, response);
}

function updateForm(request, response) {
    var firstShown = response['first_shown'];
    var lastShown = response['last_shown'];
    var totalRowsCount = response['total_rows_count'];
    var totalPagesCount = response['total_pages_count'];
    var pageNumber = response['page_number'];

    var firstPageButton = document.getElementById('first_page');
    var prevPageButton = document.getElementById('prev_page');
    var nextPageButton = document.getElementById('next_page');
    var lastPageButton = document.getElementById('last_page');
    var pageInput = document.getElementById('id_page_number');

    pageInput.setAttribute(
        'max',
        totalPagesCount,
    );
    pageInput.value = pageNumber;

    if (firstShown == 1) {
        prevPageButton.setAttribute('disabled', 'disabled');
        firstPageButton.setAttribute('disabled', 'disabled');
    } else {
        prevPageButton.removeAttribute('disabled');
        firstPageButton.removeAttribute('disabled');
    }

    if (lastShown == totalRowsCount) {
        nextPageButton.setAttribute('disabled', 'disabled');
        lastPageButton.setAttribute('disabled', 'disabled');
    } else {
        nextPageButton.removeAttribute('disabled');
        lastPageButton.removeAttribute('disabled');
    }

}

function renderTable(request, response) {
    var listViewTableDiv = document.getElementById(
        'list_view_table_div',
    );
    listViewTableDiv.innerText = '';

    var firstShown = response['first_shown'];
    var lastShown = response['last_shown'];
    var totalRowsCount = response['total_rows_count'];

    var table = document.createElement('table');
    table.border = 1;
    table.cellSpacing = 0;
    listViewTableDiv.append(table);

    var tableCaptionText = `Показаны записи с ${firstShown} по ${lastShown} из ${totalRowsCount}`;
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

function _getPage(url, pageNumber) {
    var pageInput = document.getElementById('id_page_number');
    pageInput.value = pageNumber;
    getTableRows(url);
}

function _shiftPage(url, shift) {
    var pageInput = document.getElementById('id_page_number');
    var pageNumber = parseInt(pageInput.value) + shift;
    _getPage(url, pageNumber);
}

function getNextPage(url) {
    _shiftPage(url, 1);
}

function getPrevPage(url) {
    _shiftPage(url, -1);
}

function getFirstPage(url) {
    _getPage(url, 1);
}

function getLastPage(url) {
    _getPage(url, -1);
}
