$(document).ready(function () {
    const apiUrl = '';

    var currentYear = new Date().getFullYear();

    for (var i = currentYear; i >= currentYear - 100; i--) {
        $("#year").append(`<option value='${i}' data-value="${i - 1911}">民國${i - 1911}</option>`);
    }
    for (var i = 1; i <= 12; i++) {
        $("#month").append(`<option value='${i < 10 ? "0" + i : i}'>${i}</option>`);
    }
    $("#month, #year").change(function () {
        UpdateDays();
    });
    UpdateDays();

    let cropperInstances = {};
    let $cropperModal = $('#cropperModal');

    $('#UploadBackImage').on('change', function () {
        openCropper(this, "BackImagePreview", "imageToCrop");
    });

    $('#UploadFrontImage').on('change', function () {
        openCropper(this, "FrontImagePreview", "imageToCrop");
    });

    $('#Close').on('click', function () {
        $cropperModal.css('display', 'none');
    });

    $('#cropperModal').on('click', function (event) {
        if ($(event.target).hasClass('overlay')) {
            $cropperModal.css('display', 'none');
        }
    });

    $('.searchBtnWrap button').on('click', function (e) {
        e.preventDefault();

        let identity = $('#identity').val();
        let name = $('#name').val();
        let year = $("#year").find("option:selected").data("value") < 100 ? `0${$("#year").find("option:selected").data("value")}` : $("#year").find("option:selected").data("value");
        let month = $('#month').val();
        let day = $('#day').val();

        if (identity == '' || !ValidateIdNumber(identity)) {
            Swal.fire({
                position: "center",
                icon: "error",
                title: "請輸入身分證字號",
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }
        if (name.trim() == '') {
            Swal.fire({
                position: "center",
                icon: "error",
                title: "請輸入姓名",
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }
        if (year == '' || (month == '' || month > 12 || month < 1) || (day == '' || day > 31 || day < 1)) {
            Swal.fire({
                position: "center",
                icon: "error",
                title: "請輸入生日",
                showConfirmButton: false,
                timer: 1500
            });
            return;
        }

        $.ajax({
            url: `${apiUrl}/api/upload`,
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                name: name,
                birthday: `${year}-${month}-${day}`,
                identity_id: identity,
            }),
            success: function (data) {
                if (data.status) {
                    Swal.fire({
                        position: "center",
                        icon: "success",
                        title: "建立成功",
                        showConfirmButton: false,
                        timer: 1500
                    });
                    setTimeout(function () {
                        location.href = 'records.html';
                    }, 200)
                }
            },
            error: function (data, status, error) {
                console.error('Error: ' + status, error);
                Swal.fire({
                    position: "center",
                    icon: "error",
                    title: data.responseJSON.message,
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        });
    });

    function openCropper(inputElement, previewId, imageContainerId) {
        const file = inputElement.files[0];
        let formData = new FormData();
        formData.append("file", file);
        if (file) {
            $cropperModal.css('display', 'flex');

            const $image = $('<img>');
            $image.attr('src', URL.createObjectURL(file));

            const $preview = $('#' + previewId);

            // 添加到 Cropper.js modal 中
            const $imageToCrop = $('#' + imageContainerId);
            $imageToCrop.empty();
            $imageToCrop.append($image);

            // 初始化 Cropper.js
            cropperInstances[previewId] = new Cropper($image[0], {
                viewMode: 0
            });

            // 點擊裁切
            $('#cropImage').on('click', function () {
                const croppedImage = cropperInstances[previewId].getCroppedCanvas().toDataURL();
                $('#' + previewId).css('background-image', 'url(' + croppedImage + ')');

                inputElement.value = '';
                $cropperModal.css('display', 'none');
                $preview.find('b').hide();

                ShowLoading();
                $.ajax({
                    url: `${apiUrl}/api/ocr`,
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function (res) {
                        if (res.status) {
                            const { id, name, birthday_y, birthday_m, birthday_d } = res.message.message;
                            $('#identity').val(id);
                            $('#name').val(name);
                            $('#year').val(+birthday_y + 1911);
                            $('#year').change();
                            $('#month').val(birthday_m);
                            $('#month').change();
                            $('#day').val(birthday_d);
                            HideLoading();
                            Swal.fire({
                                position: "center",
                                icon: "warning",
                                title: "請確認辨識內容是否正確再查詢",
                                showConfirmButton: false,
                                timer: 2000
                            });
                        }
                    },
                    error: function (error) {
                        console.error(error);
                    }
                });

                // cropperInstances[previewId].destroy();
            });
        }
    }

    // 台灣身份證字號格式為一個英文字母 + 9 個數字
    function ValidateIdNumber(idNumber) {
        var regex = /^[A-Z]\d{9}$/;

        return regex.test(idNumber);
    }

    function UpdateDays() {
        var selectedMonth = $("#month").val();
        var selectedYear = $("#year").val();
        var daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();

        $("#day").empty();

        for (var i = 1; i <= daysInMonth; i++) {
            $("#day").append(`<option value='${i < 10 ? "0" + i : i}'>${i}</option>`);
        }
    }

    function ShowLoading() {
        $('.loading-overlay').css('display', 'flex');
    }

    function HideLoading() {
        $('.loading-overlay').hide();
    }
});
