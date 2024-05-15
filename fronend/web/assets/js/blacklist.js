$(document).ready(function () {
    const apiUrl = '';

    let contentDiv = $('.content');
    let pageBtnDiv = $('.pageBtn');
    let listData = [];
    let currentPage = 1;

    GetListData(currentPage);

    $(document).on('click', '.data-row:not(.undone)', function (e) {
        const clickedElement = $(e.target);
        const dataId = $(this).closest('.data-row').data('id');

        if (!clickedElement.hasClass('delBtn') && !clickedElement.closest('.delBtn').length) {
            location.href = `detail.html?page=${currentPage}&type=1&id=${dataId}`;
        }
    })

    $(document).on('click', '#List .data-cell:last-child', function () {
        const dataId = $(this).closest('.data-row').data('id');
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
                DeletePpl(dataId, $(this).closest('.data-row'));
            }
        });
    })

    $(document).on('click', '.prevPage', function () {
        if (currentPage > 1) {
            currentPage -= 1;
            GetListData(currentPage);
        }
    })

    $(document).on('click', '.nextPage', function () {
        currentPage += 1;
        GetListData(currentPage);
    })

    function GetListData(page) {
        $.ajax({
            url: `${apiUrl}/api/list?page=${page}&type=1`,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                listData = data.message;

                if (listData.length > 0) {
                    contentDiv.empty();
                    listData.forEach((data, i) => {
                        const dataRowDiv =
                            $(`<div class="data-row ${i == 0 ? 'first' : ''} ${i == listData.length - 1 ? 'only' : ''} ${data["爬蟲狀態"] == '已完成' ? '' : 'undone'}" data-id=${data.id_}></div> `);

                        dataRowDiv.append(`<div class="data-cell">${data["姓名"]}</div>`);
                        dataRowDiv.append(`<div class="data-cell">${data["身份字號"]}</div>`);
                        dataRowDiv.append(`<div class="data-cell">${data["生日"]}</div>`);
                        dataRowDiv.append(`<div class="data-cell">${data["是否黑名單"] ? '是' : '否'}</div>`);
                        dataRowDiv.append(`<div class="data-cell">${data["爬蟲狀態"]}</div>`);
                        dataRowDiv.append(`<div class="data-cell">${data["黑名單原因"]}</div>`);
                        dataRowDiv.append(`<div class="data-cell delBtn"><div><i class="fa-solid fa-trash"></i></div></div>`);

                        contentDiv.append(dataRowDiv);
                    });
                } else {
                    Swal.fire({
                        position: "center",
                        icon: "error",
                        title: "無資料",
                        showConfirmButton: false,
                        timer: 1500
                    });
                    currentPage -= 1;
                }

                UpdatePageButtons();
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status, error);
            }
        });
    }

    function DeletePpl(id, $rowElement) {
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
                listData = listData.filter(item => item.id_ !== id);
                // 移除 closest(.data-row) 元素
                $rowElement.remove();
            },
            error: function (xhr, status, error) {
                console.error("失敗:", status, error);
            }
        });
    }

    function UpdatePageButtons() {
        $('.pageBtn').empty();

        if (currentPage > 1) {
            pageBtnDiv.append('<div class="prevPage"><button class="btn btn-secondary">上一頁</button></div>');
        }
        pageBtnDiv.append('<div class="nextPage"><button class="btn btn-secondary">下一頁</button></div>');
    }
})