import { useEffect, useState } from 'react';
import { useEventStore } from '../store/useEventStore';
import { useToastStore } from '../store/useToastStore';
import api from '../api';

export default function Invoices() {
  const { activeEvent } = useEventStore();
  const { addToast } = useToastStore();

  const [invoices, setInvoices] = useState<any[]>([]);
  const [booths, setBooths] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedBooth, setSelectedBooth] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [selectedProducts, setSelectedProducts] = useState<{product_id: number, quantity: number}[]>([]);

  // POS State
  const [isPosModalOpen, setIsPosModalOpen] = useState(false);
  const [posDevices, setPosDevices] = useState<any[]>([]);
  const [selectedPos, setSelectedPos] = useState('');
  const [currentInvoice, setCurrentInvoice] = useState<any>(null);
  const [paying, setPaying] = useState(false);

  useEffect(() => {
    if (activeEvent) {
      fetchInvoices();
      fetchBooths();
    }
  }, [activeEvent]);

  useEffect(() => {
    if (selectedBooth) {
      api.get(`/api/products/products/?booth=${selectedBooth}`).then(res => setProducts(res.data.results || res.data));
    } else {
      setProducts([]);
    }
  }, [selectedBooth]);

  const fetchInvoices = () => {
    api.get(`/api/invoices/invoices/?event=${activeEvent?.id}`)
       .then(res => setInvoices(res.data.results || res.data))
       .catch(err => console.error(err));
  };

  const fetchBooths = () => {
    api.get(`/api/booths/?event=${activeEvent?.id}`).then(res => setBooths(res.data.results || res.data));
  };

  const handleAddProduct = (productId: number) => {
    const existing = selectedProducts.find(p => p.product_id === productId);
    if (existing) {
      setSelectedProducts(selectedProducts.map(p => p.product_id === productId ? { ...p, quantity: p.quantity + 1 } : p));
    } else {
      setSelectedProducts([...selectedProducts, { product_id: productId, quantity: 1 }]);
    }
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooth || selectedProducts.length === 0) {
      addToast('لطفا یک غرفه و حداقل یک محصول انتخاب کنید.', 'error');
      return;
    }

    try {
      await api.post('/api/invoices/invoices/checkout/', {
        booth_id: selectedBooth,
        customer_name: customerName || 'مشتری عبوری',
        items: selectedProducts
      });
      addToast('فاکتور با موفقیت ثبت شد.', 'success');
      setIsModalOpen(false);
      fetchInvoices();
      setSelectedBooth('');
      setCustomerName('');
      setSelectedProducts([]);
    } catch (err) {
      addToast('خطا در ثبت فاکتور', 'error');
    }
  };

  const handleOpenPosModal = (invoice: any) => {
    setCurrentInvoice(invoice);
    api.get(`/api/booths/pos-devices/`)
       .then(res => {
          const boothPos = res.data.filter((p: any) => p.booth === invoice.booth);
          setPosDevices(boothPos);
          setIsPosModalOpen(true);
       });
  };

  const handlePay = async () => {
    if (!selectedPos || !currentInvoice) return;
    setPaying(true);
    try {
      await api.post(`/api/booths/pos-devices/${selectedPos}/send-payment/`, {
        amount: currentInvoice.total_amount,
        invoice_id: currentInvoice.id
      });
      addToast('پرداخت از طریق پوز با موفقیت انجام شد.', 'success');
      setIsPosModalOpen(false);
      fetchInvoices();
    } catch (err) {
      addToast('خطا در ارتباط با دستگاه پوز', 'error');
    } finally {
      setPaying(false);
    }
  };

  if (!activeEvent) return <div className="p-10 text-center font-semibold text-gray-500">رویداد فعالی وجود ندارد.</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h1 className="text-3xl font-black text-gray-800 tracking-tight">مدیریت فاکتورها</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-green-600 text-white px-5 py-2.5 rounded-xl shadow hover:bg-green-700 transition font-medium flex items-center space-x-2 space-x-reverse"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          <span>ثبت فاکتور جدید</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">شماره فاکتور</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">نام مشتری</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">مبلغ کل (تومان)</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">وضعیت پرداخت</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {invoices.map(inv => (
              <tr key={inv.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500 bg-gray-50/50">{inv.invoice_number}</td>
                <td className="px-6 py-4 whitespace-nowrap font-bold text-gray-900">{inv.customer_name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-black text-green-700">{Number(inv.total_amount).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full ${inv.is_paid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {inv.is_paid ? 'پرداخت شده' : 'در انتظار پرداخت'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {!inv.is_paid && (
                    <button
                      onClick={() => handleOpenPosModal(inv)}
                      className="text-blue-600 font-bold bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition"
                    >
                      پرداخت با کارتخوان
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {invoices.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">هیچ فاکتوری یافت نشد.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-center items-center p-4 backdrop-blur-sm transition-opacity">
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="p-6 border-b flex justify-between items-center bg-gray-50">
              <h2 className="text-xl font-bold text-gray-800">ثبت فاکتور جدید</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-500 hover:text-red-500 transition">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>

            <form onSubmit={handleCheckout} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">انتخاب غرفه</label>
                  <select
                    className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50"
                    value={selectedBooth}
                    onChange={(e) => setSelectedBooth(e.target.value)}
                    required
                  >
                    <option value="">-- انتخاب کنید --</option>
                    {booths.map(b => (
                      <option key={b.id} value={b.id}>{b.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">نام مشتری (اختیاری)</label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    placeholder="مشتری عبوری"
                  />
                </div>
              </div>

              {selectedBooth && (
                <div className="border border-gray-200 rounded-xl p-4 bg-blue-50/50">
                  <h3 className="font-bold mb-3 text-blue-800">محصولات غرفه</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {products.map(p => (
                      <div
                        key={p.id}
                        onClick={() => handleAddProduct(p.id)}
                        className="bg-white p-3 rounded-lg border border-gray-200 cursor-pointer hover:border-blue-500 hover:shadow-md transition text-center"
                      >
                        <div className="font-bold text-gray-800 mb-1">{p.name}</div>
                        <div className="text-sm text-green-600 font-mono">{Number(p.price).toLocaleString()} تومان</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedProducts.length > 0 && (
                <div className="border border-green-200 rounded-xl p-4 bg-green-50">
                  <h3 className="font-bold mb-3 text-green-800">سبد خرید</h3>
                  <ul className="space-y-2">
                    {selectedProducts.map((sp, idx) => {
                      const prod = products.find(p => p.id === sp.product_id);
                      return (
                        <li key={idx} className="flex justify-between items-center bg-white p-2 rounded shadow-sm">
                          <span className="font-medium text-gray-800">{prod?.name}</span>
                          <span className="bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">تعداد: {sp.quantity}</span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}

              <div className="flex justify-end space-x-3 space-x-reverse pt-4 border-t">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-6 py-2.5 bg-gray-200 text-gray-800 rounded-xl font-bold hover:bg-gray-300">لغو</button>
                <button type="submit" className="px-6 py-2.5 bg-green-600 text-white rounded-xl font-bold hover:bg-green-700 shadow-lg">ثبت و ایجاد فاکتور</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isPosModalOpen && currentInvoice && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-center items-center p-4 backdrop-blur-sm transition-opacity">
          <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
            <div className="p-6 border-b flex justify-between items-center bg-gray-50">
              <h2 className="text-xl font-bold text-gray-800">ارسال به کارتخوان</h2>
              <button onClick={() => setIsPosModalOpen(false)} className="text-gray-500 hover:text-red-500 transition">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div className="bg-blue-50 p-4 rounded-xl">
                <p className="text-sm text-gray-600 mb-1">مبلغ قابل پرداخت:</p>
                <p className="text-3xl font-black text-blue-700">{Number(currentInvoice.total_amount).toLocaleString()} تومان</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">انتخاب دستگاه پوز</label>
                {posDevices.length > 0 ? (
                  <select
                    className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50"
                    value={selectedPos}
                    onChange={(e) => setSelectedPos(e.target.value)}
                  >
                    <option value="">-- انتخاب کنید --</option>
                    {posDevices.map(p => (
                      <option key={p.id} value={p.id}>{p.name} - {p.bank}</option>
                    ))}
                  </select>
                ) : (
                  <p className="text-red-500 text-sm">هیچ دستگاه پوزی برای این غرفه ثبت نشده است.</p>
                )}
              </div>

              <div className="flex justify-end space-x-3 space-x-reverse pt-4 border-t">
                <button onClick={() => setIsPosModalOpen(false)} className="px-6 py-2.5 bg-gray-200 text-gray-800 rounded-xl font-bold hover:bg-gray-300">لغو</button>
                <button
                  onClick={handlePay}
                  disabled={paying || !selectedPos || posDevices.length === 0}
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 shadow-lg disabled:opacity-50"
                >
                  {paying ? 'در حال ارتباط...' : 'ارسال مبلغ به کارتخوان'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
