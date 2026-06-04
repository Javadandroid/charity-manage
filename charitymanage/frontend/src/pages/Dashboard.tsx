import { useEffect, useState } from 'react';
import { useEventStore } from '../store/useEventStore';
import api from '../api';

export default function Dashboard() {
  const { activeEvent } = useEventStore();
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    if (activeEvent) {
      api.get('/api/reports/dashboard/')
         .then(res => setStats(res.data))
         .catch(err => console.error("Failed to load dashboard stats", err));
    }
  }, [activeEvent]);

  if (!activeEvent) {
    return (
      <div className="flex flex-col items-center justify-center p-16 bg-white rounded-2xl shadow-sm border border-gray-100 mt-10">
        <div className="bg-yellow-100 p-4 rounded-full mb-4">
          <svg className="w-12 h-12 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">ابتدا یک رویداد را فعال کنید</h2>
        <p className="text-gray-500">برای مشاهده آمار داشبورد، لطفاً از بخش رویدادها، یک رویداد را انتخاب یا ایجاد نمایید.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-3xl font-black text-gray-800 tracking-tight">داشبورد مدیریتی</h1>
          <p className="text-gray-500 mt-1">نمای کلی از رویداد فعال: <span className="font-bold text-indigo-600">{activeEvent.name}</span></p>
        </div>
      </div>

      {stats ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition">
            <div>
              <h3 className="text-gray-500 text-sm font-semibold mb-1">فروش کل (بدون همت عالی)</h3>
              <p className="text-3xl font-black text-green-600">{stats.total_sales?.toLocaleString() || 0} <span className="text-sm font-medium text-gray-500">تومان</span></p>
            </div>
            <div className="bg-green-100 p-3 rounded-xl text-green-600">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition">
            <div>
              <h3 className="text-gray-500 text-sm font-semibold mb-1">مجموع همت عالی</h3>
              <p className="text-3xl font-black text-blue-600">{stats.total_donations?.toLocaleString() || 0} <span className="text-sm font-medium text-gray-500">تومان</span></p>
            </div>
            <div className="bg-blue-100 p-3 rounded-xl text-blue-600">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md transition">
            <div>
              <h3 className="text-gray-500 text-sm font-semibold mb-1">تعداد فاکتورهای صادر شده</h3>
              <p className="text-3xl font-black text-indigo-600">{stats.invoice_count || 0}</p>
            </div>
            <div className="bg-indigo-100 p-3 rounded-xl text-indigo-600">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center p-12 text-gray-500">
          <svg className="animate-spin -ml-1 mr-3 h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          در حال دریافت اطلاعات داشبورد...
        </div>
      )}
    </div>
  );
}
