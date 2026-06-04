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

  if (!activeEvent) return <div className="p-10 text-center">رویداد فعالی وجود ندارد.</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">مدیریت غرفه‌ها</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700">افزودن غرفه جدید</button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">نام غرفه</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">وضعیت</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">نمایش در کیوسک</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {booths.map(booth => (
              <tr key={booth.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{booth.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${booth.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {booth.is_active ? 'فعال' : 'غیرفعال'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {booth.show_in_kiosk ? 'بله' : 'خیر'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900 ml-4">ویرایش</button>
                  <button className="text-red-600 hover:text-red-900">حذف</button>
                </td>
              </tr>
            ))}
            {booths.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-10 text-center text-gray-500">هیچ غرفه‌ای برای این رویداد یافت نشد.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
