import { useEffect, useState } from 'react';
import api from '../api';
import { useToastStore } from '../store/useToastStore';

export default function Users() {
  const [users, setUsers] = useState<any[]>([]);
  const [groups, setGroups] = useState<any[]>([]);
  const { addToast } = useToastStore();

  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [selectedGroups, setSelectedGroups] = useState<number[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [userRes, groupRes] = await Promise.all([
        api.get('/api/users/'),
        api.get('/api/groups/')
      ]);
      setUsers(userRes.data.results || userRes.data);
      setGroups(groupRes.data.results || groupRes.data);
    } catch (e) {
      console.error(e);
      addToast('خطا در دریافت اطلاعات کاربران', 'error');
    }
  };

  const handleGroupToggle = (groupId: number) => {
    setSelectedGroups(prev =>
      prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
    );
  };

  const resetForm = () => {
    setIsEditing(false);
    setEditingId(null);
    setUsername('');
    setPassword('');
    setFirstName('');
    setLastName('');
    setSelectedGroups([]);
  };

  const handleEdit = (user: any) => {
    setIsEditing(true);
    setEditingId(user.id);
    setUsername(user.username);
    setFirstName(user.first_name);
    setLastName(user.last_name);
    setSelectedGroups(user.groups.map((g: any) => g.id));
    setPassword('');
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('آیا از حذف این کاربر مطمئن هستید؟')) return;
    try {
      await api.delete(`/api/users/${id}/`);
      addToast('کاربر با موفقیت حذف شد', 'success');
      fetchData();
    } catch (e) {
      addToast('خطا در حذف کاربر', 'error');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload: any = {
      username,
      first_name: firstName,
      last_name: lastName,
      group_ids: selectedGroups
    };
    if (password) payload.password = password;

    try {
      if (isEditing && editingId) {
        await api.put(`/api/users/${editingId}/`, payload);
        addToast('کاربر با موفقیت ویرایش شد', 'success');
      } else {
        await api.post('/api/users/', payload);
        addToast('کاربر با موفقیت ایجاد شد', 'success');
      }
      resetForm();
      fetchData();
    } catch (e) {
      addToast('خطا در ذخیره کاربر', 'error');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h1 className="text-3xl font-black text-gray-800 tracking-tight">مدیریت کاربران و دسترسی‌ها</h1>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-xl font-bold mb-6 flex items-center text-indigo-700">
          <svg className="w-6 h-6 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
          {isEditing ? 'ویرایش اطلاعات کاربر' : 'تعریف کاربر جدید'}
        </h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">نام کاربری</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} required className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50 text-left" dir="ltr" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">رمز عبور {isEditing && <span className="text-gray-400 font-normal text-xs">(در صورت عدم تغییر خالی بگذارید)</span>}</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required={!isEditing} className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50 text-left" dir="ltr" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">نام</label>
            <input type="text" value={firstName} onChange={e => setFirstName(e.target.value)} className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">نام خانوادگی</label>
            <input type="text" value={lastName} onChange={e => setLastName(e.target.value)} className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 bg-gray-50" />
          </div>
          <div className="md:col-span-2 bg-blue-50 p-4 rounded-xl border border-blue-100">
            <label className="block text-sm font-bold text-blue-800 mb-3">گروه‌های کاربری و سطوح دسترسی</label>
            <div className="flex flex-wrap gap-4">
              {groups.map(g => (
                <label key={g.id} className="flex items-center space-x-2 space-x-reverse bg-white px-4 py-2 rounded-lg border border-blue-200 cursor-pointer hover:bg-blue-100 transition">
                  <input type="checkbox" checked={selectedGroups.includes(g.id)} onChange={() => handleGroupToggle(g.id)} className="w-4 h-4 text-blue-600 rounded" />
                  <span className="font-medium text-gray-700">{g.name}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="md:col-span-2 flex space-x-4 space-x-reverse mt-2">
            <button type="submit" className="bg-blue-600 text-white font-bold px-8 py-3 rounded-xl shadow-md hover:bg-blue-700 transition">
              {isEditing ? 'ذخیره تغییرات کاربر' : 'ثبت کاربر جدید'}
            </button>
            {isEditing && <button type="button" onClick={resetForm} className="bg-gray-200 text-gray-700 font-bold px-8 py-3 rounded-xl hover:bg-gray-300 transition">انصراف و لغو ویرایش</button>}
          </div>
        </form>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">نام کاربری</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">نام و نام خانوادگی</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">گروه‌های دسترسی</th>
              <th className="px-6 py-4 text-right text-xs font-bold text-gray-500 uppercase">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {users.map(user => (
              <tr key={user.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 font-mono text-sm">{user.username}</td>
                <td className="px-6 py-4 font-bold text-gray-800">{user.first_name} {user.last_name}</td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-2">
                    {user.groups.length > 0 ? user.groups.map((g: any) => (
                      <span key={g.id} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-md font-semibold">{g.name}</span>
                    )) : <span className="text-gray-400 text-xs">بدون گروه</span>}
                  </div>
                </td>
                <td className="px-6 py-4 space-x-3 space-x-reverse font-bold text-sm">
                  <button onClick={() => handleEdit(user)} className="text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition">ویرایش</button>
                  <button onClick={() => handleDelete(user.id)} className="text-red-600 bg-red-50 px-3 py-1.5 rounded-lg hover:bg-red-100 transition">حذف</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
