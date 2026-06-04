/**
 * فایل جاوااسکریپت اصلی پروژه مدیریت رویدادهای خیریه
 */

document.addEventListener('DOMContentLoaded', function() {
    // فعال‌سازی تولتیپ‌ها
    initTooltips();
    
    // فعال‌سازی ماسک‌های ورودی
    initInputMasks();
    
    // اضافه کردن اعتبارسنجی فرم‌ها
    initFormValidation();
    
    // تایید حذف آیتم‌ها
    initDeleteConfirmation();
    
    // بهبود Select2 برای RTL
    initSelect2();
    
    // امکان اضافه کردن ردیف جدید به فرم فاکتورها
    initInvoiceForm();
    
    // تنظیم اعداد به فرمت فارسی
    initPersianNumbers();
});

/**
 * فعال‌سازی تولتیپ‌های بوت‌استرپ
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * فعال‌سازی ماسک‌های ورودی برای اعداد، تاریخ و...
 */
function initInputMasks() {
    // اعمال ماسک به شماره تلفن
    document.querySelectorAll('.phone-mask').forEach(function(input) {
        input.addEventListener('input', function(e) {
            var x = e.target.value.replace(/\D/g, '').match(/(\d{0,4})(\d{0,3})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : x[1] + '-' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    });
    
    // اعمال ماسک به مبالغ ریالی
    document.querySelectorAll('.money-mask').forEach(function(input) {
        input.addEventListener('input', function(e) {
            var value = e.target.value.replace(/[^\d]/g, '');
            e.target.value = new Intl.NumberFormat('fa-IR').format(value);
        });
    });
}

/**
 * اعتبارسنجی فرم‌ها
 */
function initFormValidation() {
    // اعتبارسنجی فرم‌ها قبل از ارسال
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * تایید حذف آیتم‌ها
 */
function initDeleteConfirmation() {
    document.querySelectorAll('.delete-confirm').forEach(function(element) {
        element.addEventListener('click', function(event) {
            if (!confirm('آیا از حذف این آیتم اطمینان دارید؟')) {
                event.preventDefault();
            }
        });
    });
}

/**
 * پیکربندی Select2 برای پشتیبانی از RTL
 */
function initSelect2() {
    if (typeof $.fn.select2 !== 'undefined') {
        // تنظیم پیش‌فرض select2 برای RTL
        $.fn.select2.defaults.set('dir', 'rtl');
        
        // اعمال select2 به همه select‌ها
        $('.select2').select2({
            width: '100%',
            language: 'fa',
            dir: 'rtl'
        });
    }
}

/**
 * افزودن امکانات فرم فاکتور
 */
function initInvoiceForm() {
    // عملکرد دکمه افزودن آیتم به فاکتور
    const addItemButton = document.getElementById('add-item');
    if (addItemButton) {
        addItemButton.addEventListener('click', function() {
            addInvoiceItem();
        });
    }
    
    // محاسبه مبلغ نهایی فاکتور
    document.querySelectorAll('.price-input, .quantity-input, #id_discount_amount, #id_donation_amount').forEach(function(input) {
        input.addEventListener('change', function() {
            calculateInvoiceTotal();
        });
    });
}

/**
 * محاسبه مبلغ نهایی فاکتور
 */
function calculateInvoiceTotal() {
    let subtotal = 0;
    
    // محاسبه جمع هر ردیف
    document.querySelectorAll('.item-row:visible').forEach(function(row) {
        const priceInput = row.querySelector('.price-input');
        const quantityInput = row.querySelector('.quantity-input');
        
        if (priceInput && quantityInput) {
            const price = parseFloat(priceInput.value) || 0;
            const quantity = parseFloat(quantityInput.value) || 0;
            const total = price * quantity;
            
            subtotal += total;
            
            // نمایش مبلغ ردیف
            const totalElement = row.querySelector('.total-price');
            if (totalElement) {
                totalElement.textContent = new Intl.NumberFormat('fa-IR').format(total);
            }
        }
    });
    
    // نمایش جمع کل
    const subtotalElement = document.getElementById('subtotal');
    if (subtotalElement) {
        subtotalElement.textContent = new Intl.NumberFormat('fa-IR').format(subtotal) + ' تومان';
    }
    
    // محاسبه تخفیف و همت عالی
    const discountInput = document.getElementById('id_discount_amount');
    const donationInput = document.getElementById('id_donation_amount');
    
    let discount = 0;
    if (discountInput) {
        discount = parseFloat(discountInput.value) || 0;
    }
    
    let donation = 0;
    if (donationInput) {
        donation = parseFloat(donationInput.value) || 0;
    }
    
    // نمایش تخفیف
    const discountElement = document.getElementById('discount');
    if (discountElement) {
        discountElement.textContent = new Intl.NumberFormat('fa-IR').format(discount) + ' تومان';
    }
    
    // نمایش همت عالی
    const donationElement = document.getElementById('donation');
    if (donationElement) {
        donationElement.textContent = new Intl.NumberFormat('fa-IR').format(donation) + ' تومان';
    }
    
    // محاسبه و نمایش مبلغ نهایی
    const total = subtotal - discount + donation;
    const totalElement = document.getElementById('total');
    if (totalElement) {
        totalElement.textContent = new Intl.NumberFormat('fa-IR').format(total) + ' تومان';
    }
}

/**
 * تبدیل اعداد انگلیسی به فارسی
 */
function initPersianNumbers() {
    document.querySelectorAll('.persian-number').forEach(function(element) {
        const number = element.textContent;
        element.textContent = number.replace(/\d/g, function(d) {
            return ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'][d];
        });
    });
}
