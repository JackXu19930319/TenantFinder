$(document).ready(function () {
    const apiUrl = '';

    let currentPage = 1;
    let contentDiv = $('.content');

    GetListData(currentPage);

    $(document).on('click', '.updatePassword', function () {
        $("#UpdatePassword").modal("show");
    })

    $(document).on('click', '#CreateAccountBtn', function () {
        $("#CreateAccount").modal("show");
    })

    function GetListData(page) {
        $.ajax({
            url: `${apiUrl}/api/list?page=${page}`,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                listData = data.message;

                if (listData.length > 0) {
                    contentDiv.empty();
                    listData.forEach((data, i) => {
                        const dataRowDiv =
                            $(`<div class="data-row ${i == 0 ? 'first' : ''} ${i == listData.length - 1 ? 'only' : ''}" data-id=${data.id_}></div> `);

                        dataRowDiv.append(`<div class="data-cell">${data["姓名"]}</div>`);
                        dataRowDiv.append(`<div class="data-cell">${data["身份字號"]}</div>`);
                        dataRowDiv.append(`
                            <div class="data-cell">
                                <select class="form-control" name="">
                                    <option value="">主管</option>
                                    <option value="">管理者</option>
                                </select>
                            </div>`
                        );
                        dataRowDiv.append(`
                            <div class="data-cell controlBtn">
                                <button class="btn btn-secondary updatePassword">修改密碼</button>
                                <button class="btn btn-primary suspension">停權</button>
                            </div>`);

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
            },
            error: function (xhr, status, error) {
                console.error("Error: " + status, error);
            }
        });
    }
});