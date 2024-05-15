$(document).ready(function () {
    const apiUrl = '';

    let listData = [];
    let reason = '';

    let queryString = window.location.search;
    let queryParams = {};
    queryString.substr(1).split("&").forEach(function (pair) {
        let keyValue = pair.split("=");
        queryParams[keyValue[0]] = decodeURIComponent(keyValue[1] || "");
    });
    let page = queryParams.page;
    let type = queryParams.type;
    let id = queryParams.id;

    GetListData();

    $(document).on('click', '#CreateBlacklist', function () {
        $("#blacklistModal").modal("show");
    })

    $(document).on('click', '#SubmitBlacklist', function () {
        reason = $('#Reason').val();
        if (reason.trim() == '') {
            Swal.fire({
                position: "center",
                icon: "error",
                title: "請填寫原因",
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }
        Swal.fire({
            title: "確定建立黑名單？",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#cd7363",
            cancelButtonColor: "#535c48",
            confirmButtonText: "確定",
            cancelButtonText: "取消",
        }).then((result) => {
            if (result.isConfirmed) {
                CreateBlacklist(id)
            }
        });
    })

    $(document).on('click', '#BackToIndex', function () {
        location.href = 'index.html';
    })

    $(document).on('click', '#DeletePpl', function () {
        Swal.fire({
            title: "確定刪除？",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#cd7363",
            cancelButtonColor: "#535c48",
            confirmButtonText: "刪除",
            cancelButtonText: "取消",
        }).then((result) => {
            if (result.isConfirmed) {
                DeletePpl();
            }
        });
    })

    function GetListData() {
        $.ajax({
            url: `${apiUrl}/api/list?page=${page}${typeof (type) == 'undefined' ? '' : '&type=' + type}`,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                listData = data.message;
                SetData(id);
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status, error);
            }
        });
    }

    function SetData(dataId) {
        const matchingData = listData.find(item => item.id_ == dataId);
        if (matchingData) {
            $('.name').html(matchingData['姓名']);
            $('.identity').html(matchingData['身份字號']);
            $('.isBad').html(matchingData['是否黑名單'] ? '有' : '無');
            $('.data-row [data-title]').each(function () {
                const title = $(this).data('title');
                let detailValue;
                if (matchingData.detail_data != null) {
                    detailValue = matchingData.detail_data[title];
                    var regex = /https?:\/\/[^\s]+/g;
                    var matches = detailValue.match(regex);
                    if (matches) {
                        for (var i = 0; i < matches.length; i++) {
                            var link = matches[i];
                            var replacement = '<a href="' + link + '" target="_blank">' + link + '</a>';
                            detailValue = detailValue.replace(link, replacement);
                        }
                    }
                }
                detailValue = detailValue.replace(/\n/g, '<br>');
                $(this).html(detailValue);
                if (detailValue !== '查無資料') {
                    $(this).addClass('warning');
                }
            });
        }
    }

    function CreateBlacklist(id) {
        $.ajax({
            url: `${apiUrl}/api/people`,
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                id_: id,
                is_bad: 1,
                cus: reason
            }),
            success: function (data) {
                Swal.fire({
                    position: "center",
                    icon: "success",
                    title: "建立成功",
                    showConfirmButton: false,
                    timer: 1500
                });
                location.reload();
            },
            error: function (xhr, status, error) {
                console.error('Error: ' + status, error);
            }
        });
    }

    function DeletePpl() {
        $.ajax({
            url: `${apiUrl}/api/del`,
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({ id_: id }),
            success: function (data) {
                Swal.fire({
                    position: "center",
                    icon: "success",
                    title: data.message,
                    showConfirmButton: false,
                    timer: 1500
                });
                if (type == '1')
                    location.href = 'blackList.html';
                else
                    location.href = 'records.html';
            },
            error: function (xhr, status, error) {
                console.error("失敗:", status, error);
            }
        });
    }
});