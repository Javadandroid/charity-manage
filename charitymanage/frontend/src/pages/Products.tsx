import { useEffect, useState, useRef } from 'react';
import { useEventStore } from '../store/useEventStore';
import { useToastStore } from '../store/useToastStore';
import api from '../api';

export default function Products() {
  const { activeEvent } = useEventStore();
  const { addToast } = useToastStore();

  const [products, setProducts] = useState<any[]>([]);
  const [booths, setBooths] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExcelModalOpen, setIsExcelModalOpen] = useState(false);
  const [selectedBoothId, setSelectedBoothId] = useState('');

  // Product Form State
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [price, setPrice] = useState(0);

  // File ref
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (activeEvent) {
      fetchProducts();
      fetchBooths();
    }
  }, [activeEvent]);

  const fetchProducts = () => {
    api.get(`/api/products/products/?event=${activeEvent?.id}`).then(res => setProducts(res.data.results || res.data));
  };
  const fetchBooths = () => {
    api.get(`/api/booths/?event=${activeEvent?.id}`).then(res => setBooths(res.data.results || res.data));
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBoothId) {
      addToast('لطفاً غرفه را انتخاب کنید', 'error');
      return;
    }
    try {
      await api.post('/api/products/products/', {
        name, code, price, booth: selectedBoothId
      });
      addToast('محصول جدید ثبت شد.', 'success');
      setIsModalOpen(false);
      setName(''); setCode(''); setPrice(0);
      fetchProducts();
    } catch (err) {
      addToast('خطا در ثبت محصول', 'error');
    }
  };

  const handleExcelUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBoothId || !fileInputRef.current?.files?.[0]) {
      addToast('لطفاً غرفه و فایل اکسل را انتخاب کنید.', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('booth_id', selectedBoothId);
    formData.append('file', fileInputRef.current.files[0]);

    try {
      const res = await api.post('/api/products/products/bulk-upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      addToast(res.data.message, 'success');
      setIsExcelModalOpen(false);
      fetchProducts();
    } catch (err) {
      addToast('خطا در آپلود اکسل', 'error');
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('آیا از حذف این محصول اطمینان دارید؟')) return;
    try {
      await api.delete(`/api/products/products/${id}/`);
      addToast('محصول با موفقیت حذف شد', 'success');
      fetchProducts();
    } catch (e) {
      addToast('خطا در حذف', 'error');
    }
  };

  if (!activeEvent) return <div className="p-10 text-center font-semibold text-gray-500">رویداد فعالی وجود ندارد.</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h1 className="text-3xl font-black text-gray-800 tracking-tight">مدیریت محصولات غرفه‌ها</h1>
        <div className="flex space-x-3 space-x-reverse">
          <button onClick={() => setIsExcelModalOpen(true)} className="bg-green-600 text-white px-5 py-2.5 rounded-xl shadow hover:bg-green-700 transition font-medium flex items-center space-x-2 space-x-reverse">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
            <span>ورود با اکسل</span>
          </button>
          <button onClick={() => setIsModalOpen(true)} className="bg-blue-600 text-white px-5 py-2.5 rounded-xl shadow hover:bg-blue-700 transition font-medium flex items-center space-x-2 space-x-reverse">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
            <span>افزودن محصول جدید</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">کد محصول</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">نام محصول</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">غرفه</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">قیمت (تومان)</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {products.map(product => (
              <tr key={product.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 font-mono text-sm">{product.code}</td>
                <td className="px-6 py-4 font-bold text-gray-900">{product.name}</td>
                <td className="px-6 py-4 text-sm text-gray-600">
                   {booths.find(b => b.id === product.booth)?.name || '-'}
                </td>
                <td className="px-6 py-4 font-black text-green-700">
                  {Number(product.price).toLocaleString()}
                </td>
                <td className="px-6 py-4 space-x-3 space-x-reverse font-bold text-sm">
                  <button onClick={() => handleDelete(product.id)} className="text-red-600 bg-red-50 px-3 py-1.5 rounded-lg hover:bg-red-100 transition">حذف</button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500">هیچ محصولی برای غرفه‌های این رویداد یافت نشد.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add Product Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-center items-center p-4 backdrop-blur-sm">
          <div className="bg-white p-6 rounded-2xl w-full max-w-md shadow-2xl">
            <h2 className="text-xl font-bold mb-4">افزودن محصول جدید</h2>
            <form onSubmit={handleAddProduct} className="space-y-4">
              <div>
                <label className="block text-sm mb-1">کد محصول</label>
                <input type="text" value={code} onChange={e => setCode(e.target.value)} required className="w-full border p-2 rounded" dir="ltr" />
              </div>
              <div>
                <label className="block text-sm mb-1">نام محصول</label>
                <input type="text" value={name} onChange={e => setName(e.target.value)} required className="w-full border p-2 rounded" />
              </div>
              <div>
                <label className="block text-sm mb-1">قیمت (تومان)</label>
                <input type="number" value={price} onChange={e => setPrice(Number(e.target.value))} required className="w-full border p-2 rounded" dir="ltr" />
              </div>
              <div>
                <label className="block text-sm mb-1">غرفه مربوطه</label>
                <select value={selectedBoothId} onChange={e => setSelectedBoothId(e.target.value)} required className="w-full border p-2 rounded">
                  <option value="">-- انتخاب --</option>
                  {booths.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
              <div className="flex justify-end space-x-3 space-x-reverse pt-4">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-gray-200 rounded">لغو</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">ثبت محصول</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Excel Upload Modal */}
      {isExcelModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex justify-center items-center p-4 backdrop-blur-sm">
          <div className="bg-white p-6 rounded-2xl w-full max-w-md shadow-2xl">
            <h2 className="text-xl font-bold mb-4">ورود دسته‌ای با اکسل</h2>
            <form onSubmit={handleExcelUpload} className="space-y-4">
              <div>
                <label className="block text-sm mb-1">انتخاب غرفه</label>
                <select value={selectedBoothId} onChange={e => setSelectedBoothId(e.target.value)} required className="w-full border p-2 rounded">
                  <option value="">-- انتخاب غرفه‌ای که محصولات به آن اضافه شوند --</option>
                  {booths.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm mb-1">فایل اکسل</label>
                <input type="file" accept=".xlsx,.xls" ref={fileInputRef} required className="w-full border p-2 rounded" />
                <p className="text-xs text-gray-500 mt-2">ستون‌ها باید به ترتیب: کد کالا، نام کالا، قیمت، شناسه واحد (اختیاری)، توضیحات باشند.</p>
              </div>
              <div className="flex justify-end space-x-3 space-x-reverse pt-4">
                <button type="button" onClick={() => setIsExcelModalOpen(false)} className="px-4 py-2 bg-gray-200 rounded">لغو</button>
                <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">آپلود و پردازش</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
