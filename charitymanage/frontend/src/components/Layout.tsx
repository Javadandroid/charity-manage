import { useEffect } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useEventStore } from '../store/useEventStore';
import { useAuthStore } from '../store/useAuthStore';

export default function Layout() {
  const { activeEvent, fetchEvents } = useEventStore();
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans" dir="rtl">
      <nav className="bg-gradient-to-r from-blue-700 to-indigo-800 text-white p-4 shadow-lg sticky top-0 z-40">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex space-x-6 space-x-reverse items-center">
            <Link to="/" className="text-2xl font-black tracking-tight ml-4">مدیریت خیریه</Link>
            <Link to="/" className="hover:text-blue-200 transition">داشبورد</Link>
            <Link to="/events" className="hover:text-blue-200 transition">رویدادها</Link>
            <Link to="/booths" className="hover:text-blue-200 transition">غرفه‌ها</Link>
            <Link to="/products" className="hover:text-blue-200 transition">محصولات</Link>
            {user?.is_superuser && (
              <Link to="/users" className="hover:text-blue-200 transition">کاربران</Link>
            )}
            <Link to="/kiosk" target="_blank" className="hover:text-blue-200 transition font-bold text-yellow-300">کیوسک</Link>
          </div>
          <div className="flex items-center space-x-4 space-x-reverse">
            {activeEvent ? (
              <span className="bg-white/20 px-4 py-1.5 rounded-full text-sm font-medium backdrop-blur-sm border border-white/30">
                رویداد فعال: <span className="font-bold text-yellow-300">{activeEvent.name}</span>
              </span>
            ) : (
              <span className="bg-red-500/80 px-4 py-1.5 rounded-full text-sm font-medium border border-red-400">
                هیچ رویداد فعالی وجود ندارد
              </span>
            )}

            <div className="relative group ml-2">
              <button className="flex items-center space-x-2 space-x-reverse bg-blue-800/50 px-4 py-2 rounded border border-blue-600 hover:bg-blue-800 transition">
                <span>{user?.first_name || user?.username}</span>
              </button>
              <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-xl py-1 z-50 hidden group-hover:block border border-gray-100">
                <button
                  onClick={handleLogout}
                  className="block w-full text-right px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  خروج از حساب
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto p-4 mt-8 pb-12">
        <Outlet />
      </main>
    </div>
  );
}
