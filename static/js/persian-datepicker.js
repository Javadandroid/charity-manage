/**
 * persian-datepicker.js
 */

$(document).ready(function () {
    setTimeout(function() {
        try {
            function jalaliToGregorian(jy, jm, jd) {
                jy = parseInt(jy);
                jm = parseInt(jm);
                jd = parseInt(jd);
                
                var gy = (jy <= 979) ? 621 : 1600;
                jy -= (jy <= 979) ? 0 : 979;
                var days = (365 * jy) + ((parseInt(jy / 33)) * 8) + (parseInt(((jy % 33) + 3) / 4)) + 78 + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
                gy += 400 * (parseInt(days / 146097));
                days %= 146097;
                if (days > 36524) {
                    gy += 100 * (parseInt(--days / 36524));
                    days %= 36524;
                    if (days >= 365) days++;
                }
                gy += 4 * (parseInt(days / 1461));
                days %= 1461;
                if (days > 365) {
                    gy += parseInt((days - 1) / 365);
                    days = (days - 1) % 365;
                }
                var gd = days + 1;
                var sal_a = [0, 31, ((gy % 4 == 0 && gy % 100 != 0) || (gy % 400 == 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
                var gm;
                for (gm = 0; gm < 13 && gd > sal_a[gm]; gm++) gd -= sal_a[gm];
                if (gm > 12) gm = 12;
                
                return [gy, gm, gd];
            }
            
            function gregorianToJalali(gy, gm, gd) {
                gy = parseInt(gy);
                gm = parseInt(gm);
                gd = parseInt(gd);
                
                var g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
                var jy = (gy <= 1600) ? 0 : 979;
                gy -= (gy <= 1600) ? 621 : 1600;
                var gy2 = (gm > 2) ? (gy + 1) : gy;
                var days = (365 * gy) + (parseInt((gy2 + 3) / 4)) - (parseInt((gy2 + 99) / 100)) + (parseInt((gy2 + 399) / 400)) - 80 + gd + g_d_m[gm - 1];
                jy += 33 * (parseInt(days / 12053));
                days %= 12053;
                jy += 4 * (parseInt(days / 1461));
                days %= 1461;
                jy += parseInt((days - 1) / 365);
                if (days > 365) days = (days - 1) % 365;
                var jm = (days < 186) ? 1 + parseInt(days / 31) : 7 + parseInt((days - 186) / 30);
                var jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
                
                return [jy, jm, jd];
            }
            
            function formatDate(year, month, day) {
                if (month < 10) month = "0" + month;
                if (day < 10) day = "0" + day;
                return year + "-" + month + "-" + day;
            }
            
            function formatJalaliDate(year, month, day) {
                if (month < 10) month = "0" + month;
                if (day < 10) day = "0" + day;
                return year + "/" + month + "/" + day;
            }
            
            function toPersianDigits(n) {
                const farsiDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
                return n.toString().replace(/\d/g, x => farsiDigits[x]);
            }
            
            function convertExistingDates() {
                $('input[name="start_date"], input[name="end_date"]').each(function() {
                    var $input = $(this);
                    var value = $input.val();
                    
                    if (value && value.match(/^\d{4}-\d{2}-\d{2}$/)) {
                        var parts = value.split('-');
                        var gDate = [parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2])];
                        var jDate = gregorianToJalali(gDate[0], gDate[1], gDate[2]);
                        
                        var jDateStr = formatJalaliDate(jDate[0], jDate[1], jDate[2]);
                        
                        var $hiddenInput = $('<input>', {
                            type: 'hidden',
                            name: $input.attr('name') + '_hidden',
                            value: value
                        });
                        
                        $input.attr('name', $input.attr('name') + '_display');
                        $input.val(jDateStr);
                        
                        $input.after($hiddenInput);
                    }
                });
            }
            
            function setupFormSubmission() {
                $('form').on('submit', function(e) {
                    $('input[name$="_display"]').each(function() {
                        var $displayField = $(this);
                        var originalName = $displayField.attr('name').replace('_display', '');
                        var $hiddenField = $('input[name="' + originalName + '_hidden"]');
                        
                        if ($hiddenField.length) {
                            var $originalField = $('input[name="' + originalName + '"]');
                            if (!$originalField.length) {
                                $originalField = $('<input>', {
                                    type: 'hidden',
                                    name: originalName
                                });
                                $displayField.after($originalField);
                            }
                            
                            $originalField.val($hiddenField.val());
                        }
                    });
                    
                    var $startDateField = $('input[name="start_date"], input[name="start_date_display"]').first();
                    var $endDateField = $('input[name="end_date"], input[name="end_date_display"]').first();
                    
                    if ($startDateField.length && $endDateField.length) {
                        var startDateValue = '';
                        var endDateValue = '';
                        
                        var $startDateHidden = $('input[name="start_date_hidden"]');
                        var $endDateHidden = $('input[name="end_date_hidden"]');
                        
                        if ($startDateHidden.length && $endDateHidden.length) {
                            startDateValue = $startDateHidden.val();
                            endDateValue = $endDateHidden.val();
                        } else {
                            startDateValue = $startDateField.val();
                            endDateValue = $endDateField.val();
                        }
                        
                        if (startDateValue && endDateValue) {
                            var startDate = new Date(startDateValue);
                            var endDate = new Date(endDateValue);
                            
                            if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime())) {
                                if (endDate < startDate) {
                                    alert('تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.');
                                    
                                    $endDateField.addClass('is-invalid');
                                    
                                    // توقف ارسال فرم
                                    e.preventDefault();
                                    return false;
                                } else {
                                    // حذف کلاس خطا اگر قبلاً وجود داشته باشد
                                    $endDateField.removeClass('is-invalid');
                                }
                            }
                        }
                    }
                    
                    return true;
                });
            }
            
            // راه‌اندازی دیت‌پیکر برای فیلدهای تاریخ
            function setupDatepickers() {
                $(".persian-datepicker, input[name=start_date], input[name=end_date], input[name$='_display']").each(function() {
                    var $input = $(this);
                    var inputName = $input.attr('name');
                    var baseFieldName = inputName.replace('_display', '');
                    
                    $input.persianDatepicker({
                        autoClose: true,
                        initialValue: false,
                        persianDigit: true,
                        format: 'YYYY/MM/DD',
                        onSelect: function(unix) {
                            // دریافت تاریخ شمسی
                            var pd = new persianDate(unix);
                            var jYear = pd.year();
                            var jMonth = pd.month();
                            var jDay = pd.date();
                            
                            // نمایش تاریخ شمسی در فیلد اصلی
                            var jalaliDate = formatJalaliDate(jYear, jMonth, jDay);
                            $input.val(jalaliDate);

                            // تبدیل به میلادی برای فیلد مخفی
                            var gDate = jalaliToGregorian(jYear, jMonth, jDay);
                            var gregorianDate = formatDate(gDate[0], gDate[1], gDate[2]);

                            // پیدا کردن یا ساختن input hidden برای مقدار میلادی
                            var $hiddenField = $('input[name="' + baseFieldName + '_hidden"]');
                            if (!$hiddenField.length) {
                                $hiddenField = $('<input>', {
                                    type: 'hidden',
                                    name: baseFieldName + '_hidden',
                                    value: gregorianDate,
                                    class: 'date-hidden'
                                });
                                $input.after($hiddenField);
                            } else {
                                $hiddenField.val(gregorianDate);
                            }
                        }
                    });
                    
                    // بررسی اولیه مقدار فیلد
                    var initialValue = $input.val();
                    if (initialValue && initialValue.includes('/')) {
                        // مقدار اولیه به فرمت شمسی است، آن را به میلادی تبدیل می‌کنیم
                        var parts = initialValue.split('/');
                        if (parts.length === 3) {
                            // تبدیل به میلادی
                            var gDate = jalaliToGregorian(parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2]));
                            var gregorianDate = formatDate(gDate[0], gDate[1], gDate[2]);
                            
                            // پیدا کردن یا ایجاد فیلد مخفی
                            var $hiddenField = $('input[name="' + baseFieldName + '_hidden"]');
                            if (!$hiddenField.length) {
                                $hiddenField = $input.next('.date-hidden');
                            }
                            
                            if (!$hiddenField.length) {
                                $hiddenField = $('<input>', {
                                    type: 'hidden',
                                    name: baseFieldName + '_hidden',
                                    value: gregorianDate,
                                    class: 'date-hidden'
                                });
                                $input.after($hiddenField);
                            } else {
                                $hiddenField.val(gregorianDate);
                            }
                        }
                    }
                    
                });
            }
            
            // اجرای توابع اصلی
            convertExistingDates();
            setupDatepickers();
            setupFormSubmission();
        } catch (error) {
            console.error("خطا در راه‌اندازی دیت‌پیکر شمسی: ", error);
        }
    }, 1000);
});
