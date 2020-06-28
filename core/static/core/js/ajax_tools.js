function createAjaxRequest(kwargs) {
    var url = kwargs['url'];
    if (!url) {
        throw new Error(
            'URL is not provided!',  // message
        );
    }

    var request = null;
    if (window.XMLHttpRequest) {
        request = new XMLHttpRequest();
    }
    if (!request) {
        throw new Error(
            'Can\'t create instance of XMLHttpRequest!',  // message
        );
    }

    request.open(
        'post',  // method
        url,  // url
        true,  // async
    );

    request.setRequestHeader(
        'Content-Type',  // name
        'application/x-www-form-urlencoded; charset=utf-8',  // value
    );

    var onRequestReadyStateChange = function (event) {
        var request = event.currentTarget;
        if (request.readyState == request.DONE) {
            if (request.status == STATUS_OK) {
                if (!!kwargs['onSuccess']) {
                    kwargs['onSuccess'](request);
                }
            } else {
                if (!!kwargs['onFailure']){
                    kwargs['onFailure'](request);
                }
            }
        } else {
            if (!!kwargs['onNotReady']) {
                kwargs['onNotReady'](request);
            }
        }
    }
    request.onreadystatechange = onRequestReadyStateChange;

    return request;
}

function getFormData(formId) {
    var form = document.getElementById(
        formId,
    );
    var formData = new FormData(form);
    var formParams = [];
    for (let [key, value] of formData.entries()) {
        formParams.push(`${key}=${value}`);
    }

    return formParams;
}