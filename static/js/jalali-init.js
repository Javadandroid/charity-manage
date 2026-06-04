/**
 * راه‌اندازی دیت‌پیکر شمسی (جلالی) برای فرم‌های پروژه
 */
$(document).ready(function() {
    // اطمینان از لود شدن کتابخانه
    if (typeof $.fn.persianDatepicker === 'undefined') {
        console.error('کتابخانه persian-datepicker لود نشده است!');
        return;
    }
    
    // فعال‌سازی دیت‌پیکر برای تمام ورودی‌های تاریخ
    $('.persian-datepicker, .jalali-datepicker, input[name="start_date"], input[name="end_date"]').each(function() {
        try {
            $(this).persianDatepicker({
                autoClose: true,
                format: 'YYYY-MM-DD',
                initialValue: false,
                onSelect: function(unixDate) {
                    var pd = new persianDate(unixDate);
                    // تبدیل به تاریخ میلادی
                    var date = pd.toCalendar('gregorian').format('YYYY-MM-DD');
                    console.log('تاریخ میلادی انتخاب شده:', date);
                    $(this.model.inputElement).val(date);
                }
            });
            console.log('دیت‌پیکر شمسی برای المان فعال شد:', this);
        } catch (e) {
            console.error('خطا در راه‌اندازی دیت‌پیکر:', e);
        }
    });
    
    console.log('راه‌اندازی دیت‌پیکر شمسی انجام شد.');
});
