/*!
  	Javascripts for project 1
	Author: JGM
	Date: May 2020
  */

/* 
	SELECT RATING
*/
var $starRating = $('.starsBox i');
var setRatingStar = function() {
	return $starRating.each(function() {
		if (parseInt($starRating.siblings('input#user_rating').val()) >= parseInt($(this).data('rating'))) {
		  return $(this).addClass('checked');
		} else {
		  return $(this).removeClass('checked');
		}
	});
};

$starRating.on('click', function() {
	$starRating.siblings('input#user_rating').val($(this).data('rating'));
	return setRatingStar();
});


/* 
	CLEAR RATING
*/
var $starBox = $('.starsBox button#clear');
var clearRaiting = function() {
  	return $starRating.each(function() {
		return $(this).removeClass('checked');
	});
};	

$starBox.on ('click', function() {
  $('input#user_rating').val(0);
  return clearRaiting();
});

$(document).ready(function() {
    // console.log( "ready!" );
	setRatingStar();
});
