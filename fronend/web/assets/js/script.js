$(document).ready(function () {
    let timeout;

    $('#ToggleMenu, .closeNav').click(function () {
        ToggleMenu();
    });

    // 在用戶活動時重置計時器
    $(document).on('mousemove keydown touchstart', function () {
        ResetTimer();
    });

    function ToggleMenu() {
        var pagesMobile = $('.pages-mobile');

        if (!pagesMobile.hasClass('show')) {
            var overlay = $('<div class="overlay"></div>');
            $('body').append(overlay);
            overlay.click(CloseMobileNav);

            pagesMobile.addClass('show');
        } else {
            CloseMobileNav();
        }
    }

    function CloseMobileNav() {
        var pagesMobile = $('.pages-mobile');
        var overlay = $('.overlay');

        pagesMobile.removeClass('show');

        overlay.off('click', CloseMobileNav);
        overlay.remove();
    }

    function ResetTimer() {
        clearTimeout(timeout);
        timeout = setTimeout(Logout, 600000); // 10分鐘
    }

    function Logout() {
        // 執行登出操作，可能需要向後端發送登出請求
        console.log('User is logged out');
        // 這裡可以添加向後端發送登出請求的代碼
    }

});
