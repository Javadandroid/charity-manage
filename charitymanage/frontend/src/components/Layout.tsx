import { useEffect } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useEventStore } from '../store/useEventStore';

export default function Layout() {
  const { activeEvent, fetchEvents } = useEventStore();

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return (
    <div className="min-h-screen bg-gray-100 font-sans" dir="rtl">
      <nav className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex space-x-4 space-x-reverse items-center">
            <Link to="/" className="text-xl font-bold">داشبورد</Link>
            <Link to="/events" className="hover:text-blue-200">رویدادها</Link>
            <Link to="/booths" className="hover:text-blue-200">غرفه‌ها</Link>
            <Link to="/products" className="hover:text-blue-200">محصولات</Link>
            <Link to="/kiosk" target="_blank" className="hover:text-blue-200">کیوسک</Link>
          </div>
          <div>
            {activeEvent ? (
              <span className="bg-blue-500 px-3 py-1 rounded-full text-sm">
                رویداد فعال: {activeEvent.name}
              </span>
            ) : (
              <span className="bg-red-500 px-3 py-1 rounded-full text-sm">
                هیچ رویداد فعالی وجود ندارد
              </span>
            )}
          </div>
        </div>
      </nav>

      <main className="container mx-auto p-4 mt-6">
        <Outlet />
      </main>
    </div>
  );
}
