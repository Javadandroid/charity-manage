import { useEffect, useState } from 'react';
import { useEventStore } from '../store/useEventStore';
import api from '../api';

export default function Booths() {
  const { activeEvent } = useEventStore();
  const [booths, setBooths] = useState<any[]>([]);

  useEffect(() => {
    if (activeEvent) {
      api.get(`/api/booths/?event=${activeEvent.id}`)
         .then(res => setBooths(res.data))
         .catch(err => console.error(err));
    }
  }, [activeEvent]);

  if (!activeEvent) return <div className="p-10 text-center font-semibold text-gray-500">رویداد فعالی وجود ندارد.</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h1 className="text-3xl font-black text-gray-800 tracking-tight">مدیریت غرفه‌ها</h1>
        <button className="bg-blue-600 text-white px-5 py-2.5 rounded-xl shadow hover:bg-blue-700 transition font-medium flex items-center space-x-2 space-x-reverse">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          <span>افزودن غرفه جدید</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">نام غرفه</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">وضعیت</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">نمایش در کیوسک</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {booths.map(booth => (
              <tr key={booth.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-bold text-gray-900">{booth.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-3 py-1 inline-flex text-xs leading-5 font-bold rounded-full ${booth.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {booth.is_active ? 'فعال' : 'غیرفعال'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-medium">
                  {booth.show_in_kiosk ? (
                    <span className="text-blue-600 flex items-center space-x-1 space-x-reverse">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                      <span>بله</span>
                    </span>
                  ) : 'خیر'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900 ml-4 font-bold bg-indigo-50 px-3 py-1 rounded-md transition">ویرایش</button>
                  <button className="text-red-600 hover:text-red-900 font-bold bg-red-50 px-3 py-1 rounded-md transition">حذف</button>
                </td>
              </tr>
            ))}
            {booths.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-gray-500 flex flex-col items-center">
                  <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                  <span>هیچ غرفه‌ای برای این رویداد یافت نشد.</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
