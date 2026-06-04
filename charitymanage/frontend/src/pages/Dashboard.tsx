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
      <div className="text-center p-10 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-gray-700">ابتدا یک رویداد را فعال کنید</h2>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">داشبورد - {activeEvent.name}</h1>

      {stats ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-gray-500 text-sm font-semibold mb-2">فروش کل</h3>
            <p className="text-3xl font-bold text-green-600">{stats.total_sales?.toLocaleString() || 0} <span className="text-sm">تومان</span></p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-gray-500 text-sm font-semibold mb-2">همت عالی</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.total_donations?.toLocaleString() || 0} <span className="text-sm">تومان</span></p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-gray-500 text-sm font-semibold mb-2">تعداد فاکتورها</h3>
            <p className="text-3xl font-bold text-gray-800">{stats.invoice_count || 0}</p>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500">در حال بارگذاری اطلاعات...</div>
      )}
    </div>
  );
}
