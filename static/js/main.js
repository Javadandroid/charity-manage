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
    
    // راه‌اندازی دیت‌پیکر شمسی
    // initPersianDatepicker();
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
    
    // عملکرد دکمه افزودن آیتم به فاکتور (آیدی دیگر)
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            addInvoiceItem();
        });
    }
    
    // محاسبه مبلغ نهایی فاکتور
    document.querySelectorAll('.price-input, .quantity-input').forEach(function(input) {
        input.addEventListener('change', function() {
            calculateInvoiceTotal();
        });
        input.addEventListener('input', function() {
            calculateInvoiceTotal();
        });
    });
    
    // برای فیلدهای تخفیف و همت عالی هم رویدادهای تغییر را اضافه می‌کنیم
    const discountInput = document.getElementById('id_discount_amount');
    if (discountInput) {
        discountInput.addEventListener('change', calculateInvoiceTotal);
        discountInput.addEventListener('input', calculateInvoiceTotal);
    }
    
    const donationInput = document.getElementById('id_donation_amount');
    if (donationInput) {
        donationInput.addEventListener('change', calculateInvoiceTotal);
        donationInput.addEventListener('input', calculateInvoiceTotal);
    }
    
    // اضافه کردن رویداد برای چک‌باکس همت عالی
    const hasDonationCheckbox = document.getElementById('has-donation');
    if (hasDonationCheckbox) {
        hasDonationCheckbox.addEventListener('change', function() {
            const donationInput = document.getElementById('id_donation_amount');
            if (donationInput) {
                if (this.checked) {
                    donationInput.removeAttribute('readonly');
                    donationInput.focus();
                } else {
                    donationInput.value = '0';
                    donationInput.setAttribute('readonly', 'readonly');
                    calculateInvoiceTotal();
                }
            }
        });
    }
}

/**
 * افزودن آیتم جدید به فاکتور
 */
function addInvoiceItem() {
    const container = document.getElementById('invoice-items-container');
    if (!container) return;
    
    // شماره ردیف جدید
    const itemCount = document.querySelectorAll('.item-row').length;
    const newIndex = itemCount + 1;
    
    // ایجاد عناصر ردیف جدید
    const row = document.createElement('div');
    row.className = 'row item-row mb-3';
    row.id = `item-row-${newIndex}`;
    
    // غرفه فعلی
    const boothId = document.getElementById('id_booth') ? document.getElementById('id_booth').value : '';
    
    // HTML ردیف جدید
    row.innerHTML = `
        <div class="col-md-4">
            <select name="items-${newIndex}-product" id="id_items-${newIndex}-product" class="form-control product-select" required>
                <option value="">محصول را انتخاب کنید</option>
            </select>
        </div>
        <div class="col-md-2">
            <input type="number" name="items-${newIndex}-quantity" id="id_items-${newIndex}-quantity" class="form-control quantity-input" value="1" min="1" required>
        </div>
        <div class="col-md-2">
            <input type="number" name="items-${newIndex}-price" id="id_items-${newIndex}-price" class="form-control price-input" value="0" min="0" required>
        </div>
        <div class="col-md-2">
            <div class="form-control-plaintext total-price text-end">0</div>
        </div>
        <div class="col-md-1">
            <div class="form-check form-switch">
                <input type="checkbox" name="items-${newIndex}-is_delivered" id="id_items-${newIndex}-is_delivered" class="form-check-input">
            </div>
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-outline-danger btn-sm remove-item" onclick="removeInvoiceItem(${newIndex})">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
    `;
    
    container.appendChild(row);
    
    // اگر Select2 فعال است، آن را برای محصول فعال کنید
    if (typeof $.fn.select2 !== 'undefined') {
        $(`#id_items-${newIndex}-product`).select2({
            width: '100%',
            language: 'fa',
            dir: 'rtl',
            ajax: {
                url: `/api/products/booth/${boothId}/`,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.results.map(function(product) {
                            return {
                                id: product.id,
                                text: `${product.name} (${product.price} تومان)`,
                                price: product.price
                            };
                        })
                    };
                },
                cache: true
            }
        });
        
        // وقتی محصول انتخاب شد، قیمت آن را در فیلد قیمت قرار دهید
        $(`#id_items-${newIndex}-product`).on('select2:select', function (e) {
            const data = e.params.data;
            if (data && data.price) {
                document.getElementById(`id_items-${newIndex}-price`).value = data.price;
                calculateInvoiceTotal();
            }
        });
    }
    
    // اضافه کردن رویدادهای تغییر برای محاسبه مجدد
    document.querySelectorAll(`#item-row-${newIndex} .price-input, #item-row-${newIndex} .quantity-input`).forEach(function(input) {
        input.addEventListener('change', calculateInvoiceTotal);
        input.addEventListener('input', calculateInvoiceTotal);
    });
    
    // بروزرسانی مقدار فیلد مدیریت فرم‌ست
    const totalForms = document.getElementById('id_items-TOTAL_FORMS');
    if (totalForms) {
        totalForms.value = newIndex;
    }
    
    // محاسبه مجدد جمع کل
    calculateInvoiceTotal();
}

/**
 * حذف یک آیتم از فاکتور
 */
function removeInvoiceItem(index) {
    const row = document.getElementById(`item-row-${index}`);
    if (row) {
        row.remove();
        calculateInvoiceTotal();
        
        // بروزرسانی تعداد فرم‌ها
        const items = document.querySelectorAll('.item-row');
        const totalForms = document.getElementById('id_items-TOTAL_FORMS');
        if (totalForms) {
            totalForms.value = items.length;
        }
    }
}

/**
 * محاسبه مبلغ نهایی فاکتور
 */
function calculateInvoiceTotal() {
    let subtotal = 0;
    
    // محاسبه جمع هر ردیف
    document.querySelectorAll('.item-row').forEach(function(row) {
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
                totalElement.textContent = new Intl.NumberFormat('fa-IR').format(total) + ' تومان';
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
    const totalElement = document.getElementById('invoice-total');
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

// تابع initPersianDatepicker اصلی در persian-datepicker.js قرار دارد
