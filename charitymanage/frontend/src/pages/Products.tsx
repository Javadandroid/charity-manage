import { useEffect, useState } from 'react';
import { useEventStore } from '../store/useEventStore';
import api from '../api';

export default function Products() {
  const { activeEvent } = useEventStore();
  const [products, setProducts] = useState<any[]>([]);

  useEffect(() => {
    if (activeEvent) {
      api.get(`/api/products/?event=${activeEvent.id}`)
         .then(res => setProducts(res.data))
         .catch(err => console.error(err));
    }
  }, [activeEvent]);

  if (!activeEvent) return <div className="p-10 text-center font-semibold text-gray-500">رویداد فعالی وجود ندارد.</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h1 className="text-3xl font-black text-gray-800 tracking-tight">مدیریت محصولات غرفه‌ها</h1>
        <button className="bg-blue-600 text-white px-5 py-2.5 rounded-xl shadow hover:bg-blue-700 transition font-medium flex items-center space-x-2 space-x-reverse">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          <span>افزودن محصول جدید</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">کد محصول</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">نام محصول</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">قیمت (تومان)</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">وضعیت موجودی</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {products.map(product => (
              <tr key={product.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500 bg-gray-50/50">{product.code}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-bold text-gray-900">{product.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-black text-green-700">
                  {product.price.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full ${product.is_available ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'}`}>
                    {product.is_available ? 'موجود است' : 'ناموجود'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900 ml-4 font-bold bg-indigo-50 px-3 py-1 rounded-md transition">ویرایش</button>
                  <button className="text-red-600 hover:text-red-900 font-bold bg-red-50 px-3 py-1 rounded-md transition">حذف</button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-gray-500 flex flex-col items-center">
                  <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                  <span>هیچ محصولی برای غرفه‌های این رویداد یافت نشد.</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
