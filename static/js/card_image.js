$(document).ready(function() {
    $('.product-image-thumbnail').click(function() {
        var newImageUrl = $(this).find('img').attr('src');
        $('.main-product-image').attr('src', newImageUrl);
    });
});